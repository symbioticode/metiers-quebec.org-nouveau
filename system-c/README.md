# System C — Sources d'Emploi Québec

> Agrégateur de 16 sources gouvernementales et institutionnelles sur l'emploi, les métiers et la formation au Québec.

**Statut** : Prototype fonctionnel (Couche Catalogue) · Spécification testée (Couche Atomique)
**Version** : 1.1
**Dernière mise à jour** : 2026-07-22

---

## 1. Vue d'ensemble

System C centralise l'accès aux données publiques sur l'emploi au Québec. Il vit dans le même dépôt que Métiers Québec (System A/B) mais fonctionne comme un projet indépendant.

**System C recouvre deux couches distinctes, qui ont longtemps porté le même nom sans être distinguées explicitement :**

| | Couche Catalogue | Couche Atomique |
|---|---|---|
| **Ce qu'elle décrit** | Les 16 sources elles-mêmes — leur URL, leurs formats, leur disponibilité API | Les faits extraits *via* ces sources, au niveau du métier — un salaire, une description, une exigence de formation |
| **Format** | JSON Feed 1.1 (`feed/emploi.json`) | Fiches atomiques par code CNP (`data/atomic/{code}.json`), spec kb008-bis |
| **Statut** | Prototype fonctionnel, déployable | Spécification formalisée et testée (GARDES + schéma), non encore peuplée sur le corpus réel |
| **Sert à** | Découvrir quelles sources existent et comment y accéder | Peupler des fiches métier avec traçabilité de provenance |
| **Documentation** | Ce README, sections 2-7 | `docs/kb008-bis.md` |

La Couche Catalogue est l'index des ingesteurs possibles. La Couche Atomique est ce que ces ingesteurs produisent. La seconde consomme la première — un ingesteur écrit dans `data/atomic/` en citant une source déclarée dans `sources-emploi-quebec.json` — mais les deux ont des cycles de vie, des formats et des critères de succès distincts. Ne pas les fusionner prématurément.

### Pourquoi

- Pas de source unique pour les données emploi au Québec
- Les 16 sources ont des formats, structures et API très hétérogènes
- Besoin d'un point d'entrée unifié pour les chercheurs d'emploi, les organismes d'aide et les développeurs

### Résultat (Couche Catalogue)

- `sources-emploi-quebec.json` : catalogue structuré des 16 sources
- `feed/emploi.json` : flux JSON Feed 1.1 agrégé (15 items, ~18 Ko)
- `prototype-feed.html` : interface web de visualisation

### Résultat (Couche Atomique)

- `docs/kb008-bis.md` : spécification du format (FAIT / GARDE / ORIGINE / CODE)
- `data/atomic-fait-schema.json` : schéma JSON Schema draft 2020-12
- `scripts/gardes.py` : 5 GARDES exécutables, stdlib uniquement
- `scripts/test_gardes.py` : 14 tests unitaires (fixtures synthétiques, validés isolément)
- `scripts/smoke_test_atomique.py` : validation bout-en-bout d'un corpus de fiches
- **Bloquant connu** : mapping slug (metiers-quebec.org) → code CNP 2021 absent. Voir `docs/PASSATION_BIG_PICKLE.md`.

---

## 2. Architecture — Couche Catalogue

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

### Fichiers Couche Catalogue

| Fichier | Taille | Rôle |
|---|---|---|
| `sources-emploi-quebec.json` | 8.9 Ko | Catalogue des 16 sources |
| `scripts/build-feed.py` | 20.8 Ko | Script Python d'agrégation |
| `data/feed-schema.json` | 5.7 Ko | Schéma JSON Feed 1.1 + extension |
| `feed/emploi.json` | 18.8 Ko | Flux généré (15 items) |
| `js/feed.js` | 14.8 Ko | Module JS de visualisation |
| `prototype-feed.html` | 14.0 Ko | Page prototype autonome |

---

## 2bis. Architecture — Couche Atomique

