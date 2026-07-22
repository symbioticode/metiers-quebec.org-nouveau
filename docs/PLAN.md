# Plan d'exécution

## Phase 1 — Prototype design ✅

Création d'un prototype visuel avec 4 pages et composants réutilisables.

- [x] Structure de fichiers
- [x] CSS design system (couleurs, typographie, composants)
- [x] Page d'accueil `index.html`
- [x] Page secteur `secteur.html` (exemple : Santé)
- [x] Page métier `profession.html` (exemple : Infirmière)
- [x] Index alphabétique `alpha.html`
- [x] JavaScript recherche + navigation `js/search.js`

## Phase 2 — Scraping du contenu ✅

Extraction de tout le contenu du site actuel metiers-quebec.org.

- [x] Exploration de la structure du site (frames, FrontPage, encoding)
- [x] Script de scraping Python (urllib + HTMLParser, sans dépendances)
- [x] Extraction de la liste des métiers via index alphabétique (458 métiers)
- [x] Extraction des 22 secteurs et leurs métiers
- [x] Scraping détaillé de 413 pages métier (90% réussite)
- [x] Détection et correction d'encodage (windows-1252 / UTF-8)
- [x] Mapping multi-variantes des URLs vers les secteurs
- [x] Stockage en JSON (`data/*.json`)

**Décisions clés :**
- Python + urllib au lieu de Node.js (pas de dépendances npm)
- HTMLParser stdlib au lieu de BeautifulSoup (pas de pip install)
- Détection d'encodage automatique (le site mélange windows-1252 et UTF-8)
- Scraping séquentiel avec delai 0.3s (respectueux du serveur)

Voir `docs/SCRAPING.md` pour la documentation détaillée.

## Phase 3 — Génération du site statique ✅

Build automatisé qui transforme les données JSON en pages HTML.

- [x] Script de génération Python (`scraper/generate.py`)
- [x] Templates HTML pour chaque type de page (accueil, secteur, métier, A-Z)
- [x] Génération de 413 pages de métiers
- [x] Génération de 22 pages de secteurs + 1 index secteurs
- [x] Génération de l'index alphabétique
- [x] Index de recherche JSON pour la recherche côté client
- [x] Copie des assets CSS/JS

**Résultat :** 446 pages HTML, 18 Mo total dans `dist/`.

## Phase 4 — Audit et validation

Vérification qualité automatisée.

- [x] Audit initial du prototype (23 erreurs, 12 critiques)
- [x] Corrections critiques appliquées (javascript:void(0), liens sources)
- [ ] Relancer l'audit sur le site généré (413 pages)
- [ ] Validation HTML (W3C vnu-jar)
- [ ] Accessibilité (axe-core, pa11y — nécessite Chromium)
- [ ] Liens cassés (linkinator)
- [ ] Performance + SEO (Lighthouse)
- [ ] Mise à jour de `docs/AUDIT.md`

## Phase 5 — Déploiement

Mise en ligne sur Cloudflare Pages.

- [ ] Configurer le repo Git
- [ ] Configurer Cloudflare Pages
- [ ] Script de build pour Cloudflare
- [ ] Déployer et tester
- [ ] Configurer un domaine personnalisé (optionnel)

## Fichiers du projet

```
metiers-quebec-prototype/
├── index.html              # Prototype page d'accueil
├── secteur.html            # Prototype secteur
├── profession.html         # Prototype métier
├── alpha.html              # Prototype A-Z
├── css/style.css           # Design system
├── js/search.js            # Recherche fuzzy
├── scraper/
│   ├── scrape_v2.py        # Script de scraping
│   ├── generate.py         # Générateur de site
│   └── fix_encoding.py     # Correction encodage
├── data/
│   ├── professions_urls.json    # URLs de tous les métiers
│   ├── professions_details.json # Données détaillées (21 Mo)
│   ├── sectors.json             # Données des secteurs
│   └── search_index.json        # Index de recherche
├── dist/                   # Site statique généré (18 Mo)
│   ├── index.html
│   ├── css/style.css
│   ├── js/search.js
│   ├── data/search.json
│   ├── secteur/*/index.html
│   ├── alpha/index.html
│   └── metier/*/index.html
├── audit.sh                # Script d'audit automatisé
└── docs/
    ├── README.md           # Vue d'ensemble
    ├── PLAN.md             # Ce fichier
    ├── PROTOTYPE.md        # Documentation prototype
    ├── SCRAPING.md         # Documentation scraping
    ├── SOURCES.md          # Sources officielles de données
    └── AUDIT.md            # Rapport d'audit
```
