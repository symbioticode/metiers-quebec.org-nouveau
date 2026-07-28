#!/usr/bin/env python3
"""
query_test.py — Query layer for Métiers Québec corpus

Loads chunks.jsonl + graph_communities.json into memory once.
Provides query(question, top_k=5) using cosine similarity on bge-small-en-v1.5 embeddings.

Usage:
  # Interactive mode
  nix-shell --run '.venv/bin/python scripts/query_test.py'

  # Run 10 test questions
  nix-shell --run '.venv/bin/python scripts/query_test.py --test'

Rules:
  - chunks.jsonl is loaded once into process memory (not LLM context)
  - Similarity computed in pure Python/numpy
  - Only printed output is read back, never the raw file
"""

import json
import sys
import time
import numpy as np
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
CHUNKS_PATH = BASE_DIR / "data" / "embeddings" / "chunks.jsonl"
GRAPH_PATH = BASE_DIR / "data" / "graph_communities.json"
MODEL_NAME = "BAAI/bge-small-en-v1.5"
SIMILARITY_THRESHOLD = 0.3


class CorpusIndex:
    """In-memory index of chunks with embeddings."""

    def __init__(self):
        self.chunks = []
        self.embeddings = None
        self.graph = {}
        self.model = None
        self._loaded = False

    def load(self):
        t0 = time.time()
        print("Loading chunks...")
        chunks = []
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        self.chunks = chunks

        # Build embedding matrix
        embs = [c["embedding"] for c in chunks]
        self.embeddings = np.array(embs, dtype=np.float32)
        # Normalize for cosine similarity via dot product
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings_normed = self.embeddings / np.clip(norms, 1e-10, None)

        # Load graph communities
        if GRAPH_PATH.exists():
            self.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

        # Load model
        print("Loading model...")
        from fastembed import TextEmbedding
        self.model = TextEmbedding(MODEL_NAME)

        elapsed = time.time() - t0
        mem_mb = self.embeddings.nbytes / (1024 * 1024)
        print(f"Index loaded in {elapsed:.1f}s ({len(chunks)} chunks, {mem_mb:.1f} MB embeddings)")
        self._loaded = True

    def query(self, question, top_k=5):
        """Query the corpus. Returns list of result dicts."""
        if not self._loaded:
            self.load()

        # Embed question
        q_emb = list(self.model.embed([question]))[0]
        q_vec = np.array(q_emb, dtype=np.float32)
        q_norm = q_vec / np.clip(np.linalg.norm(q_vec), 1e-10, None)

        # Cosine similarity via dot product
        scores = self.embeddings_normed @ q_norm

        # Top-k
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            chunk = self.chunks[idx]
            results.append({
                "score": score,
                "slug": chunk["slug"],
                "nom": chunk["nom"],
                "secteur": chunk["secteur"],
                "section": chunk["section_key_original"],
                "present_in_pipeline": chunk["present_in_pipeline"],
                "text_preview": chunk["text"][:200],
            })
        return results

    def get_graph_neighbors(self, slug, max_neighbors=3):
        """Get related professions from graph community."""
        if slug not in self.graph:
            return []
        entry = self.graph[slug]
        neighbors = entry.get("neighbors", [])
        # Filter to metier_ neighbors only
        metier_neighbors = [n for n in neighbors if n.startswith("metier_")]
        return metier_neighbors[:max_neighbors]


def format_answer(question, results, index):
    """Format a human-readable answer from query results."""
    lines = []
    lines.append(f"Question: {question}")
    lines.append("")

    if not results or results[0]["score"] < SIMILARITY_THRESHOLD:
        lines.append("Réponse: Absent du corpus source. Aucun chunk pertinent trouvé.")
        lines.append(f"(Meilleur score: {results[0]['score']:.3f}" if results else "(aucun résultat)")
        lines.append("")
        return "\n".join(lines)

    # Best result
    best = results[0]
    lines.append(f"Métier principal: {best['nom']} ({best['slug']})")
    lines.append(f"Secteur: {best['secteur']}")
    lines.append(f"Section: {best['section']}")
    lines.append(f"Présent dans le pipeline généré: {'Oui' if best['present_in_pipeline'] else 'Non — données source uniquement'}")
    lines.append(f"Score similarité: {best['score']:.3f}")
    lines.append(f"Aperçu: {best['text_preview']}...")
    lines.append("")

    # All top results
    lines.append("Top chunks:")
    for i, r in enumerate(results):
        pipeline_tag = "[pipeline]" if r["present_in_pipeline"] else "[source-only]"
        lines.append(f"  {i+1}. {r['slug']}::{r['section']} {pipeline_tag} (score={r['score']:.3f})")
    lines.append("")

    # Graph neighbors
    neighbors = index.get_graph_neighbors(best["slug"])
    if neighbors:
        neighbor_names = []
        for n in neighbors:
            # Extract readable name from graph
            n_entry = index.graph.get(n.replace("metier_", ""), {})
            n_name = n.replace("metier_", "")
            if n_entry:
                neighbor_names.append(n_name)
        if neighbor_names:
            lines.append(f"Métiers apparentés (même communauté): {', '.join(neighbor_names)}")

    return "\n".join(lines)


# 10 fixed test questions
TEST_QUESTIONS = [
    ("Quel est le salaire d'un infirmier ?", "infirmier", "Q1"),
    ("Quel est le salaire d'un administrateur ?", "administrateur", "Q2"),
    ("Quelles sont les qualités requises pour être administrateur ?", "administrateur", "Q3"),
    ("Formation requise pour devenir technicien en informatique", "tech_informatique", "Q4"),
    ("Statistiques de placement pour technologue en radiologie", "tech_radiodiagnostic", "Q5"),
    ("Quels métiers sont proches de géologue ?", "geologuel", "Q6"),
    ("Exigences d'admission pour physiothérapeute", "physiotherapeute", "Q7"),
    ("Quel est le salaire d'un astronaute", None, "Q8"),
    ("Quels métiers du secteur mines existent dans ce corpus ?", None, "Q9"),
    ("Quel est le salaire d'un infirmièr?", None, "Q10"),
]


def run_tests(index):
    """Run the 10 fixed test questions."""
    results_log = []
    t0 = time.time()

    for question, expected_slug, qid in TEST_QUESTIONS:
        print(f"\n{'='*60}")
        print(f"  {qid}: {question}")
        print(f"{'='*60}")
        results = index.query(question, top_k=5)
        answer = format_answer(question, results, index)
        print(answer)
        results_log.append({
            "qid": qid,
            "question": question,
            "expected_slug": expected_slug,
            "results": results,
            "answer": answer,
        })

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  Total test time: {elapsed:.1f}s ({elapsed/10:.1f}s/question)")
    print(f"{'='*60}")

    return results_log, elapsed


def interactive_mode(index):
    """Interactive query loop."""
    print("\nInteractive mode. Type your question and press Enter.")
    print("Type 'quit' to exit.\n")
    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() in ("quit", "exit", "q"):
            break
        results = index.query(question, top_k=5)
        print(format_answer(question, results, index))
        print()


def main():
    index = CorpusIndex()

    if "--test" in sys.argv:
        run_tests(index)
    else:
        interactive_mode(index)


if __name__ == "__main__":
    main()
