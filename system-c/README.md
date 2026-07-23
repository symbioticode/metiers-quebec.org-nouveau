# System C — Sources d'Emploi Québec

> Agrégateur de 16 sources gouvernementales et institutionnelles sur l'emploi, les métiers et la formation au Québec.

**Statut** : Prototype fonctionnel  
**Version** : 1.0  
**Dernière mise à jour** : 2026-07-23

---

## 1. Vue d'ensemble

System C est un projet indépendant — vivant dans le même dépôt que Métiers Québec — qui centralise l'accès aux données publiques sur l'emploi au Québec. Il agrège les métadonnées de **16 sources** (gouvernements provincial et fédéral, organismes institutionnels, portails de données ouvertes) dans un flux **JSON Feed 1.1** normalisé, consommable par une interface web de visualisation.

### Pourquoi

- Pas de source unique pour les données emploi au Québec
- Les 16 sources ont des formats, structures et API très hétérogènes
- Besoin d'un point d'entrée unifié pour les chercheurs d'emploi, les organismes d'aide et les développeurs

### Résultat

- `sources-emploi-quebec.json` : catalogue structuré des 16 sources
- `feed/emploi.json` : flux JSON Feed 1.1 agrégé (15 items, ~18 Ko)
- `prototype-feed.html` : interface web de visualisation

---

## 2. Architecture

```
┌─────────────────────────┐
│  sources-emploi-quebec  │  Catalogue JSON (16 sources)
│        .json            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   scripts/build-feed    │  Script Python agrégateur
│        .py              │  (fetch API + items statiques)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    feed/emploi.json     │  JSON Feed 1.1 généré
│    (15 items, 18 Ko)    │  Extension _quebec_emploi
└───────────┬─────────────┘
            │
     ┌──────┴──────┐
     ▼             ▼
┌─────────┐  ┌──────────────┐
│ feed.js │  │ prototype-   │  Consommateur client
│ (389 l) │  │ feed.html    │  (grille, filtres, modal)
└─────────┘  └──────────────┘
```

### Fichiers System C

| Fichier | Taille | Rôle |
|---|---|---|
| `sources-emploi-quebec.json` | 8.9 Ko | Catalogue des 16 sources |
| `scripts/build-feed.py` | 20.8 Ko | Script Python d'agrégation |
| `data/feed-schema.json` | 5.7 Ko | Schéma JSON Feed 1.1 + extension |
| `feed/emploi.json` | 18.8 Ko | Flux généré (15 items) |
| `js/feed.js` | 14.8 Ko | Module JS de visualisation |
| `prototype-feed.html` | 14.0 Ko | Page prototype autonome |

---

## 3. Sources (16)

### Récapitulatif

| ID | Nom | Type | Formats | API | RSS |
|---|---|---|---|---|---|
| 1 | Québec emploi | Provincial | HTML | — | — |
| 2 | Emplois en ligne – FPQ | Provincial | HTML | — | — |
| 3 | IMT en ligne | Provincial | HTML, PDF | — | — |
| 4 | Emplois d'avenir | Provincial | HTML | — | — |
| 5 | MTESS – Bulletins | Provincial | PDF, XLSX | — | — |
| 6 | Données Québec | Ouvertes | CSV, XLSX, JSON, API | ✅ | — |
| 7 | Métiers d'avenir | Institutionnel | HTML | — | — |
| 8 | ISQ | Institutionnel | HTML, PDF, XLSX, CSV | — | — |
| 9 | CPMT | Institutionnel | HTML, PDF | — | — |
| 10 | CCQ | Institutionnel | HTML, PDF | — | — |
| 11 | Statistique Canada | Fédéral | CSV, XML, JSON, SDMX | ✅ | — |
| 12 | Guichet-Emplois | Fédéral | HTML, PDF, RSS | — | ✅ |
| 13 | NOC / OaSIS | Fédéral | CSV, HTML, XML, API | ✅ | — |
| 14 | LMIC-CIMT | Fédéral | HTML, PDF, CSV, API | ✅ | — |
| 15 | Open Canada | Fédéral | CSV, XLSX, XML, JSON | ✅ | — |
| 16 | Qualifications Québec | Institutionnel | HTML, XML | — | — |

### Par type

**Gouvernement provincial (5)**
Sources légales et officielles du Québec : offres d'emploi, métiers, marché du travail, publications.

**Organismes institutionnels (4)**
ISQ (statistiques), CPMT (partenaires), CCQ (construction), Qualifications Québec (reconnaissance des compétences).

**Fédéral Canada (5)**
StatCan, Guichet-Emplois, NOC, LMIC-CIMT, Open Canada.

**Données ouvertes (1)**
Données Québec (CKAN) — 1600+ jeux de données.

### Sources avec API programmatique

| Source | API | Type | Accès |
|---|---|---|---|
| Données Québec | CKAN | REST | `donneesquebec.ca/api/3/` |
| Statistique Canada | WDS | JSON/SDMX | `api.statcan.ca/v1/` |
| NOC / OaSIS | LMI | CSV/XML | Sur demande via ESDC |
| LMIC-CIMT | Data Hub | REST | `lmic-cimt.ca` |
| Open Canada | DCAT | REST | `open.canada.ca/data/api/` |

