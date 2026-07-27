# Rapport d'audit — branches vs `phase2-systemc`

**Date** : 2026-07-26
**Branche de référence** : `phase2-systemc` (`5f6b09e` — après merge)
**Commande de fetch** : `git fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune`

---

## État final (`git ls-remote origin`, 2026-07-26)

| Branche | SHA | Statut |
|---|---|---|
| `main` | `ebee422` | inchangée |
| `phase2-systemc` | `5f6b09e` | merge kb021 effectué |
| `archive/cnp-sha-check-pending` | `9fb0002` | renommée depuis `experimental/cnp-sha-check` |
| `archive/system-c-tentative-1` | — | supprimée |
| `experimental/cnp-sha-check` | — | supprimée (→ `archive/cnp-sha-check-pending`) |
| `experimental/cnp2021-extraction` | — | supprimée (contenu dans kb021) |
| `experimental/kb021-genome-stability-test` | — | supprimée (mergée dans phase2-systemc) |

---

## Exécution (GO/NO-GO acté Andrei + Claude.ai)

### 1. Suppression `archive/system-c-tentative-1`

Ancêtre strict de `phase2-systemc`, contenu déjà intégré, aucune perte.

```
git push origin --delete archive/system-c-tentative-1
```

✅ Supprimée.

### 2. Renommage `experimental/cnp-sha-check` → `archive/cnp-sha-check-pending`

Pas rejeté sur le fond — couverture opérationnelle insuffisante pour généraliser au-delà du cas infirmier/infirmière auxiliaire (voir kb018, lien Site C). En attente d'un deuxième cas d'usage concret, pas d'un verdict négatif.

```
git push origin origin/experimental/cnp-sha-check:refs/heads/archive/cnp-sha-check-pending
git push origin --delete experimental/cnp-sha-check
```

✅ Renommée. SHA `9fb0002`.

### 3. Merge `kb021-genome-stability-test` dans `phase2-systemc`

0 conflit confirmé par dry-run (audit du 2026-07-26). Superset complet de `cnp2021-extraction` (ancêtre strict, vérifié) — un seul merge couvre les deux branches.

```
SHA avant : 1750d49
git merge --no-ff origin/experimental/kb021-genome-stability-test \
  -m "merge(kb021-genome-stability-test): H4/H4a/H4b, CNP2021 extraction, retrofit 6 KB, contenu SHA-1 hérité de cnp-sha-check"
SHA après : 5f6b09e
```

Résultat : **51 fichiers, 176 649 insertions, 0 conflit**. Push confirmé.

### 4. Nettoyage des branches redondantes

Après confirmation que `git ls-remote origin phase2-systemc` montre `5f6b09e` :

```
git push origin --delete experimental/cnp2021-extraction
git push origin --delete experimental/kb021-genome-stability-test
```

✅ Les deux supprimées. Leur contenu est intégralement dans `phase2-systemc` via le merge.

### 5. Fichiers confirmés sur `phase2-systemc` après merge

```
docs/kb021.md
docs/kb021-bottom-up-second-wave-test.md
docs/kb021-h4b-clustering-test.md
scripts/cnp_sha_check.py
scripts/test_cnp_sha_check.py
```

Tous présents ✅.

---

## Partie B — Analyse détaillée (pré-exécution)

### 1. `archive/system-c-tentative-1`

| Critère | Valeur |
|---|---|
| En avance sur `phase2-systemc` | **0 commits** |
| En retard sur `phase2-systemc` | **20 commits** |
| Dry-run merge | **Déjà à jour** (ancêtre strict de `phase2-systemc`) |

**Verdict : CONTENU DÉJÀ REDONDANT** → Supprimée.

---

### 2. `experimental/cnp-sha-check` (→ `archive/cnp-sha-check-pending`)

| Critère | Valeur |
|---|---|
| En avance sur `phase2-systemc` | **6 commits** (`e186ffc`→`9fb0002`) |
| En retard sur `phase2-systemc` | **2 commits** (gouvernance) |
| Dry-run merge | Non fait (interdit — décision Andrei déjà actée) |
| Contenu unique vs `kb021-genome-stability-test` | **0 fichiers, 0 commits** |

Commits en avance :

