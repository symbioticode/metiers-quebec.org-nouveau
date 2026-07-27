# kb021 — Test longitudinal externe de l'hypothèse 4 (O*NET, 2003-2026)

Ce document est un test de données, distinct de `docs/kb021.md` (qui reste la
formulation de l'hypothèse elle-même, DRAFT, non modifiée par ce travail). Il
fournit la preuve longitudinale que kb021 identifiait comme manquante :
observer le taux de nouveauté des fonctions atomiques sur plusieurs vagues
réelles dans le temps, en utilisant un référentiel externe déjà longitudinal
(piste explicitement notée dans kb021 : « comparer contre un référentiel
externe déjà longitudinal, ex. O*NET »).

## Méthode

**Source** : O*NET Database releases, https://www.onetcenter.org/db_releases.html
(licence CC BY 4.0, US DOL/ETA). Chaque release publie des fichiers texte
plats incluant :
- **Work Activities / GWA** — ~41 « Generalized Work Activities », le proxy le
  plus proche du concept de « fonction atomique » testé par l'hypothèse 4
  (verbes d'action génériques : « Getting Information », « Analyzing Data or
  Information »...).
- **Task Statements** — ~19 000 tâches granulaires par occupation, la couche
  volatile (équivalent fonctionnel des titres de métiers/tâches).
- **Occupation Data** — les codes O*NET-SOC couverts.

**Échantillonnage** : 17 releases sur les ~55 listées (5.0 à 30.3, avril 2003
à mai 2026), soit environ 1 point par an sur 2003-2015 puis des points
supplémentaires autour des deux révisions majeures connues (transition SOC
2000→2010 entre v10 et v14 ; transition SOC 2010→2018 entre v21 et v23) et
autour de l'apparition/disparition des « Green Task Statements » (v17-v23).
Ce choix priorise l'étalement sur toute la période 2003-2026 plutôt qu'une
couverture dense récente, conformément à la consigne. **Ce n'est pas
exhaustif** : 38 releases sur 55 n'ont pas été extraites — voir « Anomalies et
limites » ci-dessous pour ce que cela implique.

Toutes les 17 releases échantillonnées se sont révélées **téléchargeables**
(200 OK, zips texte) au moment de l'exécution (25/07/2026) via les URLs
`https://www.onetcenter.org/dl_files/db_XX.zip` (releases anciennes) et
`https://www.onetcenter.org/dl_files/database/db_XX_Y_text.zip` (releases
depuis ~v20.1). Aucune release testée n'a été indisponible.

**Scripts** :
- `scripts/extract_onet_genome_stability.py` — télécharge (cache local),
  extrait GWA (IDs+labels complets), compte des tâches, compte des
  occupations par release. Sortie : `data/reference/onet-genome-stability/<version>.json`
  (un par release) + `_combined.json`.
- `scripts/calc_onet_genome_stability.py` — calcule, pour chaque paire de
  releases consécutives échantillonnées, ΔGWA (net et "churn" = ajouts +
  retraits par ID, renommages à ID identique isolés séparément), ΔTasks,
  ΔOccupations, et les ratios |ΔTasks|/churn_GWA et |ΔOccupations|/churn_GWA.
  Sortie : `data/reference/onet-genome-stability/deltas.json` + `deltas.md`.

## Résultats bruts (nombres d'abord)

17 points temporels, 16 périodes.

| Release | Date | GWA | Tasks | Occupations |
|---|---|---|---|---|
| 5.0 | 2003-04 | 41 | 932 | 1166 |
| 6.0 | 2004-07 | 41 | 3222 | 1167 |
| 8.0 | 2005-06 | 41 | 7184 | 1167 |
| 10.0 | 2006-06 | 41 | 10809 | 949 |
| 12.0 | 2007-06 | 41 | 14622 | 949 |
| 14.0 | 2009-06 | 41 | 18361 | 1102 |
| 15.0 | 2010-07 | 41 | 18464 | 1102 |
| 17.0 | 2012-07 | 41 | 19393 | 1110 |
| 19.0 | 2014-07 | 41 | 19493 | 1110 |
| 20.0 | 2015-08 | 41 | 19530 | 1110 |
| 21.0 | 2016-08 | 41 | 19566 | 1110 |
| 22.0 | 2017-08 | 41 | 19612 | 1110 |
| 23.0 | 2018-08 | 41 | 19636 | 1110 |
| 25.0 | 2020-08 | 41 | 19735 | 1110 |
| 27.0 | 2022-08 | 41 | 19265 | 1016 |
| 29.0 | 2024-08 | 41 | 18796 | 1016 |
| 30.3 | 2026-05 | 41 | 18796 | 1016 |

Table complète des deltas par période : `data/reference/onet-genome-stability/deltas.md`
(reproduite intégralement ci-dessous).

| Période | ΔGWA net | ΔGWA churn | ΔTasks | ΔOccupations | ratio Tasks/GWAchurn | ratio Occ/GWAchurn |
|---|---|---|---|---|---|---|
| 5.0 → 6.0 | 0 | 0 | 2290 | 1 | inf | inf |
| 6.0 → 8.0 | 0 | 0 | 3962 | 0 | inf | indéterminé (0/0) |
| 8.0 → 10.0 | 0 | 0 | 3625 | -218 | inf | inf |
| 10.0 → 12.0 | 0 | 0 | 3813 | 0 | inf | indéterminé (0/0) |
| 12.0 → 14.0 | 0 | 0 | 3739 | 153 | inf | inf |
| 14.0 → 15.0 | 0 | 0 | 103 | 0 | inf | indéterminé (0/0) |
| 15.0 → 17.0 | 0 | 0 | 929 | 8 | inf | inf |
| 17.0 → 19.0 | 0 | 0 | 100 | 0 | inf | indéterminé (0/0) |
| 19.0 → 20.0 | 0 | 0 | 37 | 0 | inf | indéterminé (0/0) |
| 20.0 → 21.0 | 0 | 0 | 36 | 0 | inf | indéterminé (0/0) |
| 21.0 → 22.0 | 0 | 0 | 46 | 0 | inf | indéterminé (0/0) |
| 22.0 → 23.0 | 0 | 0 | 24 | 0 | inf | indéterminé (0/0) |
| 23.0 → 25.0 | 0 | 0 | 99 | 0 | inf | indéterminé (0/0) |
| 25.0 → 27.0 | 0 | 0 | -470 | -94 | inf | inf |
| 27.0 → 29.0 | 0 | 0 | -469 | 0 | inf | indéterminé (0/0) |
| 29.0 → 30.3 | 0 | 0 | 0 | 0 | indéterminé (0/0) | indéterminé (0/0) |

**Corrigendum (post-publication)** : une vérification externe a trouvé que
`calc_onet_genome_stability.py` encodait à tort `0.0` pour les périodes où
ΔGWAchurn = 0 ET Δ(Tasks ou Occupations) = 0 simultanément (forme
indéterminée 0/0), en contradiction avec la convention documentée dans le
champ `method` du fichier (qui prévoyait déjà "inf" pour ΔGWAchurn=0 avec
Δ≠0, mais ne traitait pas explicitement le cas Δ=0). Corrigé : ce cas encode
désormais `null` ("indéterminé (0/0)"), distinct des deux autres états
(ratio numérique, `Infinity`). Concrètement : **11 des 16 périodes** sont
indéterminées pour le ratio Occupations (pas 1 seule comme la version
précédente de ce rapport le disait), et **1 période** (29.0 → 30.3) l'est
aussi pour le ratio Tasks — cette dernière période a ΔTasks = 0 ET
ΔOccupations = 0 simultanément (18 796 tâches et 1 016 occupations
identiques entre les deux releases, un plateau réel dans la donnée, pas une
erreur d'extraction). La conclusion du verdict ci-dessous n'est pas
affectée : ΔGWAchurn reste 0 sur les 16 périodes, et ΔTasks est non-nul sur
15 des 16 périodes (la seule exception étant un plateau, pas un contre-
exemple) — le signal central du test (fonctions atomiques figées pendant
que les tâches bougent) est inchangé, seule la métrique secondaire
`ratio_occupations_per_gwa_churn` était mal encodée dans 10 lignes
supplémentaires.

**ΔGWA churn (ajouts + retraits par ID) = 0 sur les 16 périodes**, du premier
au dernier point (2003-2026). Le seul mouvement observé dans la couche GWA
est 6 renommages cosmétiques à ID identique (v25.0 → v27.0), sans ajout ni
retrait :

- `4.A.1.a.2` : « Monitor Processes, Materials, or Surroundings » → « Monitoring... »
- `4.A.1.b.2` : « Inspecting Equipment, Structures, or Material » → « ...Materials »
- `4.A.2.a.1` : « Judging the Qualities of Things, Services, or People » → « ...Objects, Services... »
- `4.A.3.b.1` : « Interacting With Computers » → « Working with Computers »
- `4.A.4.a.3` : « Communicating with Persons Outside Organization » → « ...People Outside the Organization »
- `4.A.4.b.6` : « Provide Consultation and Advice to Others » → « Providing Consultation... »

Aucun de ces changements n'altère le sens de la fonction ; ce sont des
reformulations de style éditorial (temps verbal, singulier/pluriel,
synonyme), pas des créations ou suppressions de fonction.

Pendant la même période, Task Statements varie de 932 (2003) à un pic de
19 735 (2020) puis redescend à 18 796 (2024-2026) — amplitude de plusieurs
milliers de tâches par période sur les premières années (jusqu'à +3 962 entre
deux releases), et Occupations varie entre 949 et 1 167 codes SOC selon les
révisions de la taxonomie SOC elle-même.

## Verdict

Le ratio |ΔTasks|/ΔGWAchurn est **infini** dans 15 des 16 périodes (division
par zéro : le dénominateur, ΔGWA churn, est nul partout ; ΔTasks lui-même
n'est nul que sur la dernière période, 29.0 → 30.3, qui devient indéterminée
0/0). Le ratio |ΔOccupations|/ΔGWAchurn est infini dans seulement 5 des 16
périodes et indéterminé (0/0) dans les 11 autres, car ΔOccupations est
lui-même nul plus souvent que ΔTasks sur cet échantillon (voir corrigendum
ci-dessus) — le signal reste net sur Tasks, plus mitigé sur Occupations.
Ce n'est pas
un artefact du calcul : c'est la donnée elle-même — sur cet échantillon
particulier de 17 releases O*NET couvrant 2003-2026, **le nombre de Work
Activities/GWA n'a jamais changé** (41 tout du long, hors renommages
cosmétiques sans changement d'ID), alors que le nombre de tâches et
d'occupations a fluctué de manière continue et parfois importante.

Au sens strict de la règle fixée en amont de cette tâche (« ratio >>1
consistant sur presque toutes les périodes » = corroboration), le résultat
observé est un cas limite du côté favorable à l'hypothèse : le ratio n'est
pas seulement >>1, il est indéfini par nullité du dénominateur — la couche
GWA n'a tout simplement pas bougé sur toute la fenêtre observée, ce qui est
la version la plus forte possible du signal recherché.

**Cela corrobore la prédiction testable de kb021 sur ce référentiel externe et
cet échantillon de releases : le nombre de fonctions atomiques réellement
nouvelles croît beaucoup plus lentement (dans ce cas : zéro) que le nombre de
titres/tâches, sur 23 ans et 55 versions O*NET (échantillonnées).**

Cette conclusion doit néanmoins être lue avec les limites suivantes,
substantielles, avant d'être généralisée (voir section suivante) — en
particulier le fait qu'O*NET, contrairement à la CNP/aux titres de métiers du
monde réel, **fige délibérément sa liste de GWA par construction
méthodologique** (le modèle de contenu O*NET a été conçu autour d'un nombre
fixe de dimensions génériques dès l'origine) ; ce résultat teste donc la
stabilité *d'un cadre déjà construit pour être stable*, pas la stabilité
spontanée de fonctions atomiques observées dans un corpus de métiers non
pré-structuré (ce que faisait kb020, sur un tout petit échantillon,
avec un résultat plus mitigé).

## Anomalies et limites (à lire avant toute citation de ce document)

- **Échantillonnage, pas exhaustivité** : 17 releases sur ~55 réellement
  listées (2003-2026) ont été extraites — environ 31 %. Toutes les 17
  choisies étaient téléchargeables sans exception ; rien n'indique que les
  38 non extraites auraient donné un résultat différent, mais ce n'est pas
  vérifié. Le choix a favorisé l'étalement (1 point/an + points de révision
  taxonomique) plutôt que la densité récente, par consigne explicite — donc
  potentiellement moins sensible à des changements GWA très locaux dans le
  temps (une modification introduite puis retirée entre deux releases
  échantillonnées ne serait pas détectée).
- **Structure interne des fichiers non stable — gérée, mais à noter** : le
  nom de fichier interne pour les GWA change de `WorkActivity.txt`
  (releases ≤ v8.0) à `Work Activities.txt` (v10.0+) ; celui des tâches de
  `Tasks.txt` (≤ v12.0) à `Task Statements.txt` (v14.0+) ; celui des
  occupations de `onetsoc_data.txt` à `Occupation Data.txt`. Le script gère
  ces variantes par normalisation du nom (voir docstring
  `extract_onet_genome_stability.py`), et aucune anomalie de parsing n'a été
  levée sur les 17 releases (voir `anomalies` vide dans chaque JSON
  individuel et dans `_combined.json`).
- **« Green Task Statements » (v17.0-v23.0)** : un fichier de tâches
  spécifiques à l'économie verte apparaît en v17.0 (1 373 tâches) et
  disparaît après v23.0 (dernière valeur observée : 1 386 en v23.0, absent
  en v25.0+). Ce fichier est compté séparément (`n_green_tasks`) et n'est
  **pas** additionné à `n_tasks` pour ne pas introduire une discontinuité
  artificielle dans la série Tasks — mais cela signifie que le total réel de
  granularité tâches sur cette fenêtre est en fait légèrement plus élevé que
  la colonne ΔTasks ne le montre pour ces 5 releases.
- **Le modèle GWA est par construction figé, pas observé comme stable** :
  contrairement au comptage CNP/titres de métiers, la liste des ~41 GWA fait
  partie de l'architecture originelle du modèle O*NET (le "Content Model")
  et n'est pas censée s'étendre — un ajout de GWA impliquerait une révision
  de fond du modèle lui-même, pas un ajustement de routine. Le résultat "0
  churn" est donc en partie garanti par la conception du référentiel choisi
  comme proxy, ce qui limite la force de la généralisation vers "toute
  fonction atomique de travail est stable" — l'hypothèse 4 teste une
  propriété plus large que ce que ce référentiel particulier peut, par
  construction, réfuter.
- **Transitions SOC 2000→2010 et 2010→2018 non isolées finement** : les
  variations d'Occupations (949 en 2006-2007, 1102-1110 en 2009-2020, 1016
  depuis 2022) reflètent des refontes de la taxonomie SOC elle-même, pas
  uniquement l'apparition de nouveaux métiers — ce document ne distingue pas
  les deux causes (limite reconnue, pas résolue ici).
- **Aucun test statistique formel** : ce document rapporte des comptes et
  ratios bruts, pas un test d'hypothèse avec seuil de significativité — le
  verdict ci-dessus est qualitatif, fondé sur l'ampleur de l'écart observé
  (0 vs milliers), pas sur un calcul de p-value.
- **`docs/kb021.md` n'est pas modifié par ce document** — conformément à la
  consigne, la décision de mettre à jour les questions ouvertes de kb021.md
  à la lumière de ces résultats revient à Andrei, pas à cette tâche.

## Test complémentaire — la CNP montre-t-elle le même patron que O*NET ?

**Question posée** : le résultat O*NET ci-dessus (GWA figées pendant que
Tasks/Occupations bougent de plusieurs ordres de grandeur) pourrait être un
artefact générique de toute hiérarchie à faible cardinalité au sommet — pas
une propriété spécifique aux "fonctions atomiques". Ce test vérifie si le
même patron apparaît dans une hiérarchie n'ayant aucun lien avec O*NET ni
avec une prétention d'atomicité : la Classification nationale des
professions (CNP), en comparant sa seule transition longitudinale
disponible aujourd'hui, CNP2016 v1.0 → CNP2021 v1.0.

**GARDE — une seule transition = un seul point de contraste.** CNP2026
n'est pas publiée avant décembre 2026 : il n'existe qu'un seul intervalle
observable actuellement. Ce qui suit ne permet **pas** de conclure sur un
taux de stabilité de la CNP dans le temps — seulement sur un contraste
ponctuel CNP vs O*NET, sur une fenêtre de temps comparable (2016-2021 pour
la CNP ; le test O*NET couvre 2003-2026).

Script : `scripts/compare_cnp2016_to_cnp2021_structure.py`. Sources :
`data/reference/cnp2021-structure.json` (structure officielle CNP2021, CSV
StatCan) et `data/reference/cnp2016-to-cnp2021-mapping.json` (table de
correspondance code à code, 585 lignes). **Limite de source** : aucun CSV
de structure CNP2016 équivalent au CSV structure CNP2021 n'a été trouvé
dans le repo ni en ligne — seuls les comptes agrégés officiels du sommet
CNP2016 v1.0 (page d'introduction StatCan) ont pu être confirmés (10 grandes
catégories, 40 grands groupes, 140 groupes intermédiaires, 500 groupes de
base). Les libellés exacts des 10 grandes catégories CNP2016 n'ont pas été
vérifiés un à un contre ceux de CNP2021 : seule l'égalité numérique du
sommet est établie ici, pas l'identité de contenu — signalé comme limite,
pas lissé.

### Chiffres bruts

| Niveau | CNP2016 | CNP2021 | Δ |
|---|---|---|---|
| Grande catégorie (sommet) | 10 | 10 | 0 |
| Grand groupe | 40 | 45 | +5 |
| Niveau(x) intermédiaire(s) | 140 (1 niveau) | 89 + 162 (2 niveaux) | non comparable terme à terme |
| Groupe de base (feuille) | 500 | 516 | +16 |

Répartition des 585 lignes de la table de correspondance par type de
changement (une ligne peut porter plusieurs étiquettes GSIM ; classée ici
par la catégorie la plus structurelle qu'elle porte) :

| Type de changement | Lignes |
|---|---|
| Renommage/recodage seul (aucune fusion/scission/transfert) | 429 |
| Transfert (reclassement sans fusion ni scission) | 72 |
| Scission (breakdown / split off) | 68 |
| Fusion (merger / take-over) | 16 |

**Note de lecture** : la quasi-totalité des 585 lignes porte un changement
de code ET un changement de nom (VC1 + VC2), parce que le passage de 4 à 5
chiffres a mécaniquement forcé un recodage de chaque groupe de base — que
son contenu ait changé ou non. Ceci gonfle artificiellement l'apparence de
"tout a changé" si on lit seulement la colonne code ; la colonne
type_changement isole les vrais changements structurels (fusion/scission/
transfert = 156 lignes sur 585, le reste étant recodage/renommage sans
changement de contenu identifiable dans la donnée disponible).

Le CSV de structure CNP2021 (`cnp2021-structure.json`) confirme
indépendamment 45 grands groupes / 89 sous-grands groupes / 162 sous-groupes
/ 516 groupes de base pour la version 2021 — cohérent avec les comptes
dérivés du fichier de mapping.

### Verdict du test complémentaire

**Le sommet de la CNP (grande catégorie, 10 éléments) est resté aussi
stable que les GWA d'O*NET sur cette fenêtre** : 10 → 10, zéro changement
numérique. C'est cohérent avec l'hypothèse que la stabilité observée côté
O*NET n'est pas un artefact isolé — un autre référentiel indépendant, sans
lien de conception avec O*NET, montre la même stabilité à son sommet.

**Mais le changement structurel majeur annoncé par CNP2021 (introduction du
FEER, 5e chiffre) ne se produit PAS au sommet — il se produit aux niveaux
intermédiaires** (1 niveau intermédiaire en 2016 → 2 niveaux distincts en
2021, rendant toute comparaison terme à terme à ce niveau non valide, donc
non tentée ici) et, dans une moindre mesure, à la feuille (500 → 516 groupes
de base, dont 156 changements structurels réels sur 585 lignes de mapping).
Le sommet reste petit et stable ; c'est le milieu et la base de la
hiérarchie qui absorbent le changement de modèle — un patron qui, à ce
stade avec un seul point de données, ressemble à celui d'O*NET (sommet
figé, reste mobile) plutôt qu'à un contre-exemple.

**Ce que ce résultat ne tranche pas** : avec un seul intervalle observé, on
ne peut pas distinguer "toute hiérarchie a un sommet stable par
construction (petite cardinalité = change rarement, presque par
définition mathématique)" de "les fonctions/catégories les plus abstraites
sont intrinsèquement plus stables". Le test reste compatible avec H4a
("le sommet de toute hiérarchie est structurellement stable, indépendamment
du fait qu'il s'agisse de fonctions atomiques ou non") au moins autant
qu'avec H4b ("les fonctions atomiques de travail en particulier ont une
propriété de stabilité au-delà de ce que la taille du sommet expliquerait
seule"). Ce test complémentaire ne permet donc pas de trancher entre H4a et
H4b — il montre seulement que le contraste CNP/O*NET ne va pas dans le sens
qui aurait infirmé H4a (un sommet CNP qui aurait bougé pendant que le
sommet O*NET restait figé aurait été un signal contre la généricité de H4a ;
ce n'est pas ce qu'on observe).

### Anomalies et limites (test complémentaire)

- **Un seul point de données longitudinal** (CNP2016→CNP2021) : aucune
  conclusion sur un taux de stabilité dans le temps n'est possible, ici ou
  ailleurs dans ce document, avec cette seule transition.
- **CNP2016 et CNP2021 ne sont pas structurellement comparables terme à
  terme** : passage de 4 à 5 chiffres, introduction du FEER en
  remplacement du niveau de compétence, et ajout d'un niveau hiérarchique
  entier (sous-grand groupe / sous-groupe distincts là où 2016 n'a qu'un
  "groupe intermédiaire"). Cette difficulté de mapping est documentée
  comme un résultat en soi, pas lissée en forçant une correspondance 1:1
  artificielle.
- **Absence de CSV de structure CNP2016 officiel** : les comptes du sommet
  CNP2016 (10/40/140/500) proviennent d'une page d'introduction StatCan,
  pas d'un fichier structuré comparable au CSV CNP2021 utilisé partout
  ailleurs dans ce projet — une donnée moins fiable que le reste de ce
  rapport, signalée comme telle.
- **`docs/kb021.md` n'est pas modifié par ce test non plus** — la mise à
  jour des questions ouvertes de kb021.md, si elle a lieu, doit attendre
  à la fois ce test ET le test bottom-up (point 2 de la feuille de route),
  et reste une décision d'Andrei.
