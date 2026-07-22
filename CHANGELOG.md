# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.4.0] - 2026-07-22

### Added
- `query_test.py` : couche d'interrogation sémantique
  - Charge chunks.jsonl en mémoire une fois (11.1 MB embeddings)
  - Query(question, top_k=5) : cosine similarity sur bge-small-en-v1.5
  - Enrichissement avec graph_communities.json (métiers voisins)
  - 10 questions test fixes avec verdicts manuels
- `docs/kb007.md` : validation couche d'interrogation
  - 3 correct, 4 partiels, 2 échecs, 1 hors-corpus
  - Problèmes identifiés: pas de rejet hors-corpus, confusion métiers similaires
- `graph_bridge.py` : prefix matching au lieu d'égalité stricte
  - 305→416/418 slugs mappés (73%→99%)
  - 74 slugs multi-candidats, 312 sous-nœuds conservés
  - Seulement 2 absences réelles: commis-comptable, controleur_maritimel

### Changed
- README.md : refleté l'état réel du projet (legacy site statique, query layer terminé)
- Avertissement perte de données en haut du README (lien kb005.md)

## [0.3.0] - 2026-07-22

### Added
- `embed_corpus.py` : chunk + batch embedding (BAAI/bge-small-en-v1.5, 384-dim, fastembed ONNX)
  - 7 578 chunks, 418 slugs, 81 Mo
  - Batch 64 chunks/batch, reprise automatique sur timeout
- `graph_bridge.py` : mapping corpus → graph communities
  - 416/418 slugs mappés (99%, prefix matching)
  - 29 communautés, voisins par slug
- `entropy_dashboard_v2.py` : dashboard stats augmenté
  - source_vs_pipeline par concept
  - graph_communities distribution
  - embedding_kpis (chunks, slugs, pipeline_present/absent)
  - section_entropy (clés uniques par concept)
- `data/graph_communities.json` : 305 slugs avec community, neighbors, secteur
- `dist/data/stats.json` : augmenté avec nouvelles sections

### Changed
- `embed_corpus.py` : réécrit avec batch embedding (64/batch) + resume support
  - Premier lancement timeout à 600s → réécriture avec batch
- `embeddings` exclus du tracking git (81 Mo)
- `.gitignore` : exclus `.graphify_*`, `cache/`, `2026-*/`, `*.sig`, `data/embeddings/`

### Coverage
- salaire: 5.0% (21/418)
- formation: 5.7% (24/418)
- admission: 40.4% (169/418)
- placement: 1.9% (8/418)
- marché: 9.3% (39/418)
- qualités: 2.6% (11/418)

## [0.2.0] - 2026-07-22

### Added
- `corpus_raw_v2.py` : extraction corpus brut préservant toutes les clés
  - 418 slugs uniques, 2 387 sections, 30 clés de sections
  - Sortie : `data/corpus_raw_v2/{slug}.json`
- `coverage_split.py` : analyse couverture source vs pipeline
  - Détection pipeline corrigée (vérifie contenu réel, pas juste l'en-tête)
  - Sortie : `data/coverage_report.json`
- `docs/kb005.md` : documentation problèmes couverture
  - Pipeline lossy : SECTION_MAP ne préserve que 5/30 clés
  - Faux positif "rémunération" (analyse corrigée)
  - Pipeline affiche toujours en-têtes même si données absentes

### Fixed
- Coverage analysis : ne plus se fier à l'en-tête HTML, vérifier le contenu réel
- Section key mapping : préservation de toutes les clés (pas de normalisation lossy)

## [0.1.2] - 2026-07-21

### Added
- Graphify knowledge graph extraction (2 566 noeuds, 303 communautés initiales)
- `docs/kb003.md` : déploiement Cloudflare Pages

### Fixed
- Wrangler config : `pages_build_output_dir`, `name`
- Restauration `dist/` pour Cloudflare Pages

## [0.1.1] - 2026-07-21

### Added
- Page statistiques avec 5 graphiques Chart.js (KPIs + visualisations)
- Header fixe avec logo SVG fleur-de-lis, barre recherche intégrée, navigation
- Sidebar gauche avec sections "Navigation" et "Secteurs d'emploi" (11 icônes SVG)
- Hero section sur homepage : badge, titre, search, 3 cartes stats
- Breadcrumb avec séparateurs `/` et aria-label "Fil d'Ariane"
- Pages secteur avec `page-header` (tag + titre)
- Pages métier avec `page-header` (back link + tag + titre)
- Cartes `prof-meta` (Secteur, Niveau d'études)
- Icônes SVG sur toutes les `content-section`
- Extraction automatique du niveau d'études depuis les données
- Fallback extraction description depuis le bloc `intro`
- `wrangler.toml` pour déploiement Cloudflare Pages
- `docs/kb001.md` : audit accessibilité axe-core (0 violations)
- `docs/kb002.md` : dette technique fiches emploi
- 7 métiers bâtiment manquants scrapés

### Changed
- Homepage : 12 secteurs au lieu de 30 (préparation mobile)
- `fmt()` : normalisation des sauts de ligne
- Titres métiers capitalisés (`title()`)
- Breadcrumb utilise le nom capitalisé

### Fixed
- color-contrast : `#94a3b8` → `#64748b`
- landmark-unique : `aria-label` sur tous les `<nav>`
- SSL bypass pour scraping manquant
- Section key mapping : normalisation des clés majuscules avec newlines

## [0.1.0] - 2026-07-21

### Added
- Scraper principal (`scrape_v2.py`) avec auto-détection encoding
- Générateur HTML (`generate.py`) : 446 pages statiques
- 413 métiers détaillés scrapés depuis metiers-quebec.org
- 30 secteurs d'emploi identifiés
- Design system CSS complet (variables, responsive, dark mode ready)
- Recherche fuzzy instantanée (`search.js`)
- Navigation alphabétique (`/alpha/`)
- Pages secteur (`/secteur/*/`)
- Pages métier (`/metier/*/`)
- Index alphabétique complet
- Validation HTML (htmlhint)
- Audit accessibilité (axe-core)
- Documentation : README, PLAN, PROTOTYPE, SOURCES, SCRAPING, AUDIT