```
9fb0002 kb018 - formalisation Couche de notarisation
894c1cc docs: kb017 — expérience cnp_sha_check, résultats comparatifs, conclusion
451cbeb feat(sha): compare_cnp_check_vs_sha.py — backtest out-of-sample 4 catégories
c3b702b test(sha): test_cnp_sha_check.py — 23 tests, 23/23 OK
aa90b39 feat(sha): cnp_sha_check.py — lookup SHA-1 exact, autonome, zéro dépendance cnp_check
e186ffc feat(sha): build_sha_table.py + cnp-sha-table.json (516 CNP, 2352 SHA-1, 0 collision)
```

**Verdict : À ARCHIVER SANS MERGER** → Renommée `archive/cnp-sha-check-pending`.

---

### 3. `experimental/cnp2021-extraction`

| Critère | Valeur |
|---|---|
| En avance sur `phase2-systemc` | **12 commits** (`e186ffc`→`eb6bdca`) |
| En retard sur `phase2-systemc` | **2 commits** (gouvernance) |
| Dry-run merge | **CONFLIT : 0** — merge propre |
| Fichiers qui changeraient | **15 fichiers**, 167 498 insertions |
| Contenu `cnp-sha-check` inclus ? | **Oui** — 6/6 commits identiques, 0 fichier exclusif |

Commits en avance :

```
eb6bdca docs: kb020 — test empirique hypothèse 3 sur corpus de 13 métiers émergents
9b34038 docs: kb019 — désambiguïsation de « Coach IA » et décomposition en fonctions atomiques
307c36a refactor(cnp2021): appellations-index depuis CSV officiel (elements.csv) au lieu du PDF
0183ea4 feat(cnp2021): extract_cnp2021_appellations_index.py — index alphabétique 29169 appellations
afcdae1 feat(cnp2021): extract_cnp2016_to_cnp2021_mapping.py — correspondance CNP 2016→2021 (585 entrées)
96553c5 feat(cnp2021): extract_cnp2021_structure.py — hiérarchie CNP 2021 (822 entrées, 5 niveaux)
9fb0002 kb018 - formalisation Couche de notarisation          ← cnp-sha-check
894c1cc docs: kb017 — expérience cnp_sha_check                ← cnp-sha-check
451cbeb feat(sha): compare_cnp_check_vs_sha.py                ← cnp-sha-check
c3b702b test(sha): test_cnp_sha_check.py                      ← cnp-sha-check
aa90b39 feat(sha): cnp_sha_check.py                            ← cnp-sha-check
e186ffc feat(sha): build_sha_table.py + cnp-sha-table.json     ← cnp-sha-check
```

Fichiers ajoutés (15) :

| Fichier | Lignes | Provenance |
|---|---|---|
| `data/reference/cnp2021-appellations-index.json` | 148 842 | cnp2021-extraction |
| `data/reference/cnp2021-structure.json` | 4 939 | cnp2021-extraction |
| `data/reference/cnp2016-to-cnp2021-mapping.json` | 4 688 | cnp2021-extraction |
| `data/reference/cnp-sha-table.json` | 7 293 | cnp-sha-check |
| `docs/kb017.md` | 169 | cnp-sha-check |
| `docs/kb018.md` | 165 | cnp-sha-check |
| `docs/kb019.md` | 132 | cnp2021-extraction |
| `docs/kb020.md` | 125 | cnp2021-extraction |
| `scripts/build_sha_table.py` | 161 | cnp-sha-check |
| `scripts/cnp_sha_check.py` | 156 | cnp-sha-check |
| `scripts/compare_cnp_check_vs_sha.py` | 388 | cnp-sha-check |
| `scripts/extract_cnp2016_to_2021_mapping.py` | 69 | cnp2021-extraction |
| `scripts/extract_cnp2021_appellations_index.py` | 86 | cnp2021-extraction |
| `scripts/extract_cnp2021_structure.py` | 75 | cnp2021-extraction |
| `scripts/test_cnp_sha_check.py` | 210 | cnp-sha-check |

**Verdict : SUPPRIMÉE** — Contenu intégralement subsumé par `kb021-genome-stability-test`, mergé via celui-ci.

---

### 4. `experimental/kb021-genome-stability-test`

