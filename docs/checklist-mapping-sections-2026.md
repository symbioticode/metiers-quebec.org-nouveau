# Checklist adversariale — Mapping de sections (`section_key_map`, `_looks_like_section_title`)

**Branche** : `experimental/durcissement-checklist-scraper`
**Date** : 2026-07-28
**Agent** : Big Pickle (OpenCode-DeepSeek)
**Références** : `durcissement-scraper-generateur_v0_1.md §1b`, `kb024-verdict-consolide-bug-kb002.md`

---

## Constat préalable : le format des données a changé depuis l'audit kb024

Les 53 collisions documentées dans kb024 et l'audit `fidelite-template-big-pickle.json` concernent des clés de sections **contenant des `\n`** (ex. `'MILIEU\nDE\nTRAVAIL'`, `'DONNÉES\nSALARIALES'`). Ce format était produit par l'ancienne version du scraper.

Le fichier `data/professions_details.json` actuel (généré par `scrape_v2.py`) utilise des clés **sans `\n`** — des espaces normaux (ex. `'MILIEU DE TRAVAIL'`), ou des clés radicalement différentes (ex. `'SALAIRE'` au lieu de `'DONNÉES\nSALARIALES'`).

| Clé (audit kb024, avec `\n`) | Clé actuelle | Présente ? |
|---|---|---|
| `MILIEU\nDE\nTRAVAIL` | `MILIEU DE TRAVAIL` | **ABSENTE** (0 occurrence) |
| `MILIEUX\nDE\nTRAVAIL` | `MILIEUX DE TRAVAIL` | **ABSENTE** (0 occurrence) |
| `DONNÉES\nSALARIALES` | `DONNÉES SALARIALES` | **ABSENTE** (0 occurrence) |
| `DONNÉE\nSALARIALE` | `DONNÉE SALARIALE` | **ABSENTE** (0 occurrence) |
| `EXIGENCES\nDU\nMARCHÉ\nDU\nTRAVAIL` | `EXIGENCES DU MARCHÉ DU TRAVAIL` | 45 occurrences |
| `TÂCHES\nET\nRESPONSABILITÉS` | `TÂCHES ET RESPONSABILITÉS` | 448 occurrences |

**Les 53 collisions de kb024 n'existent plus dans les données actuelles. Il n'y a aucune collision de clé détectable avec la section_key_map actuelle.** La cause n'est pas une correction du mapping, mais un changement de format des clés en amont qui a rendu la section_key_map largement inopérante pour les nouvelles clés.

---

## 1. Résultat de section_key_map sur les données actuelles

### Correspondances par cible (sur 485 fiches)

| Cible | Clés brutes correspondantes | Occurrences | Couverture |
|---|---|---|---|
| `taches` | `TÂCHES ET RESPONSABILITÉS` | 448 | 92,4% |
| `placement` | `PLACEMENT` | 433 | 89,3% |
| `marche` | `EXIGENCES DU MARCHÉ DU TRAVAIL` | 45 | 9,3% |
| `admission` | `EXIGENCES D'ADMISSION` (droite, 26), `ADMISSION` (1) | 27 | 5,6% |
| `qualites` | `QUALITÉS ET APTITUDES REQUISES` | 4 | 0,8% |
| `perspectives` | `PERSPECTIVES D'EMPLOI` (droite) | 2 | 0,4% |
| `formation` | `FORMATION REQUISE` (1), `FORMATION` (1) | 2 | 0,4% |
| `salaires` | `SALAIRES` | 1 | 0,2% |
| `milieu` | *(aucune correspondance)* | 0 | 0% |
| `description` | *(aucune correspondance)* | 0 | 0% |

### Constats clés

1. **`milieu` et `description` à 0%** : le `section_key_map` (source_keys : `['milieu\nde\ntravail', 'milieux\nde\ntravail', 'milieu']`) ne correspond à aucune clé brute actuelle. Les clés réelles incluent `MILIEUX DE PRATIQUE`, `CONDITIONS DE TRAVAIL`, etc. — toutes ignorées.

2. **`salaires` à 0,2% (1 fiche)** : la clé réelle est `SALAIRE` (471/485 fiches), pas `SALAIRES` (1 fiche) ni `DONNÉES SALARIALES` (0). La section_key_map ne matche que `'salaires'` (lowercase exact). 470 fiches avec données salariales sont perdues.

3. **`SALAIRE` vs `SALAIRES`** : le cas Chorégraphe ne montre plus la collision 86 vs 40 756 caractères documentée dans kb024. À la place, ses 637 mots de données salariales (clé `'SALAIRE'`) ne sont **pas du tout capturés** — une régression silencieuse : aucune donnée salariale n'est transmise au template.

