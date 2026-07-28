# Métiers Québec — Graphe de Connaissances

Modernisation du site [metiers-quebec.org](https://www.metiers-quebec.org/) en **graphe de connaissances queryable** pour chatbot RAG.

> **Attention** : Le pipeline de scraping du site original ne préserve que 2-40% des données brutes selon les concepts. Voir [docs/kb005.md](docs/kb005.md) pour l'analyse détaillée.

## Objectif

Transformer 418 fiches métier scrapées en un corpus structuré, chunké et vectorisé, connecté à un graphe de connaissances de 2566 noeuds — permettant des requêtes sémantiques précises sur les métiers québécois.

## État du projet

| Phase | Statut | Détails |
|-------|--------|---------|
| Phase 1-3 — Site statique | ⚠️ Legacy | 418 métiers, mapping incomplet documenté en `docs/kb002.md` |
| Phase 4 — Couche d'interrogation | ✅ Terminé | Corpus brut + embeddings + graphe + query layer |
| Phase 5 — Validation | ✅ Terminé | 10 questions test, verdicts manuels en `docs/kb007.md` |
| Phase 6 — Déploiement | ⏳ En attente | Cloudflare Pages |

## Résultats

| Métrique | Valeur |
|----------|--------|
| Métiers scrapés | **418** (slugs uniques) |
| Secteurs | **30** |
| Clés de sections | **30** (sections_raw préservées, pas de mapping lossy) |
| Chunks texte | **7 578** |
| Embeddings | **7 578** (BAAI/bge-small-en-v1.5, 384-dim, gratuit) |
| Noeuds graphe | **2 566** (Graphify) |
| Slugs mappés au graphe | **416** / 418 (99%) |
| Communautés graphe | **83** |
| Concepts coverage | **6** (salaire, formation, admission, placement, marché, qualités) |
| Temps query/question | **~1.9s** (CPU, pas de GPU) |

## Couverture source vs pipeline

Le pipeline existant du site original ne préserve qu'une fraction des données :

| Concept | Source | Pipeline | Couverture |
|---------|--------|----------|------------|
| admission | 418 | 169 | **40.4%** |
| marché | 418 | 39 | 9.3% |
| formation | 418 | 24 | 5.7% |
| salaire | 418 | 21 | 5.0% |
| qualités | 418 | 11 | 2.6% |
| placement | 418 | 8 | **1.9%** |

→ Le pipeline actuel perd **87-97%** des données pour 5/6 concepts. Voir `docs/kb005.md`.

## Technologies

| Composant | Technologie | Justification |
|-----------|------------|---------------|
| Corpus | Python + urllib + HTMLParser | Scraping sans dépendances lourdes |
| Embeddings | fastembed (BAAI/bge-small-en-v1.5) | ONNX, 33M params, gratuit, pas de PyTorch |
| Graphe | Graphify | Extraction automatique de connaissances |
| Hébergement | Cloudflare Pages | Gratuit, CDN global |

## Structure du projet

```
metiers-quebec-prototype/
├── scripts/
│   ├── corpus_raw_v2.py        # Extraction corpus brut (418 slugs, 2387 sections)
│   ├── embed_corpus.py         # Chunk + batch embedding (7578 chunks, 384-dim)
│   ├── graph_bridge.py         # Mapping corpus → graph communities (prefix match)
│   ├── coverage_split.py       # Analyse couverture source vs pipeline
│   ├── entropy_dashboard_v2.py # Dashboard stats augmenté
│   └── query_test.py           # Couche d'interrogation + 10 questions test
├── data/
│   ├── corpus_raw_v2/          # 418 JSON (sections_raw préservées)
│   ├── embeddings/
│   │   └── chunks.jsonl        # 7578 chunks avec embeddings (81 Mo)
│   ├── graph_communities.json  # 416 slugs → communautés + voisins
│   └── coverage_report.json    # Couverture source vs pipeline
├── dist/                       # Site statique (31 Mo)
│   ├── graphify-out/           # Graphe Graphify (2566 noeuds)
│   └── data/stats.json         # Statistiques augmentées
└── docs/
    ├── kb005.md                # Problèmes couverture source/pipeline
    ├── kb006.md                # Choix modèle embedding + coûts
    └── kb007.md                # Validation couche d'interrogation
```

## Lancement

### Site statique

```bash
cd dist
python3 -m http.server 8080
# http://localhost:8080
```

### Couche d'interrogation

```bash
# Test automatisé (10 questions)
nix-shell --run '.venv/bin/python scripts/query_test.py --test'

# Mode interactif
nix-shell --run '.venv/bin/python scripts/query_test.py'
```

### Génération corpus + embeddings

```bash
# 1. Corpus brut (~30s)
python3 scripts/corpus_raw_v2.py

# 2. Coverage analysis
python3 scripts/coverage_split.py

# 3. Embeddings (~45 min, batch, reprise automatique)
python3 scripts/embed_corpus.py

# 4. Graph bridge (prefix matching)
python3 scripts/graph_bridge.py

# 5. Dashboard stats
python3 scripts/entropy_dashboard_v2.py
```

### Venv (nix-shell)

```bash
nix-shell
.venv/bin/python scripts/embed_corpus.py
```

## Sources

- Site original : https://www.metiers-quebec.org/
- Données : sources publiques québécoises (OIIQ, MES, ISQ, etc.)
- Voir `docs/SOURCES.md` pour la liste complète

## Documentation

| Fichier | Description |
|---------|-------------|
| `docs/kb005.md` | Problèmes couverture source vs pipeline (perte de données) |
| `docs/kb006.md` | Choix modèle embedding + coûts |
| `docs/kb007.md` | Validation couche d'interrogation (10 questions, verdicts manuels) |
| `docs/SCRAPING.md` | Procédure de scraping |
| `docs/SOURCES.md` | Sources officielles des données |
| `docs/AUDIT.md` | Rapport d'audit accessibilité |
