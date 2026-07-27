# Audit fidélité template 2026 — le bug KB002 est-il corrigé aujourd'hui ?

**Horodatage :** 2026-07-27, ~06:30–07:15 UTC.
**Branche :** `experimental/kb0XX-migration-sens-structure` (travail local, non
poussé — voir note de statut en tête).
**Source vérifiée directement :** `docs/kb002.md` (lu intégralement avant
d'écrire ce document — pas de résumé d'un résumé, conformément au
garde-fou du brief révisé v2).

## Note de statut (avant tout résultat)

Au moment de la rédaction, `origin/experimental/kb0XX-migration-sens-structure`
n'existe pas sur le remote (vérifié par `git fetch` + `git ls-remote --heads
origin` juste avant ce travail). Andrei a confirmé attendre que Big Pickle
pousse en premier ; ce document est donc produit sur une branche locale
temporaire, committé mais **pas poussé**, en attendant que la branche
canonique apparaisse sur origin.

## Question posée, reformulée précisément

KB002 a mesuré, sur `data/professions_details.json` (420 métiers), la
couverture de 10 sections cibles après passage par le mapping de clés du
pipeline de génération. Le mécanisme identifié : le scraper stocke les
titres de section en majuscules avec des `\n` internes (`part.upper().strip()`
sur un texte déjà `\n`-joint mot par mot), et sans dictionnaire de
correspondance complet, ces clés restent invisibles au générateur.

**Question de cet audit** : ce mécanisme est-il toujours actif aujourd'hui,
avec quelle couverture réelle par section, et quelles clés brutes restent
orphelines (non mappées) ?

## Méthode — reproduction exacte, pas une nouvelle méthode

1. Chargé `data/professions_details.json` tel quel sur cette branche : **420
   entrées**, même total que KB002 (pas d'écart de taille de corpus à
   signaler).
2. Localisé le mécanisme de mapping **actuellement utilisé pour générer les
   pages** : `scraper/generate.py`, fonction `gen_profession()` (lignes
   227–251), dictionnaire local `section_key_map` — **pas** le `SECTION_MAP`
   global (ligne 61) ni `normalize_section()` (ligne 78), qui existent dans
   le fichier mais ne sont utilisés que dans `Generator.load()` pour
   construire un attribut `p["sn"]` — voir §5, cet attribut n'est jamais lu
   ailleurs dans le fichier après sa construction ; c'est `gen_profession()`
   qui reconstruit sa propre normalisation locale et c'est elle qui
   détermine ce qui apparaît réellement sur les pages générées.
3. Reproduit l'algorithme de `section_key_map` **exactement tel qu'il est
   écrit dans le code actuel** (comparaison insensible à la casse et aux
   `\n`, priorité au premier match trouvé) pour chaque profession, sur les
   mêmes 10 sections que KB002.
4. Compté une section comme « couverte » uniquement si elle a un contenu
   **non vide** après mapping (fail-loud : ne pas confondre « la clé brute
   existe dans le JSON » avec « du contenu réel est mappé » — voir le cas
   `EXIGENCES D'ADMISSION` en §4, où 183 occurrences de clés brutes
   produisent seulement 167 professions avec contenu non vide après
   mapping — l'écart est fait de clés présentes mais vides).
5. Script utilisé (reproductible, joint en annexe du dépôt) :
   `data/reference/migration-sens-structure/fidelite-template.json` contient
   la sortie brute complète, y compris chaque clé brute et son décompte
   exact.

## 1. Tableau de couverture — comparaison directe avec KB002