4. **Apostrophe courbe vs droite** : `EXIGENCES D'ADMISSION` (courbe, 337 fiches) n'est pas reconnue. Seule `EXIGENCES D'ADMISSION` (droite, 26 fiches) correspond à `'exigences\nd\'admission'`. Les fiches avec apostrophe courbe perdent leur section Admission.

5. **Zéro collisions** : aucune fiche n'a deux clés brutes qui matchent deux variantes source différentes pour la même cible.

### Analyse : biais « premier match gagne » sur les 53 cas historiques

Même si les collisions n'existent plus, l'analyse des 53 cas archivés dans `fidelite-template-big-pickle.json` montre :

| Métrique | Valeur |
|---|---|
| Total collisions (audit kb024) | 53 |
| Gagnant + court que perdant(s) | **29 (55%)** |
| Gagnant + long que perdant(s) | 24 (45%) |
| À égalité | 0 |

Par cible :
- **`milieu` (36 cas)** : gagnant + court dans 23/36 (64%) — biais modéré vers le contenu le plus court
- **`admission` (16 cas)** : gagnant + court dans 5/16 (31%) — pas de biais vers le court, plutôt l'inverse
- **`salaires` (1 cas)** : gagnant + court — Chorégraphe, rapport 474x

**Verdict** : le biais « premier match gagne → contenu le plus court » est **confirmé pour `milieu`** (64% à perte d'info), **infirmé pour `admission`** (31% à perte d'info). L'effet global (55% à perte d'info) est modéré mais réel. La gravité individuelle peut être spectaculaire (Chorégraphe : 86 vs 40 756 caractères, facteur 474× ; `administration1` milieu : 26 vs 10 062 caractères, facteur 387×) même si la fréquence n'est pas majoritaire.

**Cependant, ce constat est désormais historique** : le changement de format des clés a supprimé toutes les collisions. Le nouveau problème est plus grave — une absence massive de correspondance plutôt qu'une collision mal résolue.

---

## 2. Test du filtre `_looks_like_section_title`

### Méthode

Testé statiquement sur les 352 titres de section distincts extraits des 485 fiches de `professions_details.json` (après parsing par `scrape_v2.py`). Pour les faux positifs, chaque titre passant le filtre est examiné pour des motifs suspects. Les faux négatifs ne peuvent être vérifiés exhaustivement sans accès au HTML brut, mais on peut compter les titres qui ne passent PAS le filtre.

### Résultats

**Faux positifs (titre détecté qui n'en est pas un) :**

| Titre | Occurrences | Raison |
|---|---|---|
| `UQTR`, `UQAM`, `UQAR`, `UQAC` | 3, 3, 1, 1 | Codes d'université, pas des titres de section — apparaissent comme sous-titres dans les sections Formation |
| `NOTE` | 1 | Trop court (4 lettres), unique — probable annotation, pas titre |
| `ENTREVUES` | 1 | Unique, pourrait être un titre légitime ou un artefact |
| `LES GRADES` | 1 | Unique, probablement un sous-titre légitime mais discutable |
| `DEP-D.E.C.`, `DEC-BAC` | plus. | Abréviations de parcours, pas des sections métier |

Titres avec artefacts d'encodage (5 titres contenant `�`) — techniquement des faux positifs car le contenu est corrompu, mais la cause est un problème d'encodage amont, pas du filtre lui-même.

**Faux négatifs (titre réel non détecté) :**

0 titre dans les données actuelles n'est en minuscules — tous les titres détectés sont en majuscules. Aucun faux négatif identifié dans les données. **Cependant**, cette analyse ne couvre pas les faux négatifs qui se produiraient au niveau du parsing HTML (titres réels dont le balisage `<b><u>` ne correspond pas à la convention attendue) — cela nécessiterait un échantillonnage direct sur le site live.

**Règle « 3-120 caractères »** : vérifiée sur tous les titres. Aucun titre ne dépasse 120 caractères. Aucun titre valide n'est en dessous de 3 (le plus court hors codes UQ est `NOTE` à 4 caractères).

---

## 3. Chaîne de clé vide après nettoyage

**Aucun cas trouvé.** Sur l'ensemble des 485 fiches, aucune clé brute ne devient vide après `key.lower().replace("\n", " ").strip()`. Aucun cas de clé ayant moins de 3 caractères alphabétiques non plus.

Ce test est passé — le cas théorique documenté dans `durcissement-scraper-generateur_v0_1.md §1b` n'existe pas dans les données actuelles.

---

## Résumé et implications

### Ce qui a changé depuis kb024

| Aspect | kb024 (audit, ancien format) | Aujourd'hui (format `scrape_v2.py`) |
|---|---|---|
| Clés avec `\n` | Oui | Non |
| Collisions détectées | 53 (milieu, admission, salaires) | **0** |
| `milieu` non couvert | Partiel (244/420) | **Total** (0/485) |
| `salaires` non couvert | 21/420 (5%) | **1/485 (0,2%)** |
| Données salariales perdues | ~399 fiches avec envoi vide | **~470 fiches avec SALAIRE ignoré** |
| Chorégraphe | Collision 86 vs 40 756 chars | **637 mots ignorés** (pas de collision, pas de match du tout) |

### Problèmes ouverts

1. **`SALAIRE` manquant dans section_key_map** : la clé réelle la plus fréquente (471/485) est absente des source_keys. Ajouter `'salaire'` à la liste couvrirait instantanément 97% des fiches pour la cible `salaires`.

2. **Apostrophe courbe** : `'EXIGENCES D''ADMISSION'` (apostrophe courbe, 337 fiches) n'est pas reconnue. Seule la variante à apostrophe droite (26 fiches) l'est. Ajouter les deux formes dans les source_keys.

3. **`milieu` sans aucune correspondance** : les clés réelles pertinentes sont `'CONDITIONS DE TRAVAIL'` (3), `'MILIEUX DE PRATIQUE'` (1), `'TYPES DE MILIEUX DE PRATIQUE...'` (1), `"MILIEUX D'INTERVENTION"` (1). Aucune n'est dans la section_key_map.

4. **`description` à 0%** : le filet de secours regex sur `intro` (lignes 253-282 de `generate.py`) existe encore et fonctionne, mais son taux de succès mesurable par correspondance directe est nul.

### Recommandation

Avant toute correction du `section_key_map` : soit mettre à jour les source_keys pour correspondre au format de `scrape_v2.py`, soit normaliser les clés en amont pour correspondre aux attentes du dictionnaire. L'état actuel (mapping conçu pour un format que le scraper ne produit plus) rend la section_key_map largement inefficace — pire que le bug kb024 initial, car le problème n'est plus une collision mal résolue mais une absence quasi complète de résolution pour plusieurs sections critiques.
