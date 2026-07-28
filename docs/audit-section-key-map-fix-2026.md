# Correctif `section_key_map` — gate manquant du Sprint 1 (compatibilité generate.py)

**Horodatage :** 2026-07-28.
**Contexte :** `experimental/scrape-v2-hardening` a produit une nouvelle donnée
(`data/professions_details.json`, 485 entrées) via un scraper durci (détection
générique de titres au lieu de 15 regex fermées, liens tolérants,
multi-appellations). `scraper/generate.py` (et son `section_key_map`)
n'existait que sur `main`, avec l'ancienne donnée (420 entrées) — la
compatibilité bout-en-bout entre les deux n'avait jamais été testée. Ce
document comble ce gate, apporté sur cette branche à la demande d'Andrei.

## Ce que le diagnostic initial disait, et ce qui est réellement vrai

Le diagnostic initial (confirmé indépendamment par ailleurs) notait un écart
de format : clé réelle `'TÂCHES ET RESPONSABILITÉS'` (sans `\n`) contre
`"TÂCHES\nET\nRESPONSABILITÉS"` attendu par l'ancien `section_key_map`.

**Vérification empirique faite avant toute correction** (script
`measure_current.py`, sortie brute ci-dessous) : la normalisation `\n` →
espace existait **déjà** dans le code de `gen_profession()` avant ce
correctif (`actual_key.lower().replace("\n", " ")`), donc à elle seule,
l'absence de `\n` dans la nouvelle donnée **ne cassait rien** — une clé sans
`\n` normalisée avec `.replace("\n"," ")` reste inchangée, et matchait déjà
correctement les candidats qui, eux, contenaient des `\n` littéraux (le
`.replace()` s'applique aussi côté candidat).

**Coverage AVANT correction, mesurée directement sur les 485 entrées, avec
le `section_key_map` non modifié :**

```
TOTAL entries: 485

description        0 / 485  = 0.0%   matched_raw_keys=[]
taches           448 / 485  = 92.4%   matched_raw_keys=['TÂCHES ET RESPONSABILITÉS']
milieu             0 / 485  = 0.0%   matched_raw_keys=[]
qualites            4 / 485  = 0.8%   matched_raw_keys=['QUALITÉS ET APTITUDES REQUISES']
marche             45 / 485  = 9.3%   matched_raw_keys=['EXIGENCES DU MARCHÉ DU TRAVAIL']
formation           2 / 485  = 0.4%   matched_raw_keys=['FORMATION', 'FORMATION REQUISE']
admission          27 / 485  = 5.6%   matched_raw_keys=['ADMISSION', "EXIGENCES D'ADMISSION"]
salaires            1 / 485  = 0.2%   matched_raw_keys=['SALAIRES']
placement         433 / 485  = 89.3%  matched_raw_keys=['PLACEMENT']
perspectives        2 / 485  = 0.4%   matched_raw_keys=["PERSPECTIVES D'EMPLOI"]
```

Ce n'est donc **pas** un 0% uniforme (`taches` et `placement` marchaient déjà
par coïncidence de formulation), et la cause réelle n'est **pas** le `\n`.
Deux causes distinctes, confirmées en comptant les clés brutes réelles sur
les 485 entrées :

1. **Apostrophe courbe vs droite** — le site utilise très majoritairement
   l'apostrophe typographique `’` (U+2019) : `EXIGENCES D’ADMISSION` (364
   occurrences) contre `EXIGENCES D'ADMISSION` (apostrophe droite, 26
   occurrences seulement). L'ancien `section_key_map` codait la forme
   droite en dur — il ne matchait que la minorité des cas.
2. **Variance réelle de formulation, maintenant fidèlement capturée** — le
   scraper durci capture le titre exact de chaque page (détection générique)
   au lieu de le forcer dans 15 regex fermées. Dix-sept ans d'édition
   manuelle du site produisent plusieurs formulations réelles distinctes pour
   un même concept, et l'ancien mapping n'en couvrait souvent qu'une seule —
   parfois la mauvaise. Exemple le plus frappant : `perspectives` attendait
   `"perspectives d'emploi"`, alors que la formulation dominante réelle est
   **`PERSPECTIVES D'AVENIR`** (448 occurrences combinées, courbe+droite),
   jamais `D'EMPLOI` sous cette forme exacte.

## Correctif appliqué

`scraper/generate.py`, fonction `gen_profession()` :

1. `section_key_map` réécrit sans `\n` littéraux (candidats en espaces
   simples — plus lisible, comme anticipé par la demande).
