#!/usr/bin/env python3
"""
graph_bridge.py — Map corpus_raw_v2 slugs → graph communities + neighbors

Matching: prefix-based. For each corpus slug, find all graph nodes whose ID
starts with "metier_" + slug ("_" or end-of-string). The shortest ID wins
as the main node (most likely the "full page" node). Others are listed as
related_subnodes (sub-concepts mentioned within the page).

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


def build_slug_candidates(graph_nodes):
    """Build {slug: [node, ...]} via prefix matching on metier_ IDs.

    A node ID like "metier_administration1" matches slug "administration1".
    A node ID like "metier_administration1_admission_prepose" also matches
    slug "administration1" (it's a sub-concept on that page).
    """
    candidates = defaultdict(list)
    for node in graph_nodes:
        nid = node.get("id", "")
        if not nid.startswith("metier_"):
            continue
        prefix = nid[len("metier_"):]  # everything after "metier_"
        # We store all candidates; the caller picks by slug
        candidates[prefix].append(node)
    return candidates


def find_candidates_for_slug(slug, prefix_map):
    """Find all metier_ nodes matching a slug via prefix matching.

    Returns (main_node, [subnodes]) where main_node has the shortest ID.
    """
    # Exact match first
    if slug in prefix_map:
        nodes = prefix_map[slug]
    else:
        # Prefix match: IDs that start with slug_
        nodes = []
        for key, node_list in prefix_map.items():
            if key.startswith(slug + "_"):
                nodes.extend(node_list)

    if not nodes:
        return None, []

    # Shortest ID wins as main node
    nodes_sorted = sorted(nodes, key=lambda n: len(n["id"]))
    main = nodes_sorted[0]
    subnodes = [n["id"] for n in nodes_sorted[1:]]
    return main, subnodes


def main():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    # Build prefix map: {node_id_without_metier_: [node, ...]}
    prefix_map = defaultdict(list)
    for node in graph["nodes"]:
        nid = node.get("id", "")
        if nid.startswith("metier_"):
            key = nid[len("metier_"):]
            prefix_map[key].append(node)

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
    multi_match = 0
    subnode_total = 0

    for slug in sorted(corpus_slugs):
        node, subnodes = find_candidates_for_slug(slug, prefix_map)
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

    print(f"Graph bridge done (prefix matching):")
    print(f"  Corpus slugs:       {len(corpus_slugs)}")
    print(f"  Matched to graph:   {found}/{len(corpus_slugs)} ({found*100//len(corpus_slugs)}%)")
    print(f"  Missing (no node):  {len(missing)}")
    print(f"  Multi-candidate:    {multi_match} slugs ({subnode_total} subnodes)")
    print(f"  Communities:        {len(comm_count)}")
    print(f"  Output:             {OUT_PATH}")
    print()
    print("Top communities:")
    for comm, cnt in comm_count.most_common(10):
        print(f"  {comm}: {cnt}")
    if missing:
        print(f"\nMissing slugs: {missing}")


if __name__ == "__main__":
    main()
