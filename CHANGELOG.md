# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

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
- `page-header__meta` sous le titre des fiches emploi
- Icônes SVG sur toutes les `content-section`
- Extraction automatique du niveau d'études depuis les données
- Fallback extraction description depuis le bloc `intro`
- `wrangler.toml` pour déploiement Cloudflare Pages
- `docs/kb001.md` : audit accessibilité axe-core (0 violations)
- `docs/kb002.md` : dette technique fiches emploi
- 7 métiers bâtiment manquants scrapés (architecte, arpenteur, briqueteur, cimentier, dynamiteur, géologue, peintre)

### Changed
- Homepage : 12 secteurs au lieu de 30 (préparation mobile)
- `fmt()` : normalisation des sauts de ligne (`" ".join(item.split())`)
- Titres métiers capitalisés (`title()`)
- Breadcrumb utilise le nom capitalisé

### Fixed
- color-contrast : `#94a3b8` → `#64748b`, `.section__link` → `var(--primary)`
- landmark-unique : `aria-label` sur tous les `<nav>`
- SSL bypass pour scraping manquant (`scrape_missing.py`)
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