| Critère | Valeur |
|---|---|
| En avance sur `phase2-systemc` | **24 commits** (`e186ffc`→`3f0cdae`) |
| En retard sur `phase2-systemc` | **2 commits** (gouvernance) |
| Dry-run merge | **CONFLIT : 0** — merge propre |
| Fichiers qui changeraient | **53 fichiers**, 176 649 ins., 372 del. |
| Contenu `cnp-sha-check` inclus ? | **Oui** — 6/6 commits, 0 fichier exclusif |
| Contenu `cnp2021-extraction` inclus ? | **Oui** — 12/12 commits (superset) |

Commits uniques (vs `cnp2021-extraction`) :

```
3f0cdae retrofit(kb021): ajout champs état (Mixte : H4a, H4b) + risque résiduel
856c3a8 retrofit(kb020): ajout champs état (Hx) + risque résiduel
c0637e5 retrofit(kb019): ajout champ Type de document (KB)
0f435df retrofit(kb018): ajout champ Type de document (KB)
633adce retrofit(kb013): ajout champs état (Mixte) + risque résiduel
0e401a1 retrofit(kb010): ajout champ Type de document (KB)
95e01e4 feat+docs(kb021): test H4b — clustering TF-IDF/agglomératif, résultat inconclusif
7fedc29 feat(kb021): extract_atomic_functions_corpus.py — 88 fonctions atomiques brutes
bffcdf9 docs(kb021): test bottom-up — deuxième vague de métiers émergents 2026
cd66c49 fix(onet): distinguer 0/0 de inf dans les ratios churn
9e9f5da docs(kb021): test complémentaire CNP2016→CNP2021 — sommet stable
2a06191 feat(cnp): compare_cnp2016_to_cnp2021_structure.py
6ff80ac docs(kb021): rapport test longitudinal O*NET hypothèse 4
2644707 feat(onet): calc_onet_genome_stability.py
6051e9b feat(onet): extract_onet_genome_stability.py
```

Fichiers supplémentaires (vs `cnp2021-extraction`) :

| Fichier | Lignes |
|---|---|
| `data/reference/onet-genome-stability/` (17 JSON + deltas + clustering) | ~30 000 |
| `docs/kb021.md` | — |
| `docs/kb021-bottom-up-second-wave-test.md` | — |
| `docs/kb021-genome-stability-onet-test.md` | — |
| `docs/kb021-h4b-clustering-test.md` | — |
| `data/reference/cnp2016-vs-cnp2021-structure-comparison.json` | — |
| `scripts/calc_onet_genome_stability.py` | — |
| `scripts/extract_onet_genome_stability.py` | — |
| `scripts/extract_atomic_functions_corpus.py` | — |
| `scripts/cluster_atomic_functions.py` | — |
| `scripts/check_kb_states.py` | — |
| `scripts/compare_cnp2016_to_cnp2021_structure.py` | — |
| `docs/kb010-resume-projet.md` | — |
| `docs/kb013-rapport-methodologie.md` | — |

**Verdict : MERGÉE** dans `phase2-systemc` (commit `5f6b09e`). 0 conflit, 51 fichiers, 176 649 insertions.

---

## Synthèse

| Branche | Verdict exécuté | Conflit | Résultat |
|---|---|---|---|
| `archive/system-c-tentative-1` | SUPPRIMÉE | — | `git push origin --delete` ✅ |
| `experimental/cnp-sha-check` | RENOMMÉE | — | → `archive/cnp-sha-check-pending` (`9fb0002`) ✅ |
| `experimental/cnp2021-extraction` | SUPPRIMÉE | — | Contenu dans kb021, mergé via celui-ci ✅ |
| `experimental/kb021-genome-stability-test` | MERGÉE | 0 | `5f6b09e` sur `phase2-systemc` ✅ |

---

## Signallement

**`scripts/cnp_sha_check.py`** est maintenant présent sur `phase2-systemc` via le merge, mais **n'a pas été soumis au durcissement-outils-classification_v0_1.md**. Ce fichier n'est pas validé pour trancher quoi que ce soit — c'est un chantier séparé, non prioritaire, à traiter dans un sprint dédié plus tard. Le merge de l'étape 3 n'implique PAS que `cnp_sha_check.py` soit validé pour trancher quoi que ce soit. Ce point doit être signalé pour ne pas être oublié silencieusement.