| Section | KB002 (baseline) | Aujourd'hui (compte / 420) | Aujourd'hui (%) | Delta |
|---|---|---|---|---|
| Description | 31% | 130 | 31.0% | **−0.05 pts (stagnation)** |
| Tâches | 92% | 393 | 93.6% | +1.6 pts (stagnation, bruit) |
| Milieu | 60% | 253 | 60.2% | +0.2 pts (stagnation) |
| Qualités | 1% | 11 | **2.6%** | +1.6 pts (stagnation — toujours quasi nul) |
| Marché | 9% | 41 | 9.8% | +0.8 pts (stagnation) |
| Formation | 6% | 24 | 5.7% | −0.3 pts (stagnation) |
| Admission | 45% | 167 | **39.8%** | **−5.2 pts (dégradation réelle)** |
| Salaires | 4% | 21 | 5.0% | +1.0 pts (stagnation — toujours quasi nul) |
| Placement | 0.2% | 8 | **1.9%** | +1.7 pts (toujours quasi nul en valeur absolue : 8/420) |
| Perspectives | 39% | 161 | 38.3% | −0.7 pts (stagnation) |

**Verdict section par section, pas agrégé :** sur 10 sections, **8 sont en
stagnation stricte** (delta < 2 points, dans la marge de bruit d'un corpus
qui a pu légèrement changer de contenu depuis KB002 sans changer de
taille) — **le bug documenté par KB002 n'a pas été corrigé pour ces
8 sections**. Une seule section montre une **dégradation réelle** au-delà
du bruit (Admission, −5.2 points, voir §4). Aucune section ne montre
d'amélioration significative. **Aucune régression à 0% ou 100% n'a été
observée** — donc pas d'artefact de division par zéro à signaler (garde-fou
du brief).

## 2. Le mapping n'est pas absent — mais il ne peut pas récupérer ce qui n'a
   jamais été capturé

Point important à ne pas confondre : le pipeline actuel **a bien** un
dictionnaire de correspondance explicite (`section_key_map`,
`scraper/generate.py:227-238`) qui normalise la casse et les `\n` internes —
c'est une version quasi identique à la solution proposée par KB002
elle-même (comparer `docs/kb002.md`, section « Mapping requis » et
`scraper/generate.py:229-237` : les clés candidates sont pour l'essentiel
identiques mot pour mot, ex. `"tâches\net\nresponsabilités"`, `"milieu\nde\ntravail"`).
**Le mapping proposé par KB002 a donc été implémenté.** Mais la couverture
mesurée aujourd'hui est quasi identique à celle mesurée par KB002 **avant**
ce mapping. Ce n'est pas contradictoire : le mapping ne peut recomposer que
des clés déjà présentes dans `professions_details.json` — si une section
n'a jamais été détectée en amont par `scrape_v2.py` (parsing du HTML brut
en sections), aucun dictionnaire de correspondance en aval ne peut la faire
apparaître. **Le goulot n'est pas (plus) le mapping de clés — c'est la
capture initiale des sections par le scraper**, un problème différent de
celui documenté par KB002, bien qu'il produise le même symptôme observable
(sections quasi vides sur les fiches générées).

## 3. Clés orphelines nommées — présentes dans les données, non mappées par
   `section_key_map`

Cinq clés brutes distinctes, présentes dans `professions_details.json`,
ne correspondent à **aucune** des 10 clés cibles de `section_key_map` :

