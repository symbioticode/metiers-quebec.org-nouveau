# Rapport d'audit — branches vs `phase2-systemc`

**Date** : 2026-07-26
**Branche de référence** : `phase2-systemc` (`1750d49`)
**Commande de fetch** : `git fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune`

---

## Partie A — Commits pushed sur `phase2-systemc`

| # | SHA | Message |
|---|---|---|
| 1 | `3515a61` | `docs(gouvernance): plan-cloture-hypotheses.md — protocole de clôture des hypothèses` |
| 2 | `1750d49` | `docs(gouvernance): methodologie-agentique-system-c.md — cycle de sprint et rôles agentiques` |

Remote confirmé : `1750d49` = `refs/heads/phase2-systemc` ✅

---

## Partie B — Détail par branche

### 1. `archive/system-c-tentative-1`

| Critère | Valeur |
|---|---|
| En avance sur `phase2-systemc` | **0 commits** |
| En retard sur `phase2-systemc` | **20 commits** |
| Dry-run merge | **Déjà à jour** (ancêtre strict de `phase2-systemc`) |

**Verdict : CONTENU DÉJÀ REDONDANT**

Cette branche est un sous-ensemble strict de `phase2-systemc`. Tout son contenu a déjà été intégré (souvent enrichi). Candidate à suppression pure — aucun merge nécessaire.

---

### 2. `experimental/cnp-sha-check`

| Critère | Valeur |
|---|---|
| En avance sur `phase2-systemc` | **6 commits** (`e186ffc`→`9fb0002`) |
| En retard sur `phase2-systemc` | **2 commits** (gouvernance) |
| Dry-run merge | Non fait (interdit par instruction — décision Andrei déjà actée) |
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

**Verdict : À ARCHIVER SANS MERGER**

Tout le contenu (6 commits, 6 fichiers) est déjà recouvert par `experimental/kb021-genome-stability-test` (6/6 commits présents, 0 fichier exclusif). Renommage proposé :

```bash
git branch -m experimental/cnp-sha-check archive/cnp-sha-check-rejected
```

*(Non exécuté — en attente confirmation.)*

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

**Verdict : MERGE PROPRE POSSIBLE — MAIS ATTENTION**

0 conflit. Contenu non redondant par rapport à `phase2-systemc`. Cependant, les 6 commits `cnp-sha-check` (6 fichiers, ~9 372 lignes) sont inclus dans cette branche. Si la décision est de ne jamais fusionner le contenu SHA-1, un rebase/squash pour exciser ces 6 commits est nécessaire avant merge.

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

**Verdict : MERGE PROPRE POSSIBLE — MAIS ATTENTION**

0 conflit. Contenu non redondant. Superset complet de `cnp2021-extraction` (24 vs 12 commits) et de `cnp-sha-check` (6/6 commits). Si on merge cette branche, tout le contenu SHA-1 est intégré indirectement. Même avertissement que pour `cnp2021-extraction` : rebase/squash nécessaire si on exclut SHA-1.

---

## Synthèse

| Branche | Verdict | Conflit | Fichiers | Action requise |
|---|---|---|---|---|
| `archive/system-c-tentative-1` | CONTENU DÉJÀ REDONDANT | — | 0 | Suppression pure |
| `experimental/cnp-sha-check` | À ARCHIVER SANS MERGER | — | 0 uniques | Renommer → `archive/cnp-sha-check-rejected` |
| `experimental/cnp2021-extraction` | MERGE PROPRE POSSIBLE | 0 | 15 (167k lignes) | **Tri requis** : 6 commits SHA-1 à exciser |
| `experimental/kb021-genome-stability-test` | MERGE PROPRE POSSIBLE | 0 | 53 (176k lignes) | **Tri requis** : 6 commits SHA-1 à exciser |

### Point critique

Les branches `cnp2021-extraction` et `kb021-genome-stability-test` sont des supersets de `cnp-sha-check`. Un merge de l'une ou l'autre intégrerait le contenu SHA-1 qu'on a décidé d'exclure. Si cette décision tient :

- **Option 1** : rebase interactif pour exciser les 6 commits `e186ffc`→`9fb0002` avant merge
- **Option 2** : merger uniquement les fichiers non-SHA-1 (`git checkout <branche> -- <fichiers>`)
- **Option 3** : accepter l'intégration (la décision SHA-1 portait sur cnp-sha-check comme branche isolée, pas sur son contenu noyé dans un superset)

À trancher par Andrei + Claude.ai (synthèse GO/NO-GO, méthodologie §3).
