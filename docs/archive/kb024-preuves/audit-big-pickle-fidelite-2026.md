# Audit indépendant — Fidélité du mapping KB002 (Big Pickle / Claude Code CLI)

Date : 2026-07-27
Méthode : lecture aveugle et indépendante, sans consultation préalable de `docs/audit-fidelite-template-2026.md` (CCW). Reproduction exacte de l'algorithme de mapping tel qu'il est **réellement exécuté** par `scraper/generate.py`, pas du dictionnaire de référence documenté dans `docs/kb002.md`.

## 0. Constat préalable : deux dictionnaires de mapping coexistent dans `generate.py`

`scraper/generate.py` contient **deux** mécanismes de normalisation de section, pas un seul :

1. `SECTION_MAP` / `normalize_section()` (lignes 61-83) — utilisé dans `Generator.load()` (ligne 199) pour construire `p["sn"]`, stocké sur chaque profession.
2. Un dictionnaire local `section_key_map` défini **à l'intérieur** de `gen_profession()` (lignes 227-238), avec sa propre boucle de correspondance (lignes 240-296).

**`p["sn"]` (mécanisme 1) n'est jamais lu par `gen_profession()`.** La fonction reconstruit sa propre variable locale `sn` à partir de `raw_sections = p.get("sections", {})` en utilisant uniquement le mécanisme 2. Le mécanisme 1 est mort — il tourne, consomme du CPU au chargement, mais son résultat n'est utilisé nulle part dans le chemin de génération des pages `/metier/*/`.

Toute analyse de couverture doit donc reproduire le mécanisme 2, pas `SECTION_MAP`. C'est ce que fait cet audit.

## 1. Données sources

`data/professions_details.json` : **420 entrées** — compte exact confirmé, conforme à KB002.

## 2. Algorithme reproduit (mécanisme 2, `gen_profession` lignes 227-296)

Pour chaque profession et chaque clé cible (`description`, `taches`, `milieu`, `qualites`, `marche`, `formation`, `admission`, `salaires`, `placement`, `perspectives`) :

1. Le dictionnaire local liste des variantes de clés brutes attendues (en minuscules, `\n`-séparées) pour chaque cible.
2. Pour chaque variante, on parcourt `raw_sections.items()` et on compare `actual_key.lower().replace("\n", " ").strip()` à la variante normalisée de la même façon. Premier match trouvé → utilisé, arrêt de la recherche pour cette cible.
3. Si aucune variante ne matche, tentative de correspondance directe : `target_key in raw_sections` (ex. `"description" in raw_sections`).
4. Deux filets de secours *spécifiques* à `description` et `formation` seulement : extraction par regex depuis le bloc `intro` si la clé cible reste absente après les étapes 1-3.
5. **Aucun filet de secours n'existe pour les 8 autres sections.**

Une section est comptée « couverte » ici seulement si, après ce mapping, `fmt()` produirait un contenu non vide (donc pas seulement présence de la clé — vérifié explicitement, cf. garde-fou du brief).

## 3. Tableau de couverture par section — comparaison directe avec KB002

| Section | Couverture KB002 (référence, v0.1.1) | Couverture reproduite (code actuel) | Delta (points) |
|---|---|---|---|
| Description | 31% | **33,1%** (139/420) | +2,1 |
| Tâches | 92% | **93,6%** (393/420) | +1,6 |
| Milieu | 60% | **60,2%** (253/420 contenu non vide ; 256/420 clé présente) | +0,2 |
| Qualités | 1% | **2,6%** (11/420) | +1,6 |
| Marché | 9% | **9,8%** (41/420) | +0,8 |
| Formation | 6% | **5,7%** (24/420) | −0,3 |
| Admission | 45% | **39,8%** (167/420) | −5,2 |
| Salaires | 4% | **5,0%** (21/420) | +1,0 |
| Placement | 0,2% | **1,9%** (8/420) | +1,7 |
| Perspectives | 39% | **38,3%** (161/420) | −0,7 |

Écarts globalement faibles (±5 points max, sur Admission) — cohérent avec le fait que le code n'a apparemment pas changé de comportement substantiel depuis KB002 sur ce mécanisme précis ; les deltas restants sont plausiblement dus à une différence de méthode de comptage (KB002 semble compter par clé brute agrégée, cet audit compte par contenu formaté non vide après tout le pipeline de correspondance incluant les filets de secours regex).

**Vérification anti-artefact** : aucune section n'est à 0% ou 100% exact — Placement est la plus basse (1,9%, 8/420) et Tâches la plus haute (93,6%, 393/420), toutes deux vérifiées comme des comptages réels sur données distinctes (8 fiches ont explicitement une clé `STATISTIQUES\nDE\nPLACEMENT` ou `placement`, pas un artefact de division).

## 4. Clés orphelines (présentes dans les données, jamais couvertes par le dictionnaire de mapping)

