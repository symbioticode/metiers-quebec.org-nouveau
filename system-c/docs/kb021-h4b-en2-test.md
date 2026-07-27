# KB021 — H4b-EN2 : diagnostic corpus complet (GWA EN ↔ ESCO EN, CSV complet)

**Branche** : experimental/h4b-esco-en-full-corpus
**Statut** : méthode pré-enregistrée, résultat non encore produit.

## Objet

Sprint 5 diagnostique. Isole la variable "complétude du corpus ESCO" de
la variable "langue" dans l'écart H4b-EN (65.85%) vs H4b-FR (80.49%,
hors marge de reproductibilité ±10pt).

## Différence unique vs H4b-EN

Source ESCO anglaise remplacée : CSV officiel complet (`skills_en.csv`,
~13 939 concepts uniques attendus, comme le corpus FR) au lieu de l'API
REST avec 1 groupe en échec (`S1.5.3`, 13 094 skills récupérés). GWA,
modèle d'embedding, seuil de similarité individuel : identiques à
H4b-EN.

## Question fermée

Avec un corpus EN aussi complet que le corpus FR, la couverture EN se
rapproche-t-elle de 80.49% (FR) — indiquant que l'écart initial était un
artefact de récupération de données — ou reste-t-elle proche de 65.85%
— indiquant un vrai signal linguistique ?

## Méthode (fixée avant tout résultat)

- **Corpus GWA** : 41 O*NET Generalized Work Activities,
  `data/reference/onet-genome-stability/30.3.json`, labels en anglais —
  identiques à H4b-EN et H4b-FR.
- **Corpus ESCO** : `data/reference/esco/skills_en.csv`, déjà committé
  sur cette branche, CSV officiel complet v1.2.1, colonne
  `preferredLabel` (anglais).
- **Modèle d'embedding** : `paraphrase-multilingual-mpnet-base-v2` —
  identique aux deux sprints précédents.
- **Calcul** : embeddings normalisés des 41 GWA et des skills ESCO
  (`preferredLabel`, anglais), similarité cosinus, meilleur match ESCO
  retenu par GWA.
- **Métrique de couverture** : % des 41 GWA dont le meilleur match ESCO
  a une similarité ≥ 0.75 (seuil individuel identique aux sprints
  précédents, non ajusté après résultat).

## Seuils d'interprétation (fixés avant résultat, spécifiques à ce sprint)

- Couverture EN2 dans **[70.85%, 90.13%]** (±10pt autour de 80.49% FR) →
  **ARTEFACT CORPUS CONFIRMÉ** : l'écart initial était dû à la donnée
  manquante, pas à la langue. H4b-EN (API) est invalidée comme mesure de
  référence ; H4b-EN2 la remplace.
- Couverture EN2 dans **[55.85%, 75.85%]** (±10pt autour de 65.85% EN
  original) → **CORPUS SANS EFFET** : l'écart EN/FR est un vrai signal
  linguistique, à traiter comme résultat de fond au Sprint 4 révisé.
- Entre les deux (zone de chevauchement 70.85–75.85%) ou hors des deux
  plages → **NI L'UN NI L'AUTRE** clairement : rouvrir un diagnostic, ne
  pas forcer une conclusion.

Ce sprint n'utilise **pas** les seuils RÉFUTÉE/CORROBORÉE/INDÉTERMINÉE
de H4b-EN/H4b-FR — question différente (artefact de corpus vs
correspondance sémantique).

## Garde-fou

Pas de consultation de `kb021-h4b-esco-test.md` (H4b-EN, API) ni de
`kb021-h4b-fr-test.md` (H4b-FR) avant production du résultat brut de ce
sprint. Seuls les deux chiffres de référence (65.85% et 80.49%) sont
transmis via `VARIABLES.md`, pas les KB complets. Pas d'accès non plus à
`kb021.md` ni `kb021-h4b-clustering-test.md`.

## Résultat

*(à remplir après exécution — voir commit "résultat — H4b-EN2")*

## Verdict proposé

*(à remplir après résultat — voir commit "verdict proposé — H4b-EN2")*
