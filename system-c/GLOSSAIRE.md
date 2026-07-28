# GLOSSAIRE — System C, Couche Atomique

Référence rapide des termes introduits par kb008-bis et son implémentation.
Un terme = une définition courte + où il vit dans le code.

---

## Vocabulaire de base

**FAIT**
Unité atomique de donnée. Un FAIT décrit une seule valeur pour un seul
champ d'un seul métier, avec sa provenance.
```
FAIT = { champ, valeur, origine }
```
Fichier : chaque `data/atomic/{code}.json` contient une liste de FAITS.

**ORIGINE**
Métadonnée de provenance attachée à chaque FAIT. Répond à : d'où vient
cette valeur, quand, comment, avec quelle confiance.
```
ORIGINE = { source, date_captee, methode, confiance, reference? }
```
- `source` : nom de la source (ex. `metiers_quebec`, `imt_en_ligne`)
- `date_captee` : date à laquelle la donnée a été relevée (format `YYYY-MM-DD`)
- `methode` : `scraping` | `manuel` | `api`
- `confiance` : `haute` | `moyenne` | `basse`
- `reference` : URL de la page source consultée (champ optionnel, ajouté
  en Phase 3 pour la traçabilité des sources saisies manuellement)

**CODE**
Identifiant canonique d'un métier. En théorie le code CNP 2021 (ex.
`31301` pour infirmier). En pratique actuellement le **slug**
metiers-quebec.org (ex. `infirmier`), en attendant la résolution du
mapping slug→CNP — voir `code_provisoire` ci-dessous.

**GARDE**
Règle testable automatiquement qui vérifie qu'un ensemble de FAITS
respecte un invariant. Une GARDE retourne toujours
`{ conforme: bool, violations: [...] }`. Vit dans `scripts/gardes.py`.

**completude**
Dictionnaire déclarant explicitement, champ par champ, si une donnée est
présente ou non pour un métier. Empêche le silence — un champ absent doit
être marqué `false`, jamais simplement omis.
```
completude = { "salaire_median": true, "qualites": false, ... }
```

---

## Les 5 GARDES (`scripts/gardes.py`)

| GARDE | Vérifie que... | Détecte typiquement |
|---|---|---|
| `garde_partition` | Aucun `code` n'apparaît deux fois dans le corpus | Doublons entre fiches |
| `garde_autojugement` | Chaque FAIT a une `source` et une `confiance` déclarées | Une source qui s'auto-évaluerait comme fiable sans passer par une résolution externe |
| `garde_non_reecriture` | La `valeur` d'un FAIT recoupe lexicalement le texte brut de sa source | Valeurs inventées, paraphrasées, ou mal étiquetées (ex. `methode:"scraping"` sur une valeur tapée à la main) |
| `garde_irreversibilite` / `garde_irreversibilite_corpus` | Un FAIT existant n'est jamais modifié en place, seulement complété par un nouveau FAIT | Écrasement silencieux de données (ex. deux sections HTML équivalentes fusionnées en un seul FAIT avec une valeur qui écrase l'autre) |
| `garde_completude_explicite` | Chaque champ mentionné dans `faits` apparaît dans `completude`, et vice-versa | Absence non déclarée |

**`est_perimee(fait)`** — pas une GARDE binaire, une fonction dérivée :
calcule si un FAIT a dépassé son seuil de fraîcheur (1 an pour un salaire,
3 ans pour une description) à partir de `date_captee`. Rien n'est stocké,
recalculé à chaque lecture.

---

## Origine théorique (kb008)

**LFA — Langage Formel Abstrait**
Cadre dans lequel les invariants (I) existent indépendamment de tout
substrat (données, code, pensée humaine, activation IA). Les GARDES sont
l'implémentation exécutable des invariants I de kb008-bis dans ce
substrat-ci (Python stdlib) — remplaçables par une autre implémentation
sans changer les invariants eux-mêmes.

**D / L / I / C**
- **D** (données) : les entités et leurs relations — ici, les métiers, les FAITS
- **L** (logique) : les règles qui transforment D — ici, les ingesteurs et `resoudre_conflits.py`
- **I** (invariants) : ce qui doit rester vrai peu importe le substrat — ici, les 5 GARDES
- **C** (contradiction) : une violation prouvée d'un invariant — ce qu'une GARDE détecte

---

## Structure du projet (System C)

**Couche Catalogue**
Métadonnées sur les 16 sources elles-mêmes (`sources-emploi-quebec.json`,
`feed/emploi.json`). Répond à "quelles sources existent".

**Couche Atomique**
Les FAITS extraits *via* ces sources, au niveau du métier
(`data/atomic/{code}.json`). Répond à "que sait-on sur ce métier, et
d'où ça vient". Spécifiée par `docs/kb008-bis.md`.

**`code_provisoire`**
Marqueur (`true`) sur une fiche dont le `code` est un slug
metiers-quebec.org plutôt qu'un vrai code CNP 2021 — solution de repli le
temps que le mapping slug→CNP soit construit (Option B, documentée dans
`docs/PASSATION_BIG_PICKLE.md`, préférée à l'Option A qui bloquait tout
sur un mapping complet des 420 métiers avant de pouvoir tester quoi que
ce soit).

---

## Scripts

| Fichier | Rôle |
|---|---|
| `scripts/gardes.py` | Les 5 GARDES + `est_perimee`, fonctions pures |
| `scripts/test_gardes.py` | Tests unitaires des GARDES sur fixtures synthétiques |
| `scripts/smoke_test_atomique.py` | Valide un corpus entier contre les 5 GARDES, rapport détaillé |
| `scripts/ingest_corpus_raw_v2.py` | Transforme `corpus_raw_v2/{slug}.json` (scraping site A/B) en FAITS |
| `scripts/ingest_imt_manuel.py` | Ingère des FAITS saisis manuellement depuis IMT en ligne (source réelle, curée à la main faute d'API) |
| `scripts/resoudre_conflits.py` | Détecte et résout les conflits entre FAITS concurrents (même `code` + `champ`, sources différentes) par comparaison de `confiance` |
| `data/atomic-fait-schema.json` | Schéma JSON Schema formalisant la structure FAIT/ORIGINE/CODE |

---

*Glossaire créé après clôture de Phase 3 (validation multi-source) —
2026-07-22.*