```
┌─────────────────────────┐
│  corpus_raw_v2/{slug}   │  Données source (scraping site A,
│        .json            │  ou tout autre ingesteur déclaré au
└───────────┬─────────────┘  catalogue Couche 1)
            │ ingestion (script à écrire, dépend du mapping CNP)
            ▼
┌─────────────────────────┐
│  data/atomic/{code}     │  Fiche atomique : FAIT + ORIGINE
│        .json            │  par champ, completude explicite
└───────────┬─────────────┘
            │ vérifié par
            ▼
┌─────────────────────────┐
│   scripts/gardes.py     │  GARDE-PARTITION · GARDE-AUTOJUGEMENT
│                          │  GARDE-NON-RÉÉCRITURE · GARDE-IRRÉVERSIBILITÉ
│                          │  GARDE-COMPLÉTUDE-EXPLICITE
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  smoke_test_atomique.py │  Rapport pass/fail, code de sortie
└─────────────────────────┘  non-zéro si une GARDE échoue
```

### Le rôle de traducteur — protocole, pas geste ad hoc

Un invariant formulé en langage naturel (ex. « une source ne fixe jamais elle-même sa propre confiance ») ne descend pas automatiquement dans le code. Il reste au niveau où il est énoncé jusqu'à ce que quelqu'un le traduise en test vérifiable sur données réelles. Ce projet nomme ce rôle explicitement plutôt que de le laisser se redécouvrir à chaque KB :

1. L'invariant s'énonce en langage naturel dans une KB (ex. kb008-bis).
2. Il se traduit en fonction pure dans `gardes.py` — `(données) -> {"conforme": bool, "violations": [...]}`.
3. Il se vérifie d'abord sur fixtures synthétiques (`test_gardes.py`), puis sur un échantillon réel avant extension au corpus complet.
4. Un ingesteur ou un pipeline **applique lui-même** la GARDE avant de rapporter un succès — jamais une validation sur métrique agrégée seule (ex. « le compteur de fiches a augmenté ») sans vérification directe sur les données produites.

Ce protocole s'applique à toute nouvelle GARDE ajoutée à ce projet, pas seulement aux cinq actuelles.

### Fichiers Couche Atomique

| Fichier | Rôle |
|---|---|
| `docs/kb008-bis.md` | Spécification du format et des GARDES |
| `data/atomic-fait-schema.json` | Schéma de validation structurelle |
| `scripts/gardes.py` | GARDES exécutables (stdlib) |
| `scripts/test_gardes.py` | Tests unitaires sur fixtures |
| `scripts/smoke_test_atomique.py` | Validation bout-en-bout d'un corpus |
| `docs/PASSATION_BIG_PICKLE.md` | Bloquants connus et commandes d'exécution |

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

## 4. Format de données — Couche Catalogue

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

### Format de données — Couche Atomique

Voir `docs/kb008-bis.md` pour la spécification complète. Résumé :

```json
{
  "code": "31301",
  "noms": ["Infirmière", "Infirmier"],
  "secteur": "sante",
  "faits": [
    {
      "champ": "salaire_median",
      "valeur": 78000,
      "origine": {
        "source": "isq",
        "date_captee": "2026-05-01",
        "methode": "api",
        "confiance": "haute"
      }
    }
  ],
  "completude": { "salaire_median": true, "qualites": false }
}
```

Schéma : `data/atomic-fait-schema.json`.

---

## 5. Pipeline de build

### `scripts/build-feed.py` (Couche Catalogue)

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

### `scripts/smoke_test_atomique.py` (Couche Atomique)

**Bloquant actuel** : nécessite un script d'ingestion (`ingest_corpus_raw_v2.py`, non encore écrit) qui dépend lui-même d'un mapping slug → code CNP 2021 absent du projet. Voir `docs/PASSATION_BIG_PICKLE.md` pour les deux options envisagées et les commandes exactes une fois débloqué.