---

## 4. Format de données

### JSON Feed 1.1

Le flux suit la spécification [JSON Feed 1.1](https://jsonfeed.org/version/1.1) avec une extension personnalisée `_quebec_emploi`.

**Champs standard** :
- `version` : `https://jsonfeed.org/version/1.1`
- `title`, `description`, `language` (`fr-CA`)
- `items[]` : chaque source = un item

**Extension `_quebec_emploi`** (par item) :
```json
{
  "_quebec_emploi": {
    "about": "https://metiers-quebec.org/sources-emploi-quebec.json",
    "source_id": 11,
    "source_nom": "Statistique Canada",
    "source_url": "https://www150.statcan.gc.ca",
    "type_source": "federal",
    "categorie": "statistiques",
    "region": "Quebec",
    "formats_disponibles": ["CSV", "JSON", "XML", "SDMX"],
    "api_disponible": true,
    "derniere_mise_a_jour": "2026-07-23T01:32:43Z"
  }
}
```

### Schéma

`data/feed-schema.json` — JSON Schema draft 2020-12, valide la structure du flux.

---

## 5. Pipeline de build

### `scripts/build-feed.py`

Script Python autonome (aucune dépendance externe).

**Entrée** : `sources-emploi-quebec.json` (16 sources)

**Étapes** :
1. Lecture du catalogue source
2. Pour chaque source avec API : tentative de fetch des métadonnées
3. Pour les sources sans API : items statiques prédéfinis
4. Normalisation en items JSON Feed 1.1
5. Écriture dans `feed/emploi.json`

**Contraintes** :
- SSL : les erreurs `CERTIFICATE_VERIFY_FAILED` dans l'environnement de build ne bloquent pas — les items échoués passent en statiques
- Timeout : 12 secondes par requête
- Aucune dépendance externe (stdlib Python uniquement)

**Usage** :
```bash
python3 scripts/build-feed.py                          # mode standard
python3 scripts/build-feed.py --out feed/emploi.json   # sortie personnalisée
python3 scripts/build-feed.py --quiet                  # sans verbose
```

---

## 6. Accès API / Feed

### URL du flux

```
https://metiers-quebec.org/feed/emploi.json
```

### Content-Type

```
application/feed+json
```

### Auto-discovery

```html
<link rel="alternate" type="application/feed+json"
      href="feed/emploi.json"
      title="Emploi Québec – Flux agrégé">
```

### Sécurité

- **CORS** : restreint par Cloudflare Pages (same-origin par défaut)
- **Cache-Control** : `public, max-age=3600, stale-while-revalidate=86400` recommandé
- **Pas de secrets** : toutes les URLs sont publiques

---

## 7. Visualisation

### `prototype-feed.html`

Page HTML autonome avec :
- Bannière d'intro (gradient, badges)
- Sidebar de filtres (type, catégorie, tags)
- Grille de cartes (badge type, titre, résumé, source, date, tags, formats)
- Recherche temps réel
- Modal détail (description, lien source, ID, formats)
- Responsive (mobile-first)

### `js/feed.js`

Module vanilla JS (389 lignes) :
- Fetch `feed/emploi.json`
- Rendu grille avec filtrage
- Sidebar avec compteurs
- Modal de détail
- Recherche dans titres/résumés/tags

---

## 8. Roadmap

### Fait ✅

- [x] Catalogue `sources-emploi-quebec.json` (16 sources)
- [x] Schéma `data/feed-schema.json`
- [x] Script `scripts/build-feed.py`
- [x] Flux `feed/emploi.json` (15 items)
- [x] Module `js/feed.js`
- [x] Prototype `prototype-feed.html`

### À faire 📋

- [ ] Déploiement Cloudflare Pages (config wrangler.toml)
- [ ] Cron build automatique (mise à jour quotidienne)
- [ ] Miroir RSS/Atom du flux JSON
- [ ] Intégration Données Québec (API CKAN, SSL à résoudre)
- [ ] Intégration Open Canada (API DCAT, SSL à résoudre)
- [ ] Plus de sources (CNESST, RFQ, Ordres professionnels)
- [ ] Dashboard de couverture (% sources actives vs total)
- [ ] Tests automatisés (validation schéma + smoke tests)

---

## 9. Sécurité

- **Sources publiques uniquement** : aucune donnée privée ou authentifiée
- **Pas de secrets** : les URLs et clés API publiques ne sont pas dans le code
- **Rate limiting** : les appels API respectent les timeouts (12s) et les erreurs SSL sont silently fallback
- **Content-Type** : `application/feed+json` (pas `application/json`) pour éviter les confusions MIME

---

## 10. Relation avec Métiers Québec

System C est **indépendant** du projet Métiers Québec (System A/B) mais vit dans le même dépôt :

| Aspect | Métiers Québec (A/B) | System C |
|---|---|---|
| Données | 418 métiers scrapés | 16 sources agrégées |
| Format | HTML statique + graphe | JSON Feed 1.1 |
| Usage | Site web + RAG chatbot | API feed + visualisation |
| Déploiement | Cloudflare Pages | Cloudflare Pages (même config) |

Ils peuvent éventuellement se croiser (le graphe peut consommer le feed), mais pour l'instant ils fonctionnent séparément.