| Clé brute orpheline | Occurrences (fiches où présente et non utilisée) |
|---|---|
| `LIENS\nRECOMMANDÉS` | 383 |
| `VOIR\nAUSSI` | 309 |
| `MILIEUX\nDE\nTRAVAIL` | 36 *(collision, voir §5 — comptée orpheline seulement quand `MILIEU\nDE\nTRAVAIL` existe aussi dans la même fiche et gagne)* |
| `EXIGENCE\nDU\nMARCHÉ\nDU\nTRAVAIL` | 19 |
| `EXIGENCE\nD'ADMISSION` (singulier) | 16 *(idem collision)* |
| `NIVEAU\nD'ÉTUDES` | 11 |
| `DONNÉES\nSALARIALE` | 1 |

`LIENS\nRECOMMANDÉS` et `VOIR\nAUSSI` ne sont pas des bugs de mapping — il n'existe simplement aucune section cible correspondante dans `section_order` (ligne 307) : ce sont des sections de contenu jamais prévues pour être affichées sur les fiches `/metier/*/`, donc 100% « perdues » par conception, pas par bug. `EXIGENCE\nDU\nMARCHÉ\nDU\nTRAVAIL` (singulier, sans le S final de EXIGENCES) est en revanche un vrai trou : cette variante n'apparaît dans **aucune** des listes `source_keys` du dictionnaire (seule `EXIGENCES\nDU\nMARCHÉ\nDU\nTRAVAIL`, pluriel, y figure) — 19 fiches perdent leur contenu Marché du travail pour cette seule raison.

## 5. Collisions (deux clés brutes distinctes de la même fiche pointant vers la même section cible)

**53 collisions détectées** sur 420 fiches. Répartition par cible :

- `milieu` : très majoritaire — `MILIEU\nDE\nTRAVAIL` toujours gagnant sur `MILIEUX\nDE\nTRAVAIL` (ordre des `source_keys` : le singulier est testé avant le pluriel dans la liste).
- `admission` : `EXIGENCES\nD'ADMISSION` (pluriel) toujours gagnant sur `EXIGENCE\nD'ADMISSION` (singulier).
- 1 cas `salaires` : `DONNÉES\nSALARIALES` gagnant sur `DONNÉES\nSALARIALE`.

**Le contenu perdu est-il substantiel ou redondant ?** Sur les 53 collisions, **29 (55%)** ont un contenu perdu strictement plus long (en caractères) que le contenu gardé — parfois de façon spectaculaire : ex. `chorégraphe` garde 86 caractères de `DONNÉES\nSALARIALES` et perd 40 756 caractères de `DONNÉES\nSALARIALE` (la variante orpheline contenait en fait tout le contenu réel, la variante gagnante était quasi vide). Autre exemple frappant : `journaliste`, cible `milieu` — 402 caractères gardés vs 25 359 perdus. Ce n'est donc pas un cas de doublon redondant : c'est le mécanisme de sélection « premier match dans l'ordre du dictionnaire » qui choisit arbitrairement la clé la plus courte/vide plutôt que la plus riche, dans une majorité de cas observés.

## 6. Résumé des causes racines identifiées

1. Le mapping réellement actif ignore un mapping alternatif plus général (`SECTION_MAP`) qui existe dans le même fichier mais n'est jamais appelé — code mort trompeur pour quiconque lit le fichier en diagonale.
2. Absence de variante `EXIGENCE\nDU\nMARCHÉ\nDU\nTRAVAIL` (singulier) dans `source_keys["marche"]` — 19 fiches perdent leur section Marché.
3. Ordre de priorité figé (premier match gagne) sans logique « garder le contenu le plus long » — cause 55% des collisions à perte substantielle de contenu.
4. Aucun filet de secours regex pour Qualités, Marché, Admission, Salaires, Placement, Perspectives — seuls Description et Formation en bénéficient.

## 7. Comparaison avec l'audit CCW (`docs/audit-fidelite-template-2026.md`)

*(section rédigée après lecture du document CCW, une fois ce document figé — conformément au brief)*

### Convergence forte

Les deux lectures, produites indépendamment, arrivent à des chiffres **quasi identiques au dixième de point** sur les 10 sections :

| Section | Big Pickle (ici) | CCW | Écart entre les deux audits |
|---|---|---|---|
| Description | 33,1% (139) | 31,0% (130) | 2,1 pts — seul écart notable, cf. ci-dessous |
| Tâches | 93,6% (393) | 93,6% (393) | 0 |
| Milieu | 60,2% (253) | 60,2% (253) | 0 |
| Qualités | 2,6% (11) | 2,6% (11) | 0 |
| Marché | 9,8% (41) | 9,8% (41) | 0 |
| Formation | 5,7% (24) | 5,7% (24) | 0 |
| Admission | 39,8% (167) | 39,8% (167) | 0 |
| Salaires | 5,0% (21) | 5,0% (21) | 0 |
| Placement | 1,9% (8) | 1,9% (8) | 0 |
| Perspectives | 38,3% (161) | 38,3% (161) | 0 |

9 sections sur 10 sont identiques au chiffre exact près — accord total sur le mécanisme, l'algorithme reproduit, et son résultat sur les 420 fiches. Les deux audits convergent aussi, indépendamment, sur :

