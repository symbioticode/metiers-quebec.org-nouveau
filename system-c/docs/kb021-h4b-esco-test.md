# KB021 — H4b-ESCO : correspondance sémantique GWA ↔ ESCO skills

**Branche** : experimental/h4b-esco-onet-closure
**Statut** : résultat produit (voir Amendement 1 ci-dessous, langue EN/EN).

## Question fermée

Les 41 GWA O*NET trouvent-elles une correspondance sémantique dans le
référentiel ESCO skills (13 890 concepts, indépendant de CNP/O*NET) à un
taux suffisant pour traiter GWA comme un sous-ensemble d'un alphabet plus
large et stable, plutôt qu'une taxonomie isolée ?

## Méthode (fixée avant tout résultat)

- **Corpus GWA** : 41 O*NET Generalized Work Activities,
  `data/reference/onet-genome-stability/30.3.json` (release la plus
  récente, branche phase2-systemc). Labels en anglais (artefact O*NET
  natif, jamais traduit).
- **Corpus ESCO** : ESCO v1.2.1, skills member concepts, récupérés via
  l'API REST officielle (`https://ec.europa.eu/esco/api/`), scheme
  `concept-scheme/member-skills`, traversée récursive de la hiérarchie
  (S/K/L/A → groupes → skills feuilles), langue anglaise. **13 094
  skills récupérés** sur 13 485 annoncés par l'API (13 890 dans
  VARIABLES.md, chiffre du CSV officiel) : 1 groupe (`skill/S1.5.3`)
  inaccessible (erreur serveur 500 côté ESCO, persistante,
  indépendante de la langue — non contournable), le reste de l'écart
  (~391 concepts) n'est pas expliqué et reste une limite documentée de
  cette extraction. Licence CC BY 4.0.