```bash
python3 scripts/test_gardes.py -v                      # GARDES isolées, fonctionne déjà
python3 scripts/smoke_test_atomique.py --in data/atomic/  # bout-en-bout, bloqué en attente du mapping
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

### Fait ✅ — Couche Catalogue

- [x] Catalogue `sources-emploi-quebec.json` (16 sources)
- [x] Schéma `data/feed-schema.json`
- [x] Script `scripts/build-feed.py`
- [x] Flux `feed/emploi.json` (15 items)
- [x] Module `js/feed.js`
- [x] Prototype `prototype-feed.html`

### Fait ✅ — Couche Atomique

- [x] Spécification `docs/kb008-bis.md` (FAIT / GARDE / ORIGINE / CODE)
- [x] Schéma `data/atomic-fait-schema.json`
- [x] `scripts/gardes.py` — 5 GARDES exécutables
- [x] `scripts/test_gardes.py` — 14 tests unitaires validés (fixtures synthétiques)
- [x] `scripts/smoke_test_atomique.py` — écrit, non encore exécuté sur données réelles

### À faire 📋 — Couche Catalogue

- [ ] Déploiement Cloudflare Pages (config wrangler.toml)
- [ ] Cron build automatique (mise à jour quotidienne)
- [ ] Miroir RSS/Atom du flux JSON
- [ ] Intégration Données Québec (API CKAN, SSL à résoudre)
- [ ] Intégration Open Canada (API DCAT, SSL à résoudre)
- [ ] Plus de sources (CNESST, RFQ, Ordres professionnels)
- [ ] Dashboard de couverture (% sources actives vs total)

### À faire 📋 — Couche Atomique

- [ ] **Bloquant** : mapping slug metiers-quebec.org → code CNP 2021
- [ ] Script d'ingestion `corpus_raw_v2` → `data/atomic/`
- [ ] Validation Phase 2 sur échantillon réel (5-10 métiers)
- [ ] Test de conflit multi-source (Phase 3 — ex. ISQ vs metiers-quebec.org)
- [ ] Extension au corpus complet (420 métiers, Phase 4)

### Question ouverte — non tranchée, à décider avant d'aller plus loin

**Est-ce qu'une couche de requête sémantique (interrogation en langage naturel des fiches atomiques) fait partie du contenu C à préserver, ou est-ce une couche ajoutée avec ses propres critères de succès, indépendants de la fidélité de migration ?**

Tant que cette question n'est pas tranchée, deux chantiers restent explicitement hors scope de System C : la détection de requêtes hors-corpus (Δ sémantique, documenté dans kb011 §4 pour site A/B) et les tests de non-régression sémantique. Les introduire maintenant durcirait un composant qui n'existe pas encore ici — à réévaluer si et quand une couche de requête est ajoutée à System C.

---

## 9. Sécurité

- **Sources publiques uniquement** : aucune donnée privée ou authentifiée
- **Pas de secrets** : les URLs et clés API publiques ne sont pas dans le code
- **Rate limiting** : les appels API respectent les timeouts (12s) et les erreurs SSL sont silently fallback
- **Content-Type** : `application/feed+json` (pas `application/json`) pour éviter les confusions MIME

---

## 10. Relation avec Métiers Québec

System C est **indépendant** du projet Métiers Québec (System A/B) mais vit dans le même dépôt :

| Aspect | Métiers Québec (A/B) | System C — Catalogue | System C — Atomique |
|---|---|---|---|
| Données | 418 métiers scrapés | 16 sources agrégées | Faits par métier, multi-source |
| Format | HTML statique + graphe | JSON Feed 1.1 | Fiches CNP, spec kb008-bis |
| Usage | Site web + RAG chatbot | API feed + visualisation | Source de vérité pour toute reconstruction future |
| Déploiement | Cloudflare Pages | Cloudflare Pages (même config) | Non déployé — format en validation |

La Couche Atomique peut à terme consommer `corpus_raw_v2` (System A/B) comme un ingesteur parmi d'autres — ce n'est pas une migration de A/B vers C, c'est C qui absorbe A/B comme une source déclarée au même titre que les 16 autres.
