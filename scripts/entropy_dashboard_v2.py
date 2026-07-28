#!/usr/bin/env python3
"""
entropy_dashboard_v2.py — Augment stats.json with source vs pipeline coverage

Reads:  data/coverage_report.json
        data/graph_communities.json
        data/embeddings/chunks.jsonl
        dist/data/stats.json (existing stats from pipeline)
Writes: dist/data/stats.json (augmented)
"""

import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
COVERAGE_PATH = BASE_DIR / "data" / "coverage_report.json"
GRAPH_PATH = BASE_DIR / "data" / "graph_communities.json"
CHUNKS_PATH = BASE_DIR / "data" / "embeddings" / "chunks.jsonl"
STATS_PATH = BASE_DIR / "dist" / "data" / "stats.json"
RAW_DIR = BASE_DIR / "data" / "corpus_raw_v2"


def main():
    # Load existing stats
    stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))

    # --- Source vs Pipeline coverage ---
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    source_vs_pipeline = []
    for concept, data in coverage.get("concepts", {}).items():
        details = data.get("details", [])
        source_count = len(details)  # all slugs in source
        pipeline_count = sum(1 for d in details if d.get("present_in_pipeline", False))
        source_vs_pipeline.append({
            "concept": concept,
            "source_count": source_count,
            "pipeline_count": pipeline_count,
            "coverage_pct": round(pipeline_count / source_count * 100, 1) if source_count else 0,
            "source_label": f"Source ({concept})",
            "pipeline_label": f"Pipeline ({concept})",
        })
    stats["source_vs_pipeline"] = sorted(source_vs_pipeline, key=lambda x: x["coverage_pct"])

    # --- Graph community distribution ---
    graph_comm = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    community_counter = Counter(v["community"] for v in graph_comm.values())
    stats["graph_communities"] = [
        {"community": c, "count": n}
        for c, n in community_counter.most_common()
    ]
    stats["graph_kpis"] = {
        "total_corpus_slugs": len(graph_comm),
        "matched_to_graph": sum(1 for v in graph_comm.values() if v["graph_node_id"]),
        "total_communities": len(community_counter),
    }

    # --- Embedding stats ---
    chunk_slugs = set()
    chunk_sections = Counter()
    total_chunks = 0
    pipeline_present = 0
    if CHUNKS_PATH.exists():
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                total_chunks += 1
                chunk_slugs.add(rec["slug"])
                chunk_sections[rec["section_key_original"]] += 1
                if rec.get("present_in_pipeline"):
                    pipeline_present += 1

    stats["embedding_kpis"] = {
        "total_chunks": total_chunks,
        "unique_slugs": len(chunk_slugs),
        "pipeline_present_chunks": pipeline_present,
        "pipeline_absent_chunks": total_chunks - pipeline_present,
        "avg_chunks_per_slug": round(total_chunks / len(chunk_slugs), 1) if chunk_slugs else 0,
    }

    # --- Source section entropy (how many unique section keys per concept) ---
    concept_sections = {}
    for f in RAW_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        for key in data.get("sections_raw", {}):
            concept = key.split("::")[0] if "::" in key else key
            concept_sections.setdefault(concept, set()).add(key)

    stats["section_entropy"] = [
        {"concept": c, "unique_keys": len(keys)}
        for c, keys in sorted(concept_sections.items(), key=lambda x: -len(x[1]))
    ]

    # --- KPIs update ---
    stats["kpis"]["total_corpus_raw"] = len(list(RAW_DIR.glob("*.json")))
    stats["kpis"]["total_embeddings"] = total_chunks
    stats["kpis"]["graph_match_pct"] = round(
        stats["graph_kpis"]["matched_to_graph"] / stats["graph_kpis"]["total_corpus_slugs"] * 100, 1
    )

    # Write augmented stats
    STATS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Entropy dashboard v2 done:")
    print(f"  Source vs pipeline: {len(source_vs_pipeline)} concepts")
    print(f"  Graph communities: {len(community_counter)}")
    print(f"  Embedding chunks:  {total_chunks}")
    print(f"  Output: {STATS_PATH}")
    print()
    print("Coverage source vs pipeline:")
    for item in source_vs_pipeline:
        bar = "#" * int(item["coverage_pct"] / 5)
        print(f"  {item['concept']:20s} {item['coverage_pct']:5.1f}% ({item['pipeline_count']}/{item['source_count']}) {bar}")


if __name__ == "__main__":
    main()