| Clé brute exacte | Occurrences | Diagnostic |
|---|---|---|
| `LIENS\nRECOMMANDÉS` | **383** (91% des fiches) | Section très fréquente sur le site, **totalement absente** de `section_key_map` dans `gen_profession()`. Existe pourtant dans le `SECTION_MAP` global inutilisé (`"recommandés": "liens"`, ligne 71) — incohérence entre les deux mécanismes de mapping coexistant dans le même fichier (voir §2, méthode point 2). |
| `VOIR\nAUSSI` | **309** (74% des fiches) | Même diagnostic : présente dans les données, absente de `section_key_map`, jamais rendue sur les pages générées. |
| `EXIGENCE\nDU\nMARCHÉ\nDU\nTRAVAIL` (singulier) | 19 | Variante orthographique non couverte : `section_key_map["marche"]` ne liste que `"exigences\ndu\nmarché\ndu\ntravail"` (pluriel). La variante singulière existe dans les données réelles (19 fiches) et n'est jamais mappée — cause directe d'une partie du déficit de la section Marché (9.8% au lieu d'un chiffre plus élevé si cette variante était couverte). |
| `NIVEAU\nD'ÉTUDES` | 11 | Absente de `section_key_map` (existe dans `SECTION_MAP` global sous `"niveau"`, mais ce mapping n'est pas utilisé par `gen_profession()`). |
| `DONNÉES\nSALARIALE` (singulier, sans "S" final) | 1 | **Cas particulier, diagnostiqué précisément** — voir §4. Ce n'est pas un vrai « jamais mappable » : une entrée équivalente (`"données\nsalariale"`, pluriel+singulier) existe bien dans `section_key_map["salaires"]` et matcherait cette clé isolément. Elle apparaît orpheline ici uniquement parce que, dans l'unique profession où les deux coexistent (`danseurl`), l'algorithme de matching s'arrête au premier candidat trouvé (`DONNÉES\nSALARIALES`, pluriel-pluriel) et ne visite jamais le second. |

**`LIENS RECOMMANDÉS` et `VOIR AUSSI` sont les découvertes les plus
significatives de cette section** : ce ne sont pas des cas rares — elles
couvrent respectivement 91% et 74% des fiches, largement plus que 8 des 10
sections officiellement suivies par KB002, et pourtant elles ne font partie
d'aucun suivi ni d'aucun mapping actif. Une section très bien couverte dans
les données brutes peut être invisible sur le site généré simplement parce
que personne ne l'a ajoutée à la liste des 10 clés cibles.

## 4. Diagnostic du mécanisme — deux bugs distincts, pas un seul

**Bug A (déjà identifié par KB002, non corrigé) : le scraper ne capture pas
toutes les sections réelles du site.** Ceci a été confirmé indépendamment
dans `docs/audit-claude-code-web-structure-site.md` (§5.1 de ce document,
rédigé avant ce brief révisé v2) : `scrape_v2.py` (le code de la classe
`ProfessionParserV2`, méthode `parse_sections`) utilise une liste **fermée**
de 15 regex de titres de section — toute section réelle du site dont le
titre ne matche aucune de ces 15 regex est fusionnée silencieusement dans
la section précédente, avant même d'atteindre `professions_details.json`.
C'est la cause structurelle en amont de la faible couverture de Qualités
(2.6%), Salaires (5.0%), Placement (1.9% — 8 fiches sur 420) : ces titres
réels sur le site (`SALAIRE`, `PLACEMENT`, `QUALITÉS ET APTITUDES
REQUISES` sans variante alternative) ne matchent pas les regex du scraper
(qui attend par exemple `DONNÉES SALARIALES`, pas `SALAIRE` seul — voir
l'exemple concret `protection/ambulancier.htm` où le vrai titre est
`SALAIRE`, jamais capturé).

**Bug B (nouveau, spécifique au mapping de `gen_profession()`, non
documenté par KB002) : collisions de clés à l'intérieur d'une même fiche.**
Quand une profession a **deux clés brutes distinctes qui pointent vers la
même section cible**, l'algorithme actuel (`section_key_map`, boucle avec
`break` au premier match) ne conserve que la première trouvée et **perd
silencieusement le contenu de la seconde**, même si les deux contiennent
des informations différentes. Mesuré précisément sur les 420 fiches :

| Section cible | Fiches avec collision (≥2 clés brutes distinctes) |
|---|---|
| Milieu | 36 (ex. `MILIEU DE TRAVAIL` + `MILIEUX DE TRAVAIL` coexistent) |
| Admission | 16 (ex. `EXIGENCES D'ADMISSION` + `EXIGENCE D'ADMISSION` coexistent) |
| Salaires | 1 — **`danseurl`**, vérifié en détail : `DONNÉES SALARIALES` (courte note de renvoi vers une autre fiche) et `DONNÉES SALARIALE` (données salariales substantielles, plusieurs paragraphes de chiffres) coexistent dans la même fiche. Seule la première (la note de renvoi, la moins utile des deux) est retenue ; **le contenu salarial réel de cette fiche est silencieusement perdu**. |

Le cas Admission (16 fiches en collision) explique une partie de la
dégradation de −5.2 points mesurée en §1 : sur ces fiches, une des deux
variantes (`EXIGENCE` singulier ou `EXIGENCES` pluriel) est ignorée même
quand elle est présente et non vide — combiné aux clés présentes mais
vides (183 occurrences de clés brutes vs 167 fiches à contenu non vide,
voir méthode point 4), cela suffit à expliquer l'écart avec le chiffre
KB002 de 45%.

## 5. Incohérence structurelle du fichier lui-même

`scraper/generate.py` contient **deux mécanismes de normalisation de clés
de section indépendants et incohérents entre eux** :

1. `SECTION_MAP` (ligne 61) + `normalize_section()` (ligne 78, matching par
   sous-chaîne insensible à la casse) — utilisé uniquement dans
   `Generator.load()` pour peupler `p["sn"]`, un attribut qui n'est **plus
   jamais lu** ailleurs dans le fichier après sa construction (vérifié par
   recherche textuelle de `p["sn"]` / `["sn"]` dans le reste du fichier —
   aucune occurrence trouvée après la ligne 201).
2. `section_key_map` local (ligne 227, dans `gen_profession()`) — c'est
   **celui-ci qui détermine réellement** ce qui est rendu sur chaque page
   générée.

Le premier couvre `liens` et `niveau` ; le second ne les couvre pas. Deux
développeurs (ou deux passes du même agent, à des moments différents) ont
manifestement écrit deux solutions au même problème sans les unifier, et
c'est la moins complète des deux qui est active en production. C'est un
écart facile à corriger (fusionner les deux dictionnaires, supprimer le
mort), mais il n'a pas été trouvé avant cet audit malgré un `SECTION_MAP`
apparemment déjà « complet » à première lecture.

## 6. Réponse à la question posée

**Le bug KB002 (mapping de clés fragile) n'a été ni corrigé, ni reproduit
à l'identique ailleurs — il persiste, avec une nuance de méthode
importante :**

- Le **symptôme mesuré** (couverture par section) est quasiment identique
  à celui de KB002, section par section, à ±2 points près pour 9 sections
  sur 10 — c'est-à-dire **stagnation**, pas correction.
- Mais le **mécanisme causal a changé de place**. KB002 avait diagnostiqué
  un problème de mapping en aval (`generate.py` ne reconnaissait pas les
  clés produites par le scraper). Ce mapping en aval **a depuis été
  largement implémenté** (`section_key_map`, quasi identique à la solution
  proposée par KB002 elle-même) — mais il ne peut pas récupérer une
  section jamais capturée en amont par `scrape_v2.py`. Le goulot s'est
  déplacé du mapping vers la capture initiale, sans que la couverture
  finale n'en soit changée pour l'utilisateur.
- Deux mécanismes **nouveaux**, non documentés par KB002, ont été trouvés
  et quantifiés dans ce même pipeline : (a) deux sections à fort volume
  (`LIENS RECOMMANDÉS` 91%, `VOIR AUSSI` 74%) présentes dans les données
  mais absentes de tout mapping actif ; (b) une perte de contenu par
  collision de clés au sein d'une même fiche (54 fiches concernées au
  total sur les 3 sections vérifiées), avec au moins un cas confirmé de
  perte de contenu substantiel et non redondant (`danseurl` / Salaires).

Ce n'est donc ni « corrigé » ni un pur « copier-coller du même bug » — c'est
un **bug voisin, dans la même famille** (correspondance de clés fragile
entre étapes du pipeline), qui produit le même symptôme mesuré mais par un
mécanisme partiellement différent et avec au moins deux causes additionnelles
non documentées jusqu'ici.
