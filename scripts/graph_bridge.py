#!/usr/bin/env python3
"""
graph_bridge.py — Map corpus_raw_v2 slugs → graph communities + neighbors

Reads:  dist/graphify-out/graph.json
        data/corpus_raw_v2/*.json
Writes: data/graph_communities.json

Output format:
{
  "slug": {
    "graph_node_id": "metier_slug",
    "community": "Mining & Construction",
    "community_id": 5,
    "neighbors": ["neighbor1", "neighbor2"],
    "neighbor_count": 4,
    "secteur_graph": "secteur_mines"
  }
}
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).parent.parent
GRAPH_PATH = BASE_DIR / "dist" / "graphify-out" / "graph.json"
RAW_DIR = BASE_DIR / "data" / "corpus_raw_v2"
OUT_PATH = BASE_DIR / "data" / "graph_communities.json"


def main():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    # Build slug → node
    slug_to_node = {}
    for node in graph["nodes"]:
        nid = node.get("id", "")
        if nid.startswith("metier_"):
            slug = nid[len("metier_"):]
            slug_to_node[slug] = node

    # Build link index: node_id → set of neighbor ids
    link_index = defaultdict(set)
    for link in graph["links"]:
        link_index[link["source"]].add(link["target"])
        link_index[link["target"]].add(link["source"])

    # Load corpus slugs
    corpus_slugs = set()
    for f in RAW_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        corpus_slugs.add(data["slug"])

    # Build mapping
    result = {}
    found = 0
    missing = []

    for slug in sorted(corpus_slugs):
        node = slug_to_node.get(slug)
        if not node:
            missing.append(slug)
            continue

        nid = node["id"]
        neighbors = sorted(link_index.get(nid, set()))

        # Find secteur neighbor
        secteur_graph = None
        for nb in neighbors:
            if nb.startswith("secteur_"):
                secteur_graph = nb
                break

        result[slug] = {
            "graph_node_id": nid,
            "community": node.get("community_name", "unknown"),
            "community_id": node.get("community", -1),
            "neighbors": neighbors,
            "neighbor_count": len(neighbors),
            "secteur_graph": secteur_graph,
        }
        found += 1

    # Stats
    comm_count = Counter(v["community"] for v in result.values())

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Graph bridge done:")
    print(f"  Corpus slugs:     {len(corpus_slugs)}")
    print(f"  Matched to graph: {found}")
    print(f"  Missing (no node): {len(missing)}")
    print(f"  Communities:      {len(comm_count)}")
    print(f"  Output:           {OUT_PATH}")
    print()
    print("Top communities:")
    for comm, cnt in comm_count.most_common(10):
        print(f"  {comm}: {cnt}")
    if missing:
        print(f"\nMissing slugs (first 10): {missing[:10]}")


if __name__ == "__main__":
    main()
