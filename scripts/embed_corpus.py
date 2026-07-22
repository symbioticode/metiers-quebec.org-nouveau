#!/usr/bin/env python3
"""
embed_corpus.py — Chunk + embed corpus_raw_v2 (batch mode, resume support)

Modèle: BAAI/bge-small-en-v1.5 (fastembed, 384-dim, ~33M params)
- Léger (pas de PyTorch), inference ONNX
- Fonctionne sur le français malgré l'entraînement anglais dominant

Sortie: data/embeddings/chunks.jsonl
Resume: reads existing chunks.jsonl, skips already-embedded slugs
"""

import json
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "corpus_raw_v2"
OUT_DIR = BASE_DIR / "data" / "embeddings"
COVERAGE_FILE = BASE_DIR / "data" / "coverage_report.json"

CHUNK_TARGET_WORDS = 400
CHUNK_MAX_WORDS = 600
EMBED_BATCH_SIZE = 64  # fastembed optimal batch size

MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_DIM = 384


def load_coverage_map():
    if not COVERAGE_FILE.exists():
        return {}
    with open(COVERAGE_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)
    pipeline_map = {}
    for concept, data in report.get("concepts", {}).items():
        for detail in data.get("details", []):
            slug = detail["slug"]
            if slug not in pipeline_map:
                pipeline_map[slug] = {}
            pipeline_map[slug][concept] = detail.get("present_in_pipeline", False)
    return pipeline_map


def chunk_text(text, target_words=CHUNK_TARGET_WORDS, max_words=CHUNK_MAX_WORDS):
    words = text.split()
    if len(words) <= max_words:
        return [text] if text.strip() else []
    chunks = []
    current = []
    for word in words:
        current.append(word)
        if len(current) >= target_words and word.endswith((".", "!", "?", ";", ":")):
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def _key_to_concept(key):
    k = key.lower()
    if "salaire" in k or "salarial" in k or ("donnée" in k and "salarial" in k):
        return "salaire"
    if "formation" in k or "programme" in k:
        return "formation"
    if "admission" in k or ("exigence" in k and "admission" in k):
        return "admission"
    if "placement" in k or ("statistique" in k and "placement" in k):
        return "placement"
    if "marché" in k or "marche" in k:
        return "marché"
    if "qualit" in k or "aptitude" in k or "compétence" in k or "competence" in k:
        return "qualités"
    return None


def load_already_embedded(out_path):
    """Read existing chunks.jsonl, return set of slugs already done."""
    done = set()
    if not out_path.exists():
        return done
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                done.add(rec["slug"])
    return done


def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "chunks.jsonl"

    # Resume: skip already-embedded slugs
    done_slugs = load_already_embedded(out_path)
    print(f"Already embedded: {len(done_slugs)} slugs")

    coverage_map = load_coverage_map()
    slug_files = sorted(RAW_DIR.glob("*.json"))
    remaining = [f for f in slug_files
                 if json.loads(f.read_text(encoding="utf-8")).get("slug") not in done_slugs]
    print(f"Files remaining:  {len(remaining)}/{len(slug_files)}")

    if not remaining:
        print("Nothing to do.")
        return

    from fastembed import TextEmbedding
    print(f"Loading model: {MODEL_NAME} ...")
    model = TextEmbedding(MODEL_NAME)
    print(f"Model loaded (dim={MODEL_DIM})")

    # Append to existing output
    out_f = open(out_path, "a", encoding="utf-8")
    total_chunks = 0
    total_files = 0

    for slug_file in remaining:
        record = json.loads(slug_file.read_text(encoding="utf-8"))
        slug = record["slug"]
        nom = record["nom"]
        secteur = record["secteur"]
        sections_raw = record.get("sections_raw", {})
        pipeline_status = coverage_map.get(slug, {})

        # Collect all chunks for this file
        batch_texts = []
        batch_meta = []

        for section_key, section_text in sections_raw.items():
            if not section_text or not section_text.strip():
                continue
            concept = _key_to_concept(section_key)
            in_pipeline = pipeline_status.get(concept, False) if concept else False
            text_chunks = chunk_text(section_text)
            for n, chunk_text_str in enumerate(text_chunks):
                chunk_id = f"{slug}::{section_key}::{n}"
                batch_texts.append(chunk_text_str)
                batch_meta.append({
                    "id": chunk_id,
                    "slug": slug,
                    "nom": nom,
                    "secteur": secteur,
                    "section_key_original": section_key,
                    "text": chunk_text_str,
                    "present_in_pipeline": in_pipeline,
                })

        # Batch embed all chunks for this file at once
        if batch_texts:
            embeddings = list(model.embed(batch_texts, batch_size=EMBED_BATCH_SIZE))
            for meta, emb in zip(batch_meta, embeddings):
                meta["embedding"] = emb.tolist()
                out_f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            total_chunks += len(batch_texts)

        total_files += 1
        if total_files % 50 == 0:
            out_f.flush()
            elapsed = time.time() - t0
            rate = total_chunks / elapsed if elapsed > 0 else 0
            print(f"  {total_files}/{len(remaining)} files, {total_chunks} chunks, {rate:.0f} chunks/s")

    out_f.close()
    elapsed = time.time() - t0
    file_size_mb = out_path.stat().st_size / (1024 * 1024)

    print(f"\nDone:")
    print(f"  Files processed: {total_files}")
    print(f"  Total chunks:    {total_chunks}")
    print(f"  Embedding dim:   {MODEL_DIM}")
    print(f"  Output file:     {out_path} ({file_size_mb:.1f} MB)")
    print(f"  Execution time:  {elapsed:.1f}s")


if __name__ == "__main__":
    main()
