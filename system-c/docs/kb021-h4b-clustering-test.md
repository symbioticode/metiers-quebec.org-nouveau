# kb021 — Test H4b : un alphabet de fonctions atomiques émerge-t-il par clustering ?

**Statut : test empirique complémentaire, non committé comme conclusion de kb021.md.**

## Contexte

Le test O*NET (`kb021-genome-stability-onet-test.md`) a corroboré H4a — une couche figée
*par construction* (les 41 GWA) reste figée. Ce n'est pas une preuve de H4b, la version
forte de l'hypothèse : que les fonctions atomiques forment un alphabet stable en émergeant
*naturellement* du corpus, sans qu'une liste externe ne les fige a priori. Le test
bottom-up second-wave (`kb021-bottom-up-second-wave-test.md`) n'a pas non plus testé H4b :
il a répété la méthode de classification manuelle (i)/(ii)/(iii) de kb020 sur un deuxième
échantillon — utile pour comparer un taux de nouveauté, mais aucun alphabet n'y émerge par
une méthode indépendante du jugement humain catégorie par catégorie.

Ce document teste H4b directement : faire émerger des clusters sémantiques par une méthode
automatique, sans fixer leur nombre à l'avance, sur l'ensemble des fonctions atomiques déjà
nommées dans kb019 + kb020 + second-wave, puis vérifier si ces clusters restent stables
quand on ajoute la deuxième vague.

## Corpus

`scripts/extract_atomic_functions_corpus.py` → `data/reference/onet-genome-stability/atomic-functions-corpus.json` :
88 fonctions atomiques candidates, recopiées **telles quelles** (aucune reformulation ni
fusion manuelle préalable — voir garde en tête du script) depuis :
- kb019 (3 lectures décomposées de "Coach IA" : (a), (c), (d)) : 19 fonctions
- kb020 (13 métiers) : 36 fonctions
- second-wave (11 métiers, 2026) : 33 fonctions

Découpage pour le test de stabilité :
- **(a)** kb019 + kb020 = 55 fonctions, 16 "métiers"/lectures
- **(full)** (a) + second-wave = 88 fonctions, 27 métiers
- Croissance du corpus entre (a) et (full) : +60% de fonctions, **+68,8% de métiers**

## Méthode (décidée et documentée avant tout résultat)

`scripts/cluster_atomic_functions.py`. Choix figés avant exécution, pour écarter le
risque de choisir une méthode qui produirait un résultat proche de 41 (biais de
confirmation implicite, explicitement proscrit par la consigne) :

1. **Vectorisation** : TF-IDF sur des n-grammes de caractères (`analyzer='char_wb'`,
   `ngram_range=(3,5)`), minuscules, accents conservés — pas de lemmatisation ni de liste
   d'arrêt (choix qui introduirait un paramètre supplémentaire à justifier).
2. **Distance** : cosinus.
3. **Algorithme** : `AgglomerativeClustering` (scikit-learn), `linkage='average'`,
   `n_clusters=None`, `distance_threshold=T` — le nombre de clusters émerge du seuil, il
   n'est jamais fixé.
4. **Trois seuils pré-enregistrés** : T ∈ {0,50 ; 0,60 ; 0,70} (bas → fusion stricte, haut
   → fusion permissive), tous rapportés, aucun sélectionné après coup.
5. **(full)** est un reclustering complet depuis zéro sur les 88 fonctions, pas un ajout
   incrémental sur les centroïdes de (a) — pour tester si la *forme* des clusters change,
   pas seulement leur nombre.

Stabilité mesurée par **pureté** : pour chaque cluster de (a), on identifie le cluster de
(full) qui contient le plus de ses membres, et on calcule la fraction des membres du
cluster (a) qui restent groupés dans ce même cluster (full). Pureté = 1 → cluster
parfaitement stable ; pureté < 1 → le cluster (a) a été éclaté par l'ajout de la deuxième
vague.

## Résultats bruts

| Seuil T | k clusters (a) | k clusters (full) | Croissance clusters | Croissance métiers | Pureté moyenne | Clusters (a) parfaitement stables |
|---|---|---|---|---|---|---|
| 0,50 | 52 | 81 | +55,8% | +68,8% | 1,000 | 52/52 |
| 0,60 | 49 | 76 | +55,1% | +68,8% | 0,990 | 48/49 |
| 0,70 | 47 | 71 | +51,1% | +68,8% | 0,989 | 46/47 |

Détail complet : `data/reference/onet-genome-stability/clustering-h4b.json` (résultat
brut, tous seuils) et `clustering-h4b.md` (table).

