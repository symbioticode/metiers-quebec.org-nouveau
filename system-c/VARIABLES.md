# H4b-EN2 — Seuil pré-enregistré (diagnostic corpus complet)

**Branche** : experimental/h4b-esco-en-full-corpus
**Objet** : Sprint 5 diagnostique, isole la variable "complétude du corpus
ESCO" de la variable "langue" dans l'écart H4b-EN (65.85%) vs H4b-FR
(80.49%, hors marge ±10pt).

**Différence unique vs H4b-EN** : source ESCO anglaise remplacée —
CSV officiel complet (skills_en.csv, ~13 939 concepts uniques attendus,
comme le FR) au lieu de l'API avec 1 groupe en échec (S1.5.3, 13 094
skills). GWA, modèle d'embedding, seuil, tout le reste : identique à
H4b-EN.

**Question fermée** : avec un corpus EN aussi complet que le corpus FR,
la couverture EN se rapproche-t-elle de 80.49% (FR) — indiquant que
l'écart initial était un artefact de récupération de données — ou
reste-t-elle proche de 65.85% — indiquant un vrai signal linguistique ?

**Seuils d'interprétation (fixés avant résultat)** :
- Couverture EN2 dans [70.85%, 90.13%] (±10pt autour de 80.49% FR) →
  ARTEFACT CORPUS CONFIRMÉ : l'écart initial était dû à la donnée
  manquante, pas à la langue. H4b-EN (API) est invalidée comme mesure
  de référence ; H4b-EN2 la remplace.
- Couverture EN2 dans [55.85%, 75.85%] (±10pt autour de 65.85% EN
  original) → CORPUS SANS EFFET : l'écart EN/FR est un vrai signal
  linguistique, à traiter comme résultat de fond au Sprint 4 révisé.
- Entre les deux (zones qui se chevauchent : 70.85–75.85%) ou hors des
  deux plages → NI L'UN NI L'AUTRE clairement : rouvrir un diagnostic,
  ne pas forcer une conclusion.

**Modèle, GWA, threshold de couverture individuel (0.75)** : identiques à
H4b-EN et H4b-FR, aucun changement.

**Garde-fou** : ne pas consulter kb021-h4b-esco-test.md (H4b-EN, API) ni
kb021-h4b-fr-test.md (H4b-FR) avant de produire son propre résultat brut
— seuls les deux chiffres de référence (65.85% et 80.49%) sont transmis
via ce VARIABLES.md, pas les KB complets.
