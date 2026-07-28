# Métiers Québec — Nouveau

Site moderne de [metiers-quebec.org](https://www.metiers-quebec.org/), un guide éducatif québécois répertoriant 420 métiers et professions dans 30 secteurs d'emploi.

**Live** : https://metiers-quebec-org.weathered-water-5f20.workers.dev/

## Objectif

Transformer un site vieillot (HTML frames, FrontPage 2002) en un site statique moderne, responsive, avec recherche instantanée — gratuitement sur Cloudflare Pages.

## État actuel

| Phase | Statut | Détails |
|-------|--------|---------|
| Phase 1 — Prototype | ✅ Terminé | Design system complet, layout sidebar/header/hero |
| Phase 2 — Scraping | ✅ Terminé | 420 métiers, 30 secteurs |
| Phase 3 — Génération | ✅ Terminé | 457 pages statiques |
| Phase 4 — Audit | ✅ Terminé | 0 violation axe-core (accessibilité) |
| Phase 5 — Déploiement | ✅ Terminé | Cloudflare Pages |

## Technologies

| Composant | Technologie |
|-----------|------------|
| Structure | HTML5 sémantique |
| Style | CSS3 (custom properties, grid, flexbox) |
| Interaction | JavaScript vanilla (recherche fuzzy) |
| Graphiques | Chart.js v4.5.0 (CDN) |
| Scraping | Python + urllib + HTMLParser |
| Hébergement | Cloudflare Pages (gratuit) |

## Structure

```
├── dist/                       # Site statique (457 pages)
│   ├── index.html              # Accueil
│   ├── secteurs/index.html     # Liste des secteurs
│   ├── secteur/*/index.html    # 30 pages secteur
│   ├── metier/*/index.html     # 420 fiches emploi
│   ├── alpha/index.html        # Index alphabétique
│   ├── stats/index.html        # Statistiques (5 graphiques)
│   ├── css/style.css           # Design system
│   ├── js/search.js            # Recherche fuzzy
│   ├── js/stats.js             # Chart.js
│   └── data/*.json             # Données pré-calculées
├── scraper/
│   ├── scrape_v2.py            # Scraper principal
│   ├── scrape_missing.py       # Scraper complémentaire
│   └── generate.py             # Générateur HTML
├── data/
│   ├── professions_details.json # 420 métiers détaillés (21 Mo)
│   └── sectors.json            # 30 secteurs
├── docs/
│   ├── kb001.md                # Accessibilité (axe-core)
│   ├── kb002.md                # Dette technique fiches emploi
│   └── kb003.md                # Déploiement Cloudflare
├── wrangler.toml               # Config Cloudflare Pages
├── CHANGELOG.md                # Historique des versions
└── audit.sh                    # Script d'audit
```

## Lancement local

```bash
cd dist
python3 -m http.server 8080
# Ouvrir http://localhost:8080
```

## Régénération

```bash
python3 scraper/scrape_v2.py     # Scraping (~3 min)
python3 scraper/generate.py      # Génération HTML
```

## Déploiement

Le déploiement est automatique : chaque push sur `main` déclenche un build Cloudflare Pages.

```bash
git add -A && git commit -m "description" && git push origin main
```

Voir `docs/kb003.md` pour la configuration détaillée.

## Accessibilité

Audit automatisé avec axe-core : **0 violation** sur toutes les pages testées.

```bash
cd /tmp && node audit_stats.mjs
```

## Sources

- Site original : https://www.metiers-quebec.org/
- Auteur original : Dany Savard
- Données : sources publiques québécoises (OIIQ, MES, ISQ, etc.)