**Composition des clusters** : à tous les seuils testés, la grande majorité des clusters
sont des singletons (une seule fonction, aucune fusion) — à T=0,70 (seuil le plus
permissif), 40 des 47 clusters de (a) sont des singletons ; seuls 7 regroupent 2 ou 3
fonctions. Exemples de fusions réussies : « ajuster des paramètres/règles d'un système » /
« ajuster des paramètres de modèle » / « ajuster des paramètres de procédé de fabrication »
(3 fonctions, vocabulaire quasi identique) ; « accompagner un changement organisationnel
(adoption) » / « accompagner un changement organisationnel lié à l'IA » (kb019 lecture (d)
et second-wave item #9 — la même paire déjà repérée qualitativement dans le rapport
second-wave).

**Fusions manquées** (paires sémantiquement proches mais jamais regroupées, à aucun
seuil) : « évaluer une performance individuelle » (kb019-c) et « évaluer le niveau de
maîtrise d'un outil chez un individu » (kb019-d) ne partagent presque aucun n-gramme de
caractères malgré une proximité sémantique évidente pour un lecteur humain — elles restent
dans des clusters séparés aux trois seuils.

## Verdict — inconclusif, et pourquoi

**Ce test ne corrobore ni n'infirme H4b proprement — la méthode elle-même est trop
grossière pour trancher, et ce constat doit être rapporté comme tel plutôt que forcé dans
un sens.**

Deux lectures possibles des chiffres, et rien dans les données ne permet de choisir entre
elles :

1. **Lecture pro-H4b** : la croissance des clusters (51-56%) est légèrement inférieure à
   la croissance des métiers (68,8%), et les clusters (a) qui existent restent
   quasi-parfaitement stables (pureté 0,99-1,0) quand on ajoute la deuxième vague — aucun
   cluster ne se redessine significativement, contrairement au negative case prévu par la
   consigne ("les clusters se redessinent à chaque ajout").
2. **Lecture méthode-insuffisante** : l'écart clusters/métiers (52-56% de croissance)
   n'est pas net comme celui d'O*NET (0% de croissance des GWA), et surtout, la
   composition des clusters trouvés montre que la méthode capte des similarités
   **lexicales de surface** (mêmes mots partagés : "ajuster des paramètres...",
   "accompagner un changement organisationnel...") plutôt que des équivalences
   **sémantiques** (l'exemple "évaluer une performance individuelle" / "évaluer le niveau
   de maîtrise" le montre directement — deux fonctions qu'un lecteur humain rapprocherait
   sans hésiter restent non fusionnées à tous les seuils testés). Avec 40-50 des ~50
   clusters qui sont des singletons, le clustering se comporte proche d'une identité
   (chaque fonction = son propre cluster) — un résultat qui ressemblerait à une
   "corroboration faible" de H4b même dans un corpus où l'alphabet réel ne serait PAS plus
   stable que les métiers, simplement parce que la méthode ne détecte quasiment aucune
   redondance sémantique à regrouper.

**En clair** : la faible croissance relative des clusters observée ici est compatible avec
H4b, mais elle est tout aussi compatible avec un simple artefact de sous-détection de la
méthode lexicale utilisée. Ce test ne peut pas distinguer les deux — il faudrait des
embeddings sémantiques réels (modèle de langue, pas TF-IDF de caractères) pour retester H4b
avec une méthode capable de rapprocher des libellés sémantiquement équivalents mais
lexicalement distincts. Ceci est signalé comme limite de méthode, pas comme résultat
positif déguisé.

## GARDES

- **Corpus encore petit** (88 fonctions, 24 métiers cumulés uniques hors doublons de
  lecture) : même avec un résultat net, ce test resterait indicatif, pas définitif. Il ne
  l'est pas ici de toute façon (voir verdict).
- **Méthode choisie avant tout résultat** : les trois seuils (0,50/0,60/0,70) ont été
  décidés avant l'exécution, aucun n'a été retenu après coup pour son nombre de clusters —
  documenté dans le script avant l'exécution, conformément à la garde anti-biais de
  confirmation demandée.
- **TF-IDF de n-grammes de caractères ≠ embeddings sémantiques** : c'est la limite
  principale de ce test, explicitée ci-dessus plutôt que masquée. Un futur test avec de
  vrais embeddings sémantiques (nécessitant un accès à un modèle d'embedding, non
  disponible dans cet environnement d'exécution) serait nécessaire pour trancher H4b plus
  proprement.
- **`docs/kb021.md` n'est pas modifié par ce document.** Le résultat n'est pas net dans un
  sens ou l'autre — il est documenté ici comme finding en soi, exactement comme kb020 et
  le test second-wave l'ont fait pour leurs propres résultats mitigés. Les trois tests
  complémentaires de kb021 (top-down O*NET/CNP, bottom-up second-wave, et ce test de
  clustering H4b) sont désormais tous disponibles pour la décision d'Andrei — cette
  décision n'est pas prise ici.
