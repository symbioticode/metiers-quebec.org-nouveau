# Audit Milieu / Description / Formation — dernière zone d'ombre du gate Sprint 1

**Horodatage :** 2026-07-28.
**Branche :** `experimental/durcissement-milieu-description-formation` (depuis
`experimental/scrape-v2-hardening`, tip `f301a95`, avant intégration des
travaux `experimental/durcissement-checklist-scraper` de Big Pickle).
**Corpus :** `data/professions_details.json`, 485 fiches, post-fix `f301a95`
(scraper durci, clés sans `\n`).

## Résumé — un résultat par section, trois causes différentes confirmées

| Section | Avant (section_key_map seul) | Après (mesure corrigée, pipeline complet) | Verdict |
|---|---|---|---|
| `description` | 0.0% | **10.1%** (49/485) | Angle mort de mesure confirmé — le fallback `intro→description` existe et fonctionne, juste jamais inclus dans les mesures de couverture précédentes. Pas de correctif de code nécessaire. |
| `formation` | 0.4% | **1.4%** (7/485) | Vraiment bas, pas un artefact. Les 3 variantes candidates identifiées (`ENDROITS DE FORMATION`, `ENDROIT DE FORMATION`, `AUTRES FORMATIONS`) sont un concept **différent** (établissements/programmes), vérifié sur le contenu réel — **non fusionnées**. Le vrai niveau de formation requis semble vivre dans `intro` sous un intitulé différent (`NIVEAU(X) D'ÉTUDES`), mais son extraction fiable n'a pas pu être faite proprement dans ce sprint — signalé comme travail ouvert, pas bricolé. |
| `milieu` | 0.0% | **0.0%** | Confirmé par balayage exhaustif des 353 clés brutes distinctes du corpus entier (pas un échantillon) : aucun titre apparenté à « milieu de travail » n'existe dans ces 485 fiches, à l'exception de 3 occurrences isolées et sémantiquement différentes. **Aucune correspondance forcée.** |

## 1. `description` — angle mort de mesure, pas un bug de code

Le fallback `intro → description` existe déjà dans `gen_profession()`
(`scraper/generate.py`, lignes 289-318) : il cherche dans `intro` le premier
« déclencheur de phrase » français (`Le `, `La `, `Un `, etc.) et extrait
jusqu'à 500 caractères jusqu'à la ponctuation de fin de phrase suivante.

**Vérification directe** (réplication exacte de la logique du fallback,
exécutée sur les 485 fiches réelles, hors du mesureur de couverture
précédent qui ne testait que `section_key_map`) : le fallback produit un
résultat non vide pour **49 fiches sur 485 (10.1%)**. Ce n'est **pas** un
0% masqué qui serait en réalité proche de 100% une fois le fallback pris en
compte — 10.1% est le vrai chiffre.

**Qualité du contenu extrait, vérifiée sur 3 exemples réels** (pas
supposée) :

```
transport1l      -> "L'agent d'escale peut travailler les week-ends et les jours fériés."
tech_administration -> "Une chose est certaine, c'est une formation collégiale que tu veux ?"
armee2           -> "Un capitaine par exemple, peut commander un peloton comprend environ une centaine de soldats."
```

Le premier exemple est une phrase sur les conditions de travail, pas une
description du métier ; le second est une question rhétorique tronquée,
pas une phrase informative. **L'heuristique « premier déclencheur de
phrase » est fragile et produit parfois un contenu de mauvaise qualité même
quand elle n'est pas vide** — signalé comme limite connue, hors scope de
correction dans ce sprint (le brief demandait de vérifier si le fallback
fonctionne, pas de le réécrire).

**Action prise** : aucune modification de code. La mesure de couverture
corrigée (incluant le fallback) est reportée dans le tableau récapitulatif
final (§4).

## 2. `formation` — contenu vérifié avant fusion, rejeté à raison

Trois variantes candidates identifiées par comptage direct sur les 485
fiches : `ENDROITS DE FORMATION` (365), `ENDROIT DE FORMATION` (73),
`AUTRES FORMATIONS` (75).