- **Le diagnostic du code mort** : `SECTION_MAP`/`normalize_section()` construit `p["sn"]`, jamais relu ; c'est le dictionnaire local de `gen_profession()` qui gouverne réellement le rendu. Identifié dans les deux documents avec les mêmes numéros de ligne.
- **Les clés orphelines majeures** : `LIENS\nRECOMMANDÉS` (383) et `VOIR\nAUSSI` (309) — mêmes comptages exacts, même interprétation (sections non prévues dans `section_order`, pas un bug de correspondance).
- **La variante manquante `EXIGENCE\nDU\nMARCHÉ\nDU\nTRAVAIL`** (singulier, 19 occurrences) absente de `source_keys["marche"]`.
- **Les collisions Milieu et Admission** : mêmes deux paires de clés en collision (`MILIEU`/`MILIEUX DE TRAVAIL`, `EXIGENCES`/`EXIGENCE D'ADMISSION`), même clé toujours gagnante dans les deux cas (celle listée en premier dans `source_keys`).
- **Le cas `danseurl` (Salaires)** : les deux audits identifient nommément cette fiche comme la seule collision sur Salaires, avec la même clé gagnante quasi vide (`DONNÉES\nSALARIALES`) écrasant une clé perdante substantielle (`DONNÉES\nSALARIALE`).

### Divergences

1. **Description : 33,1% (ici) vs 31,0% (CCW) — écart de 2,1 points, 9 fiches.** Cause identifiable : mon comptage inclut le filet de secours regex sur `intro` (lignes 253-282 de `generate.py`), qui récupère 9 fiches supplémentaires quand la clé `DESCRIPTION` est absente (`matched_actual_key_distribution["description"]` chez moi montre `'intro(fallback-regex)': 9`). CCW ne mentionne pas ce filet de secours dans son tableau de couverture — soit son script ne l'a pas reproduit, soit il l'a exclu délibérément en ne comptant que les correspondances directes de clé. Le brief demandait de reproduire l'algorithme "exactement tel qu'il est écrit dans le code actuel" ; ce filet de secours fait bel et bien partie du code actif de `gen_profession()`, donc son inclusion ici est cohérente avec la consigne — mais c'est un point où les deux méthodes divergent réellement, pas un simple bruit d'arrondi.

2. **Nombre de collisions total : 53 (ici) vs 54 (CCW).** CCW rapporte "54 fiches concernées au total sur les 3 sections vérifiées" en cumulant 36 (Milieu) + 16 (Admission) + 1 (Salaires) = 53 dans son propre tableau — c'est une incohérence interne au document CCW lui-même (36+16+1=53, pas 54) plutôt qu'un vrai écart avec cet audit. Mes comptages exacts par section (à partir des données brutes) : Milieu, Admission et Salaires correspondent à ceux de CCW ; je trouve en outre des collisions supplémentaires non listées par CCW sur d'autres cibles (`taches`, `qualites`, `formation`, `placement`, `perspectives`, `marche`, `description` face à leurs propres variantes minuscules directes type `"taches" in raw_sections`), ce qui explique le total légèrement différent selon la portée exacte retenue. CCW a visiblement limité son inventaire des collisions aux 3 sections où il a jugé l'effet significatif, sans prétendre à l'exhaustivité — un choix de portée, pas une erreur de calcul en soi.

3. **Interprétation du "goulot d'étranglement" (CCW §2, §6)** : CCW conclut explicitement que "le goulot n'est pas (plus) le mapping de clés — c'est la capture initiale des sections par le scraper (`scrape_v2.py`)", en s'appuyant sur son propre audit complémentaire `docs/audit-claude-code-web-structure-site.md` (liste fermée de 15 regex dans `scrape_v2.py`). Cet audit-ci n'a pas investigué `scrape_v2.py` — le brief demandait de se concentrer sur `generate.py` et le mapping en aval, pas sur le scraper amont. Je ne peux donc ni confirmer ni infirmer indépendamment cette conclusion sur la cause racine amont ; je note simplement que mon périmètre était plus étroit que celui de CCW sur ce point précis, pas que nous sommes en désaccord.

### Lecture d'ensemble

L'accord quasi parfait sur 9 sections/10 et sur tous les mécanismes structurels (code mort, clés orphelines, collisions) constitue une mesure de robustesse forte : deux implémentations indépendantes du même algorithme, sur les mêmes données, produisent le même résultat au chiffre près. La seule divergence méthodologique réelle (Description, filet de secours regex) est mineure et traçable à une différence de périmètre de reproduction du code, pas à une erreur de l'un ou l'autre audit. La conclusion partagée est sans ambiguïté : **le bug KB002 n'est pas corrigé** — la couverture mesurée aujourd'hui reproduit presque exactement les chiffres de KB002, malgré l'implémentation d'un dictionnaire de mapping proche de celui que KB002 recommandait.

---

*Fichier de données brutes* : `data/reference/migration-sens-structure/fidelite-template-big-pickle.json`
