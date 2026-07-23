# Passation — validation kb008-bis sur sources-emploi-quebec

Statut : Phase 1 complétée et vérifiée ici (14/14 tests, sandbox isolé).
Phases 2-4 nécessitent le vrai dépôt et n'ont pas pu être exécutées depuis
cet environnement — pas d'accès à `corpus_raw_v2/` ni au dépôt réel.

## Fichiers livrés (à copier dans le dépôt)

- `gardes.py` → `scripts/gardes.py`
- `test_gardes.py` → `scripts/test_gardes.py`
- `atomic-fait-schema.json` → `data/atomic-fait-schema.json`
- `smoke_test_atomique.py` → `scripts/smoke_test_atomique.py`

Tous en stdlib pur — cohérent avec la contrainte déjà en place sur
`build-feed.py` ("aucune dépendance externe"). Aucun `pip install` requis,
donc pas de souci d'environnement NixOS/nix-shell à gérer pour cette phase.

## Ce qui manque avant Phase 2 (bloquant)

**Un mapping slug (metiers-quebec.org) → code CNP 2021 n'existe pas
encore dans le projet.** `corpus_raw_v2/{slug}.json` est indexé par slug
(`infirmier`, `administrateur`...), pas par CNP. kb008-bis suppose ce
mapping résolu. Sans lui, impossible de générer une seule fiche
`data/atomic/{code}.json` réelle.

Deux options, à trancher avant de continuer :
1. Construire le mapping via le Guide MESS "Salaires par profession"
   (516 professions, CNP 2021, déjà cité dans SOURCES.md) — recoupement
   par nom de métier, avec les mêmes techniques multi-variantes que
   SCRAPING.md §5.2 pour les URLs de secteur.
2. Solution de repli temporaire : garder le slug comme `code` provisoire
   en attendant le mapping CNP, avec un champ `code_provisoire: true` —
   permet de tester Phase 2 sans bloquer sur (1).

Recommandation : option 2 pour débloquer immédiatement les tests, option 1
en parallèle comme tâche séparée (ce n'est pas un problème de format, c'est
un problème de données manquantes — ne pas mélanger les deux GARDES).

## Commandes Phase 1 (déjà vérifiées, à revalider dans le vrai dépôt)

```bash
cd scripts/
python3 test_gardes.py -v
# Attendu : "Ran 14 tests in ~0.01s / OK"
```

## Commandes Phase 2 (à exécuter une fois le mapping résolu)

```bash
# 1. Générer 5-10 fiches atomiques réelles depuis corpus_raw_v2
#    (script d'ingestion à écrire — pas fourni ici, dépend du mapping)
python3 scripts/ingest_corpus_raw_v2.py --limit 10 --out data/atomic/

# 2. Smoke test sur cet échantillon
python3 scripts/smoke_test_atomique.py --in data/atomic/
# Attendu : "OK — toutes les GARDES respectées" ou liste précise des échecs
```

## Commandes Phase 3 (conflit multi-source)

Nécessite un deuxième ingesteur (ex. IMT en ligne, statique pour commencer
vu qu'il n'a pas d'API — voir sources-emploi-quebec.json id=3) produisant
un FAIT concurrent pour un `code` déjà couvert par `corpus_raw_v2`. Pas de
script fourni — dépend de la décision sur le mapping CNP (bloquant listé
plus haut).

## Commandes Phase 4 (une fois Phase 2 stable sur l'échantillon)

```bash
python3 scripts/ingest_corpus_raw_v2.py --out data/atomic/   # sans --limit, 420 métiers
python3 scripts/smoke_test_atomique.py --in data/atomic/
```

## Rien à faire côté nix-shell / flake.nix

`gardes.py`, `test_gardes.py`, `smoke_test_atomique.py` n'utilisent que
`json`, `pathlib`, `datetime`, `argparse`, `unittest` — tous stdlib. Le
Python 3.12 déjà utilisé par `build-feed.py` suffit, pas de nouvelle
dépendance à ajouter au `flake.nix`.