**Contenu réel vérifié sur 4 exemples concrets avant toute décision de
fusion**, conformément au garde-fou du brief :

```
tech_tourisme (ENDROITS DE FORMATION) :
  "Qu'est-ce que l'... (D.E.C. en tourisme d'aventure), campus de Gaspé
   offert en cheminement en alternance travail-études..."

ouvrier_agricole5 (ENDROITS DE FORMATION) :
  "Demande d'admission via Internet... Saint-Anselme (C.S. de la
   Côte-du-Sud, Chaudière-Appalaches) Accès à une érablière-école..."

gest_appro (AUTRES FORMATIONS) :
  "Il existe également plusieurs programmes d'A.E.C. d'une durée moindre
   que le D.E.C. (1 an ou 2 ans)..."

artiste_cirque (AUTRES FORMATIONS) :
  "Il existe également d'autres formations permettant de faire carrière...
   Le Programme de formation professionnelle d'artiste du cirque..."
```

**Verdict : ce n'est pas la même nature d'information que « formation
requise » attendait.** `ENDROITS DE FORMATION` liste des établissements,
campus, modalités d'admission, bourses — c'est une réponse à « où
étudier ? ». `AUTRES FORMATIONS` liste des programmes alternatifs — une
réponse à « quelles autres voies existent ? ». Ni l'un ni l'autre ne
répond à « quel niveau d'études est requis pour exercer ce métier ? »,
qui était l'intention originale de la clé cible `formation`. **Fusionner
ces trois variantes sous `formation` aurait été exactement l'erreur que
le garde-fou du brief demandait d'éviter** — non fait.

**Piste ouverte, non résolue dans ce sprint** : le vrai niveau de formation
requis semble présent dans `intro`, sous l'intitulé `NIVEAU(X) D'ÉTUDES`
(confirmé par lecture directe : ex. `agriculture3l` — *« NIVEAUX D'ÉTUDES
:SECONDAIRE NON TERMINÉ ouSECONDAIRE TERMINÉ ouFORMATION PROFESSIONNELLE
courte »*). Une tentative d'extraction par regex sur ce motif a été faite
et **a échoué à produire un résultat fiable** (le format `intro` est un
flux de mots collés sans ponctuation fiable, rendant la délimitation de fin
de champ ambiguë sans un travail de parsing plus sérieux qu'un correctif
ponctuel). Non implémenté ici plutôt que livré sous une forme fragile —
signalé comme travail pour un sprint dédié, pas bricolé dans celui-ci.

**Action prise** : aucune modification de `section_key_map`. `formation`
reste couvert uniquement par ses correspondances directes existantes
(`FORMATION REQUISE`, `FORMATION` — 2 occurrences) et le fallback intro
existant (`FORMATION\s+REQUISE?` — recouvre 5 occurrences supplémentaires,
qui ne cherchent pas le bon motif `NIVEAU D'ÉTUDES` mais matchent par
coïncidence sur d'autres formulations). Total mesuré : 7/485 (1.4%).

## 3. `milieu` — absence confirmée, pas une correspondance manquée

**Méthode** : balayage exhaustif de **toutes les 353 clés brutes
distinctes** présentes dans les `sections` des 485 fiches (pas un
échantillon, pas un grep limité à quelques mots-clés évidents) —
recherche des motifs `MILIEU`, `TRAVAIL`, `CONDITION`, `LIEU DE`,
`ENVIRONNEMENT`, `AMBIANCE`, `HORAIRE`, `CADRE DE`.

**Résultat complet** :

```
  45  'EXIGENCES DU MARCHÉ DU TRAVAIL'     (déjà mappé vers "marche")
  19  'EXIGENCE DU MARCHÉ DU TRAVAIL'      (déjà mappé vers "marche")
   3  'CONDITIONS DE TRAVAIL'
   2  'EXIGENCES DES EMPLOYEURS ET DU MARCHÉ DU TRAVAIL'
   1  'CONDITIONS D'ADMISSION'
   1  'STATISTIQUES DÉMONTRANT LE TRAVAIL DES AGENTS DES SERVICES FRONTALIERS'
   1  'TYPES DE MILIEUX DE PRATIQUE EN MÉDECINE GÉNÉRALE ET FAMILIALE'
   1  'AUTRES EXIGENCES DU MARCHÉ DU TRAVAIL'
   1  'FORMATION EN MILIEU DE TRAVAIL'
   1  'MILIEUX DE PRATIQUE'
   1  "MILIEUX D'INTERVENTION"
```

