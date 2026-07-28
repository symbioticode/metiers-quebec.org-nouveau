#!/usr/bin/env python3
"""
graph_bridge.py — Map corpus_raw_v2 slugs → graph communities + neighbors

Algorithm: node-centric longest-prefix-wins.
For each graph node (metier_ prefix stripped → key):
  - Sort corpus_slugs by length descending
  - Find the FIRST slug s (longest, most specific) such that key == s or key.startswith(s + "_")
  - Assign this node exclusively to s

This eliminates the asymmetric bug where slugs without exact-match nodes
got contaminated by sibling sub-concepts (see docs/kb009.md — resolved).

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
    "secteur_graph": "secteur_mines",
    "related_subnodes": ["metier_slug_sub1", "metier_slug_sub2"]
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


def assign_nodes_to_slugs(graph, corpus_slugs):
    """Node-centric assignment: each metier_ node goes to its longest matching slug.

    Returns {slug: [node, ...]} with exclusive assignment.
    """
    # Sort slugs longest-first for greedy longest-prefix matching
    sorted_slugs = sorted(corpus_slugs, key=len, reverse=True)

    slug_nodes = defaultdict(list)
    unassigned = []

    for node in graph["nodes"]:
        nid = node.get("id", "")
        if not nid.startswith("metier_"):
            continue
        key = nid[len("metier_"):]

        # Find longest matching slug
        assigned = False
        for s in sorted_slugs:
            if key == s or key.startswith(s + "_"):
                slug_nodes[s].append(node)
                assigned = True
                break
        if not assigned:
            unassigned.append(nid)

    return slug_nodes, unassigned


def main():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    # Load corpus slugs
    corpus_slugs = set()
    for fp in RAW_DIR.glob("*.json"):
        data = json.loads(fp.read_text(encoding="utf-8"))
        corpus_slugs.add(data["slug"])

    # Node-centric assignment
    slug_nodes, unassigned = assign_nodes_to_slugs(graph, corpus_slugs)

    # Build link index: node_id → set of neighbor ids
    link_index = defaultdict(set)
    for link in graph["links"]:
        link_index[link["source"]].add(link["target"])
        link_index[link["target"]].add(link["source"])

    # Build result
    result = {}
    found = 0
    missing = []
    multi_match = 0
    subnode_total = 0

    for slug in sorted(corpus_slugs):
        nodes = slug_nodes.get(slug, [])
        if not nodes:
            missing.append(slug)
            continue

        # Shortest ID wins as main node
        nodes_sorted = sorted(nodes, key=lambda n: len(n["id"]))
        main = nodes_sorted[0]
        subnodes = [n["id"] for n in nodes_sorted[1:]]

        nid = main["id"]
        neighbors = sorted(link_index.get(nid, set()))

        secteur_graph = None
        for nb in neighbors:
            if nb.startswith("secteur_"):
                secteur_graph = nb
                break

        result[slug] = {
            "graph_node_id": nid,
            "community": main.get("community_name", "unknown"),
            "community_id": main.get("community", -1),
            "neighbors": neighbors,
            "neighbor_count": len(neighbors),
            "secteur_graph": secteur_graph,
            "related_subnodes": subnodes,
        }
        found += 1
        if subnodes:
            multi_match += 1
            subnode_total += len(subnodes)

    # Stats
    comm_count = Counter(v["community"] for v in result.values())

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Graph bridge done (node-centric longest-prefix-wins):")
    print(f"  Corpus slugs:       {len(corpus_slugs)}")
    print(f"  Matched to graph:   {found}/{len(corpus_slugs)} ({found*100//len(corpus_slugs)}%)")
    print(f"  Missing (no node):  {len(missing)}")
    print(f"  Multi-candidate:    {multi_match} slugs ({subnode_total} subnodes)")
    print(f"  Communities:        {len(comm_count)}")
    print(f"  Unassigned nodes:   {len(unassigned)}")
    print(f"  Output:             {OUT_PATH}")
    print()
    print("Top communities:")
    for comm, cnt in comm_count.most_common(10):
        print(f"  {comm}: {cnt}")
    if missing:
        print(f"\nMissing slugs: {missing}")
    if unassigned:
        print(f"\nUnassigned nodes (first 10): {unassigned[:10]}")


if __name__ == "__main__":
    main()
