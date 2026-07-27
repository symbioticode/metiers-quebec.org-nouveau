# KB021 — H4b-EN2 : diagnostic corpus complet (GWA EN ↔ ESCO EN, CSV complet)

**Branche** : experimental/h4b-esco-en-full-corpus
**Statut** : résultat produit.

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

Couverture : **28/41 = 68.29%** au seuil de similarité cosinus ≥ 0.75.

JSON brut : `data/reference/esco/h4b-en2-results.json` (même structure
que H4b-EN et H4b-FR). Corpus ESCO utilisé : `data/reference/esco/skills_en.csv`
(13 939 concepts uniques, colonne `preferredLabel`, dédupliqué par
`conceptUri` — 13 960 lignes brutes contenaient des doublons d'URI).

| GWA (EN) | Meilleur match ESCO (EN, CSV complet) | Similarité cosinus | ≥0.75 |
|---|---|---|---|
| Thinking Creatively | think creatively | 0.968 | oui |
| Repairing and Maintaining Mechanical Equipment | maintain mechanical equipment | 0.904 | oui |
| Developing and Building Teams | team building | 0.904 | oui |
| Handling and Moving Objects | move objects | 0.892 | oui |
| Repairing and Maintaining Electronic Equipment | maintain electronic equipment | 0.892 | oui |
| Getting Information | information extraction | 0.881 | oui |
| Processing Information | analyse information processes | 0.862 | oui |
| Scheduling Work and Activities | follow work schedule | 0.861 | oui |
| Performing General Physical Activities | assist in performing physical exercises | 0.856 | oui |
| Coaching and Developing Others | develop a coaching style | 0.851 | oui |
| Inspecting Equipment, Structures, or Materials | inspect industrial equipment | 0.848 | oui |
| Analyzing Data or Information | analyse information processes | 0.839 | oui |
| Controlling Machines and Processes | operate automated process control | 0.839 | oui |
| Resolving Conflicts and Negotiating with Others | resolve conflicts | 0.836 | oui |
| Providing Consultation and Advice to Others | consultation methods | 0.815 | oui |
| Drafting, Laying Out, and Specifying Technical Devices, Parts, and Equipment | design hardware | 0.810 | oui |
| Organizing, Planning, and Prioritizing Work | work in an organised manner | 0.808 | oui |
| Operating Vehicles, Mechanized Devices, or Equipment | operation of transport equipment | 0.807 | oui |
| Training and Teaching Others | advise on teaching methods | 0.805 | oui |
| Evaluating Information to Determine Compliance with Standards | follow interpreting quality standards | 0.796 | oui |
| Monitoring and Controlling Resources | manage resources | 0.796 | oui |
| Staffing Organizational Units | personnel management | 0.789 | oui |
| Communicating with Supervisors, Peers, or Subordinates | communicate problems to senior colleagues | 0.789 | oui |
| Working with Computers | computer technology | 0.785 | oui |
| Monitoring Processes, Materials, or Surroundings | monitor processing environment conditions | 0.784 | oui |
| Performing Administrative Activities | office administration | 0.781 | oui |
| Guiding, Directing, and Motivating Subordinates | leadership principles | 0.772 | oui |
| Making Decisions and Solving Problems | make decisions | 0.759 | oui |
| Documenting/Recording Information | write batch record documentation | 0.749 | non |
| Developing Objectives and Strategies | develop strategy to solve problems | 0.741 | non |
| Coordinating the Work and Activities of Others | collaborate in company's daily operations | 0.730 | non |
| Performing for or Working Directly with the Public | speak about your work in public | 0.725 | non |
| Communicating with People Outside the Organization | communicate professionally with colleagues in other fields | 0.721 | non |
| Assisting and Caring for Others | assist community | 0.712 | non |
| Establishing and Maintaining Interpersonal Relationships | develop therapeutic relationships | 0.711 | non |
| Updating and Using Relevant Knowledge | maintain updated professional knowledge | 0.695 | non |
| Selling or Influencing Others | demonstrate motivation for sales | 0.672 | non |
| Estimating the Quantifiable Characteristics of Products, Events, or Information | process qualitative information | 0.668 | non |
| Interpreting the Meaning of Information for Others | critically evaluate information and its sources | 0.663 | non |
| Identifying Objects, Actions, and Events | determine event objectives | 0.647 | non |
| Judging the Qualities of Objects, Services, or People | characteristics of services | 0.564 | non |

## Verdict proposé

**CORPUS SANS EFFET**, selon les seuils d'interprétation pré-enregistrés
dans VARIABLES.md : couverture EN2 = 68.29%, dans la plage
[55.85%, 75.85%] (±10pt autour de 65.85%, le chiffre EN original via
API partielle).

Application mécanique des seuils fixés avant résultat : avec un corpus
ESCO anglais rendu aussi complet que le corpus français (13 939 concepts
uniques via CSV officiel, contre 13 094 via l'API partiellement en
échec), la couverture reste proche du chiffre EN original (68.29% vs
65.85%, +2.44 points) et **hors** de la plage [70.85%, 90.13%] qui
aurait confirmé un artefact de récupération de données. La complétude du
corpus n'explique donc pas l'écart observé entre EN (65.85%) et FR
(80.49%) : ce dernier reste, à ce stade, un signal potentiellement
linguistique plutôt qu'un artefact de données manquantes côté anglais.

**Qualificatifs à porter avant d'acter ce verdict au niveau du projet**
(pas des ajustements post-hoc des seuils — ceux-ci restent tels que
fixés — mais des limites de portée qui affectent l'interprétation) :

1. **Ce sprint isole la complétude du corpus, pas d'autres facteurs.**
   "CORPUS SANS EFFET" signifie que *cette* variable-là (nombre de
   concepts ESCO disponibles) n'explique pas l'écart EN/FR. Cela ne
   confirme pas positivement que la langue est la cause — seulement que
   la complétude du corpus est écartée comme cause probable. D'autres
   facteurs possibles (couverture du CSV FR différente en nature, pas
   seulement en volume ; biais du modèle d'embedding vis-à-vis du
   français vs l'anglais) ne sont pas testés ici.
2. **Léger delta positif non nul** (68.29% vs 65.85% EN original,
   +2.44 points) : dans le sens attendu si la complétude avait un effet
   partiel, mais l'amplitude reste largement à l'intérieur de la marge
   ±10pt — donc non distinguable du bruit de mesure selon le protocole
   pré-enregistré.
3. **Dédoublonnage du CSV** : `skills_en.csv` contenait 13 960 lignes
   brutes pour 13 939 URIs uniques (21 doublons). Un même skill listé
   deux fois n'aurait pas changé le résultat (le meilleur match par GWA
   est invariant à la duplication d'une entrée), mais le nombre de
   concepts distincts rapporté ci-dessus utilise le total dédoublonné.
4. **Garde-fou respecté** : ni `kb021-h4b-esco-test.md` (H4b-EN) ni
   `kb021-h4b-fr-test.md` (H4b-FR) n'ont été consultés ; seuls les deux
   chiffres de référence (65.85% et 80.49%) transmis via VARIABLES.md
   ont servi à définir les plages d'interprétation.

Aucune modification de VARIABLES.md, des seuils, ni du corpus n'a été
faite après observation du résultat.
