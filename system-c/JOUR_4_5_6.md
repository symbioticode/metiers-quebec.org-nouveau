Plan finalisé — Jour 4, 5, 6 (Couche Atomique)

Suite du plan initial (Jour 1-3, Couche Catalogue — désormais fait ✅,
voir arborescence ci-dessous marquée). Ce plan couvre exclusivement la
Couche Atomique (kb008-bis) : format FAIT/GARDE/ORIGINE/CODE, tests,
ingestion. La Couche Catalogue n'est pas retouchée.

Structure des fichiers

62_FREE/
├── sources-emploi-quebec.json
├── data/
│   ├── feed-schema.json
│   ├── atomic-fait-schema.json      [NOUVEAU]
│   └── atomic/                      [NOUVEAU]
│       └── {code}.json
├── scripts/
│   ├── build-feed.py
│   ├── gardes.py                    [NOUVEAU]
│   ├── test_gardes.py               [NOUVEAU]
│   ├── smoke_test_atomique.py       [NOUVEAU]
│   └── ingest_corpus_raw_v2.py      [A ECRIRE — Jour 5-6]
├── docs/
│   ├── kb008-bis.md                 [NOUVEAU]
│   └── PASSATION_BIG_PICKLE.md      [NOUVEAU]
├── feed/
│   └── emploi.json
├── prototype-feed.html
├── js/
│   └── feed.js
└── css/
    └── style.css

`[NOUVEAU]` = ajouté ce sprint · `[A ECRIRE]` = pas encore créé · sans marque = fait au Jour 1-3, inchangé.

### Détail des nouveaux fichiers

| Fichier | Rôle |
|---|---|
| `data/atomic-fait-schema.json` | Schéma JSON Schema draft 2020-12 pour les fiches FAIT/ORIGINE/CODE |
| `data/atomic/{code}.json` | Une fiche par code CNP, générée à l'ingestion. 0 fichier tant que le mapping slug→CNP n'est pas résolu — voir bloquant Jour 5 |
| `scripts/gardes.py` | 5 GARDES exécutables (stdlib) : `garde_partition`, `garde_autojugement`, `garde_non_reecriture`, `est_perimee`, `garde_irreversibilite`, `garde_completude_explicite` |
| `scripts/test_gardes.py` | 14 tests unitaires, fixtures synthétiques, validés isolément |
| `scripts/smoke_test_atomique.py` | Validation bout-en-bout d'un corpus de fiches (CLI `--in` / `--quiet`) |
| `scripts/ingest_corpus_raw_v2.py` | À écrire (Jour 5-6) — bloqué sur le mapping CNP |
| `docs/kb008-bis.md` | Spécification du format |
| `docs/PASSATION_BIG_PICKLE.md` | Bloquants connus + commandes d'exécution |

Étapes d'implémentation

Jour 4 — Copier les livrables déjà écrits et vérifiés

1. data/atomic-fait-schema.json — copier tel quel depuis les fichiers livrés
   (déjà validé : JSON syntaxiquement correct, structure FAIT/ORIGINE conforme
   à kb008-bis)

2. scripts/gardes.py — copier tel quel (stdlib uniquement : json, pathlib,
   datetime, argparse — rien à ajouter au flake.nix)

3. scripts/test_gardes.py — copier tel quel, puis exécuter :
   ```
   cd scripts/
   python3 test_gardes.py -v
   ```
   Attendu : `Ran 14 tests in ~0.01s` / `OK`. Si un test échoue ici, ne pas
   avancer au Jour 5 — les GARDES doivent être stables sur fixtures avant
   de toucher au corpus réel.

4. scripts/smoke_test_atomique.py — copier tel quel. Ne pas encore exécuter
   (aucune fiche dans data/atomic/ à ce stade — voir bloquant Jour 5)

5. docs/kb008-bis.md et docs/PASSATION_BIG_PICKLE.md — copier tel quel

Jour 5 — Résoudre le bloquant : mapping slug → code CNP

corpus_raw_v2/{slug}.json (System A/B) est indexé par slug
(infirmier, administrateur...), pas par CNP 2021. kb008-bis exige le CNP
comme clé canonique. Sans ce mapping, aucune fiche atomique réelle ne peut
être générée.

Décision à prendre avant d'écrire ingest_corpus_raw_v2.py — deux options,
non exclusives dans le temps :

  Option A (mapping définitif) — recouper les 420 slugs contre le Guide
  MESS "Salaires par professions" (516 professions, CNP 2021, déjà cité
  dans SOURCES.md), avec les mêmes techniques multi-variantes que
  SCRAPING.md §5.2 (correspondance par nom normalisé, gestion des
  appellations alternatives)

  Option B (repli temporaire, débloque immédiatement) — utiliser le slug
  comme `code` provisoire avec un champ `code_provisoire: true` dans la
  fiche, le temps que l'Option A soit traitée séparément

Recommandation : Option B pour ne pas bloquer le Jour 6, Option A en tâche
parallèle distincte — ce n'est pas un problème de format, c'est un problème
de données manquantes, à ne pas mélanger avec les GARDES elles-mêmes.

Jour 6 — Écrire l'ingesteur et valider sur échantillon réel

6. scripts/ingest_corpus_raw_v2.py — nouveau script, stdlib uniquement :
   - lit corpus_raw_v2/{slug}.json
   - applique le mapping (Option A ou B du Jour 5)
   - produit un FAIT par section normalisée (description, taches, salaires...)
     avec origine.source="metiers_quebec", origine.methode="scraping",
     origine.confiance="moyenne" (donnée brute non vérifiée par une
     source officielle — cf. GARDE-AUTOJUGEMENT, la confiance n'est jamais
     fixée à "haute" par l'ingesteur lui-même)
   - écrit data/atomic/{code}.json
   - respecte GARDE-IRRÉVERSIBILITÉ : n'écrase jamais un FAIT existant en
     place, ajoute uniquement

   Commande de test, échantillon limité d'abord :
   ```
   python3 scripts/ingest_corpus_raw_v2.py --limit 10 --out data/atomic/
   ```

7. Smoke test sur l'échantillon :
   ```
   python3 scripts/smoke_test_atomique.py --in data/atomic/
   ```
   Attendu : `OK — toutes les GARDES respectées`, ou liste précise des
   violations à corriger avant d'étendre au corpus complet.

8. Si Jour 6 étape 7 passe : extension au corpus complet (420 métiers,
   sans --limit). Sinon : corriger l'ingesteur ou le mapping, revalider
   sur l'échantillon avant de scaler — ne jamais lancer sur 420 métiers
   avant que l'échantillon soit propre.

Ordre d'exécution

1. data/atomic-fait-schema.json
2. scripts/gardes.py
3. scripts/test_gardes.py  (python3 scripts/test_gardes.py -v)
4. scripts/smoke_test_atomique.py
5. docs/kb008-bis.md, docs/PASSATION_BIG_PICKLE.md
6. Décision mapping CNP (Option A ou B)
7. scripts/ingest_corpus_raw_v2.py  (à écrire)
8. python3 scripts/ingest_corpus_raw_v2.py --limit 10 --out data/atomic/
9. python3 scripts/smoke_test_atomique.py --in data/atomic/
10. Si succès sur échantillon → extension aux 420 métiers, sinon retour à 7

Ce que ce plan ne couvre pas

La couche de requête sémantique (Δ sémantique kb011 §4, tests de
non-régression sémantique) reste hors scope — question ouverte non
tranchée dans le README (section 8). Rien dans Jour 4-5-6 ne présuppose
une réponse à cette question.