**Aucun titre `MILIEU DE TRAVAIL` (ou variante plurielle proche) n'existe
dans le corpus entier.** Les seules occurrences contenant littéralement le
mot « milieu » sont isolées (1 occurrence chacune), rattachées à des fiches
uniques et sémantiquement distinctes (« milieux de pratique » en médecine,
« milieux d'intervention », « formation en milieu de travail » — un
sous-thème de formation, pas une section autonome). `CONDITIONS DE
TRAVAIL` (3 occurrences) est le candidat le plus proche mais reste
marginal (0.6% des fiches), pas une variante systématique du même concept.

**Corroboration indépendante** : la lecture aveugle du site live
(`docs/audit-claude-code-web-structure-site.md`, produite dans un audit
antérieur séparé, avant tout accès au code du scraper) n'avait déjà relevé
aucune section « MILIEU DE TRAVAIL » sur les deux fiches lues intégralement
(`tailleur_pierres.html`, `ambulancier.htm`) — cohérent avec l'hypothèse que
cette section n'existe simplement pas, ou n'existe plus, sous ce titre sur
le site source pour l'essentiel des fiches, plutôt que d'être perdue par un
défaut du scraper ou du mapping.

**Action prise : aucune.** Pas de correspondance forcée vers un concept
voisin (`EMPLOYEURS POTENTIELS`, très fréquent à 473 occurrences, aurait pu
être un candidat tentant mais reste sémantiquement distinct — une liste
d'employeurs n'est pas une description du milieu de travail — non fait,
conformément au garde-fou).

## 4. Tableau de couverture final — méthode KB002, pipeline complet

Mesure incluant `section_key_map` **et** les deux fallbacks `intro`
existants (`description`, `formation`) — pas seulement le dictionnaire brut
comme dans les mesures précédentes de ce sprint.

| Section | KB002 original | Avant ce sprint (`f301a95`, dict seul) | Après ce sprint (pipeline complet) |
|---|---|---|---|
| Description | 31% | 0.0% | **10.1%** |
| Tâches | 92% | 92.4% | 92.4% (inchangé) |
| Milieu | 60% | 0.0% | **0.0%** (confirmé, pas un bug) |
| Qualités | 1% | 96.5%¹ | 96.5% |
| Marché | 9% | 13.2%¹ | 13.2% |
| Formation | 6% | 0.4% | **1.4%** |
| Admission | 45% | 87.4%¹ | 87.4% |
| Salaires | 4% | 97.3%¹ | 97.3% |
| Placement | — | 89.3% | 89.3% (inchangé) |
| Perspectives | 39% | 92.8%¹ | 92.8% |

¹ Déjà corrigé par le fix `section_key_map` de `f301a95` (apostrophe +
formulations réelles), avant ce sprint — inchangé ici, reporté pour
contexte complet.

**`milieu` reste très en dessous du chiffre KB002 original (60%), et c'est
la conclusion correcte, pas une régression à corriger.** KB002 mesurait un
corpus antérieur (ancien scraper, 420 fiches) où cette section existait
peut-être réellement sous ce titre. Sur le corpus actuel du scraper durci
(485 fiches), elle n'existe simplement plus sous cette forme — un
changement de contenu réel, pas un défaut de mapping à corriger dans
`section_key_map`.

## Ce que ce rapport ne fait pas

- Ne modifie pas `section_key_map` — aucune des trois investigations n'a
  justifié un ajout ou une correction du dictionnaire.
- Ne force aucune correspondance approximative pour faire monter un chiffre.
- N'implémente pas d'extracteur `NIVEAU D'ÉTUDES` pour `formation` malgré la
  piste identifiée — tentative documentée, résultat non fiable, non livré.
- Ne modifie aucune donnée source (`professions_details.json` inchangé).
