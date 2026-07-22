# Métiers Québec — Modernisation

Recréation moderne du site [metiers-quebec.org](https://www.metiers-quebec.org/), un guide éducatif québécois répertoriant plus de 1 500 métiers et professions dans 32 secteurs d'emploi.

## Objectif

Transformer un site vieillot (HTML frames, FrontPage 2002) en un site statique moderne, responsive, avec recherche instantanée et navigation par filtres — le tout gratuitement sur Cloudflare Pages.

## État actuel

| Phase | Statut | Détails |
|-------|--------|---------|
| Phase 1 — Prototype | ✅ Terminé | 4 pages, design system complet |
| Phase 2 — Scraping | ✅ Terminé | 413 métiers, 22 secteurs, 446 pages |
| Phase 3 — Génération | ✅ Terminé | Site statique 18 Mo dans `dist/` |
| Phase 4 — Audit | 🔄 En cours | Audit initial fait, à relancer sur site généré |
| Phase 5 — Déploiement | ⏳ En attente | Cloudflare Pages |

## Technologies

| Composant | Technologie | Justification |
|-----------|------------|---------------|
| Structure | HTML5 sémantique | Standard, accessibilité |
| Style | CSS3 (custom properties, grid, flexbox) | Responsive, moderne |
| Interaction | JavaScript vanilla | Aucune dépendance |
| Scraping | Python + urllib + HTMLParser | Pas de pip install |
| Génération | Python | Pas de dépendances externes |
| Hébergement | Cloudflare Pages | Gratuit, CDN global |

## Structure du projet

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
    ├── README.md           # Ce fichier
    ├── PLAN.md             # Plan d'exécution
    ├── PROTOTYPE.md        # Documentation prototype
    ├── SCRAPING.md         # Documentation scraping
    ├── SOURCES.md          # Sources officielles de données
    └── AUDIT.md            # Rapport d'audit
```

## Lancement

### Site prototype (Phase 1)

```bash
cd metiers-quebec-prototype
python3 -m http.server 8080
# Ouvrir http://localhost:8080
```

### Site généré (Phase 3)

```bash
cd metiers-quebec-prototype/dist
python3 -m http.server 8080
# Ouvrir http://localhost:8080
```

### Scraping complet

```bash
# 1. Scraping (~3 minutes, 460 requêtes HTTP)
python3 scraper/scrape_v2.py

# 2. Génération du site
python3 scraper/generate.py

# 3. Copier les assets
mkdir -p dist/css dist/js
cp css/style.css dist/css/
cp js/search.js dist/js/
```

## Audit

```bash
bash audit.sh
# Les résultats sont dans docs/AUDIT.md
```

## Sources

- Site original : https://www.metiers-quebec.org/
- Auteur original : Dany Savard (dsavard@metiers-quebec.org)
- Données : sources publiques québécoises (OIIQ, MES, ISQ, etc.)
- Voir `docs/SOURCES.md` pour la liste complète

## Documentation

- `docs/SCRAPING.md` — Procédure de scraping et décisions techniques
- `docs/SOURCES.md` — Sources officielles des données avec URLs
- `docs/AUDIT.md` — Rapport d'audit du site prototype