2. Nouvelle fonction `_norm_key()` : normalise apostrophe courbe `’` → droite
   `'`, en plus de la casse et des espaces multiples (le `\n` n'a plus besoin
   d'un traitement spécial car il n'est plus présent).
3. Candidats élargis avec les formulations réelles confirmées par comptage
   direct sur les 485 entrées (pas devinées) : variantes de `qualités`,
   `perspectives d'avenir`, `salaire` singulier, `exigence` (singulier) du
   marché du travail.

## Coverage APRÈS correction — comparaison directe avec l'ancien résultat

```
TOTAL entries: 485

Section        Avant (non corrigé)   Après (corrigé)   Delta
description     0.0%                  0.0%              0.0 pts (inchangé — voir note)
taches         92.4%                 92.4%              0.0 pts (déjà correct)
milieu          0.0%                  0.0%              0.0 pts (inchangé — voir note)
qualites        0.8%                 96.5%            +95.7 pts
marche          9.3%                 13.2%             +3.9 pts
formation       0.4%                  0.4%              0.0 pts (inchangé — voir note)
admission       5.6%                 87.4%            +81.8 pts
salaires        0.2%                 97.3%            +97.1 pts
placement      89.3%                 89.3%              0.0 pts (déjà correct)
perspectives    0.4%                 92.8%            +92.4 pts
```

## Comparaison avec kb024

**kb024 n'était pas disponible en intégralité dans cette session** (recherché
sur toutes les branches distantes, absent partout — seul le point d'ancrage
cité directement par Andrei, « 60% Milieu », a pu être utilisé). Sur ce point
précis : **`milieu` reste à 0.0% après correction**, très en dessous des 60%
cités pour kb024/KB002. Ce n'est **pas un bug de mapping résiduel** — vérifié
directement : le titre exact `MILIEU DE TRAVAIL` (ou `MILIEUX DE TRAVAIL`)
n'existe **quasiment plus du tout** dans les 485 entrées de cette branche
(recherche exhaustive : seules des variantes composées non équivalentes comme
`MILIEUX DE PRATIQUE`, `MILIEUX D'INTERVENTION`, chacune à 1 occurrence
isolée). La section `EMPLOYEURS POTENTIELS` (473 occurrences, très
fréquente) est peut-être un successeur sémantique proche, mais **ce n'est
pas vérifié** et je ne l'ai pas mappée vers `milieu` sans confirmation —
faire ce choix silencieusement reviendrait à trancher une question de
modélisation sémantique (est-ce le même concept ?) déguisée en correctif de
formatage, exactement le type de décision que ce projet a déjà appris à ne
pas prendre à la légère (voir kb025). Signalé, non tranché.

`description` (0.0%) et `formation` (0.4%) restent également bas après
correction, pour une raison différente et plus bénigne : `description` est
géré par le repli existant sur `intro` déjà présent dans `gen_profession()`
(hors scope de `section_key_map`, non modifié ici) ; `formation` au sens
strict de « FORMATION REQUISE » n'existe presque plus, remplacé
vraisemblablement par `LES PROGRAMMES D'ÉTUDES` (226) / `LE PROGRAMME
D'ÉTUDES` (225) / `AUTRES FORMATIONS` (75) — candidats **volontairement non
ajoutés** à `formation` dans ce correctif : rattacher « programme d'études »
à la clé `formation` est un choix de modélisation, pas une correction de
format, et n'a pas été fait sans confirmation, par le même principe que pour
`milieu`.

## Ce que ce correctif ne fait pas

- Ne mappe aucune des sections très fréquentes mais absentes du schéma à 10
  clés d'origine (`EMPLOYEURS POTENTIELS` 473×, `LIENS RECOMMANDÉS` 427×,
  `PROFESSIONS APPARENTÉES` 410×, `EXIGENCES DES EMPLOYEURS` 389×) — hors
  scope de cette demande précise (comparaison à la méthode KB002/kb024, qui
  ne suit que les 10 clés d'origine).
- Ne corrige pas `description`/`formation`/`milieu` à 0% par un remappage
  vers un concept voisin non confirmé — signalé explicitement ci-dessus au
  lieu d'être silencieusement classé comme résolu.
- Ne modifie aucune donnée (`professions_details.json` inchangé) — seul
  `scraper/generate.py` est modifié.

## Fichiers

- `scraper/generate.py` — `section_key_map` et `_norm_key()` corrigés.
- Scripts de mesure (`measure_current.py`, `measure_corrected.py`,
  non committés — usage ponctuel de vérification, reproductibles depuis ce
  document si nécessaire).