- **Modèle d'embedding** : `paraphrase-multilingual-mpnet-base-v2`
  (Sentence-Transformers), exécution locale (pas d'appel API externe
  pour l'inférence, pas de fuite de données).
- **Calcul** : embeddings normalisés des 41 GWA et des 13 094 skills
  ESCO, similarité cosinus, meilleur match ESCO retenu par GWA.
- **Métrique de couverture** : % des 41 GWA dont le meilleur match ESCO
  a une similarité ≥ 0.75 (seuil choisi arbitrairement mais fixé ici,
  non ajusté après résultat).

## Amendement 1 — correction langue (voir VARIABLES.md)

Le protocole initial pré-enregistrait une comparaison français↔français.
Erreur de fait : le corpus GWA fourni est en anglais uniquement. Correction
actée dans VARIABLES.md avant tout résultat : comparaison **GWA anglais ↔
ESCO anglais** (labels anglais du même dump ESCO v1.2.1, récupérés via
l'API en `language=en`). Ce test ne valide donc pas l'agnosticisme
linguistique de la méthode — un sprint séparé en français est prévu après
clôture de celui-ci.

## Écart au protocole — source ESCO via API plutôt que CSV

VARIABLES.md prescrivait un CSV téléchargé manuellement depuis
`esco.ec.europa.eu/en/use-esco/download`. Ce formulaire exige une adresse
courriel pour recevoir le lien de téléchargement (inscription), ce qui
sortait du périmètre autonome de ce test. Écart validé : utilisation de
l'API REST officielle ESCO (même source, même version v1.2.1, pas de
miroir tiers), avec la limite de couverture documentée ci-dessus
(13 094/13 890, ~94.3%).

## Seuils de clôture (pré-enregistrés)

- Couverture ≥ 90% → **CORROBORÉE** (candidat)
- Couverture < 70% → **RÉFUTÉE** (candidat)
- Entre les deux → **INDÉTERMINÉE**, diagnostic §5 méthodologie avant
  reformulation.

## Garde-fou anti-circularité

Le crosswalk ESCO↔O*NET (2022, Commission + US DOL) existe mais opère au
niveau OCCUPATIONS, pas SKILLS/GWA. Il n'a été ni téléchargé, ni
consulté, ni utilisé d'aucune façon dans ce test.

## Rapport au test clustering (TF-IDF)

Ce chantier est distinct de `kb021-h4b-clustering-test.md`. Les deux
résultats seront rapprochés au Sprint 4, jamais fusionnés en un seul
chiffre.

## Risque résiduel nommé d'avance

Un bon score de couverture GWA→ESCO montre une compatibilité
lexicale/sémantique entre deux taxonomies existantes — ça ne prouve pas
l'émergence *naturelle* d'un alphabet depuis un corpus brut (le
clustering non supervisé, lui, le ferait). H4b resterait donc
partiellement non testée même en cas de CORROBORÉE ici.

## Résultat

Couverture : **27/41 = 65.85%** au seuil de similarité cosinus ≥ 0.75.

JSON brut : `data/reference/esco/h4b-esco-results.json`
(41 GWA, meilleur match ESCO, score, + métadonnées de run).
Corpus ESCO utilisé : `data/reference/esco/esco-skills-en.json` (13 094
skills, labels anglais).

| GWA | Meilleur match ESCO | Similarité cosinus | ≥0.75 |
|---|---|---|---|
| Thinking Creatively | think creatively | 0.968 | oui |
| Repairing and Maintaining Mechanical Equipment | maintain mechanical equipment | 0.904 | oui |
| Developing and Building Teams | team building | 0.904 | oui |
| Repairing and Maintaining Electronic Equipment | maintain electronic equipment | 0.892 | oui |
| Getting Information | information extraction | 0.881 | oui |
| Working with Computers | use a computer | 0.865 | oui |
| Processing Information | analyse information processes | 0.862 | oui |
| Scheduling Work and Activities | follow work schedule | 0.861 | oui |
| Performing General Physical Activities | assist in performing physical exercises | 0.856 | oui |
| Coaching and Developing Others | develop a coaching style | 0.851 | oui |
| Inspecting Equipment, Structures, or Materials | inspect industrial equipment | 0.848 | oui |
| Analyzing Data or Information | analyse information processes | 0.839 | oui |
| Controlling Machines and Processes | operate automated process control | 0.839 | oui |
| Providing Consultation and Advice to Others | consultation methods | 0.815 | oui |
| Guiding, Directing, and Motivating Subordinates | exert a goal-oriented leadership role towards colleagues | 0.813 | oui |
| Drafting, Laying Out, and Specifying Technical Devices, Parts, and Equipment | design hardware | 0.810 | oui |
| Organizing, Planning, and Prioritizing Work | work in an organised manner | 0.808 | oui |
| Operating Vehicles, Mechanized Devices, or Equipment | operation of transport equipment | 0.807 | oui |
| Training and Teaching Others | advise on teaching methods | 0.805 | oui |
| Evaluating Information to Determine Compliance with Standards | follow interpreting quality standards | 0.796 | oui |
| Monitoring and Controlling Resources | manage resources | 0.796 | oui |
| Resolving Conflicts and Negotiating with Others | handle conflicts | 0.794 | oui |
| Staffing Organizational Units | personnel management | 0.789 | oui |
| Communicating with Supervisors, Peers, or Subordinates | communicate problems to senior colleagues | 0.789 | oui |
| Monitoring Processes, Materials, or Surroundings | monitor processing environment conditions | 0.784 | oui |
| Performing Administrative Activities | execute administration | 0.784 | oui |
| Making Decisions and Solving Problems | make decisions | 0.759 | oui |
| Documenting/Recording Information | write batch record documentation | 0.749 | non |
| Developing Objectives and Strategies | develop strategy to solve problems | 0.741 | non |
| Establishing and Maintaining Interpersonal Relationships | maintain working relationships | 0.737 | non |
| Performing for or Working Directly with the Public | speak about your work in public | 0.725 | non |
| Communicating with People Outside the Organization | communicate professionally with colleagues in other fields | 0.721 | non |
| Coordinating the Work and Activities of Others | work in an organised manner | 0.714 | non |
| Assisting and Caring for Others | assist community | 0.712 | non |
| Updating and Using Relevant Knowledge | maintain updated professional knowledge | 0.695 | non |
| Estimating the Quantifiable Characteristics of Products, Events, or Information | observe products' behaviour | 0.686 | non |
| Handling and Moving Objects | supervise artefact movement | 0.679 | non |
| Selling or Influencing Others | demonstrate motivation for sales | 0.672 | non |
| Interpreting the Meaning of Information for Others | communicate by use of interpretation in social services | 0.664 | non |
| Identifying Objects, Actions, and Events | determine event objectives | 0.647 | non |
| Judging the Qualities of Objects, Services, or People | characteristics of services | 0.564 | non |

## Verdict proposé

**RÉFUTÉE (candidat)**, selon les seuils pré-enregistrés dans
VARIABLES.md : couverture 65.85% < 70%.

Application mécanique du seuil de clôture fixé avant résultat : les 41
GWA O*NET, comparés aux 13 094 skills ESCO récupérées (labels anglais,
via API), ne trouvent un meilleur match à similarité cosinus ≥ 0.75 que
pour 27/41 (65.85%). Sous le plancher de 70%, le protocole conclut à
RÉFUTÉE plutôt qu'INDÉTERMINÉE.

**Qualificatifs à porter avant d'acter ce verdict au niveau du projet**
(pas des ajustements post-hoc du seuil — le seuil reste 0.75/70%/90% tel
que fixé — mais des limites de portée du test qui affectent
l'interprétation du chiffre) :

1. **Ce n'est pas le test prévu.** VARIABLES.md prévoyait français↔
   français ; ce résultat est anglais↔anglais (Amendement 1). Le test
   français reste à faire (sprint séparé, CSV fourni par Andrei) avant
   de considérer H4b-ESCO comme close dans une langue quelconque.
2. **Couverture ESCO incomplète** : 13 094/13 890 concepts (94.3%),
   1 groupe inaccessible pour raison technique documentée, ~391
   concepts manquants sans explication trouvée. Un score de couverture
   calculé sur l'ensemble complet pourrait différer légèrement (plus de
   candidats potentiels → coverage ne peut que monter ou rester égale,
   jamais baisser) mais l'écart est trop petit pour expliquer 65.85%
   vs 70%.
3. **Une seule paire embedding/seuil testée.** Le protocole interdit
   d'ajuster le seuil après résultat (respecté), mais ne dit rien sur
   la sensibilité du chiffre au choix du modèle d'embedding — un autre
   modèle multilingue pourrait donner une couverture différente. Ce
   n'est pas un ajustement post-hoc du test actuel, mais un diagnostic
   à documenter au §5 méthodologie si le statut INDÉTERMINÉE ou une
   reformulation sont un jour envisagés pour ce chantier.
4. **Rapport au test clustering (TF-IDF, kb021-h4b-clustering-test.md)**
   : non consulté ici, conformément au garde-fou. Le rapprochement des
   deux résultats est prévu au Sprint 4, pas avant.

Aucune modification de VARIABLES.md, du seuil, ni du corpus n'a été
faite après observation du résultat.
