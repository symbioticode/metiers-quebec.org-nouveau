# KB021 — H4b-FR : réplication translinguistique GWA (EN) ↔ ESCO skills (FR)

**Branche** : experimental/h4b-esco-fr-replication
**Statut** : résultat produit.

## Question fermée

Le taux de couverture GWA↔ESCO obtenu en anglais (65.85%, chantier
parallèle H4b-EN) se reproduit-il en français, à ±10 points de
pourcentage (donc entre 55.85% et 75.85%) ? Hors de cette marge, l'écart
n'est pas du bruit de mesure — c'est un résultat en soi (langue, modèle,
ou couverture ESCO en cause) à diagnostiquer, pas à ignorer.

## Différence méthodologique volontaire vs H4b-EN

Les 41 GWA restent en **anglais** (source O*NET originale, aucune
traduction). Seul le référentiel ESCO cible change : anglais → français.
Ce n'est donc pas un test franco-français symétrique, mais
anglais-GWA ↔ français-ESCO — teste si le modèle multilingue relie
correctement les deux à travers la frontière de langue, condition
nécessaire avant d'envisager un jour des GWA eux-mêmes traduits.

## Méthode (fixée avant tout résultat)

- **Corpus GWA** : 41 O*NET Generalized Work Activities,
  `data/reference/onet-genome-stability/30.3.json`, labels en anglais,
  non traduits — identiques à H4b-EN.
- **Corpus ESCO** : `data/reference/esco/skills_fr.csv`, déjà committé
  sur cette branche, package v1.2.1, 37 038 lignes de données (+
  en-tête), téléchargé manuellement le 2026-07-27. Labels français
  utilisés : colonne `preferredLabel`.
- **Modèle d'embedding** : `paraphrase-multilingual-mpnet-base-v2`
  (Sentence-Transformers), identique à H4b-EN — seule la langue du
  corpus ESCO varie entre les deux tests, pas le modèle.
- **Calcul** : embeddings normalisés des 41 GWA (anglais) et des skills
  ESCO (`preferredLabel`, français), similarité cosinus, meilleur match
  ESCO retenu par GWA.
- **Métrique de couverture** : % des 41 GWA dont le meilleur match ESCO
  a une similarité ≥ 0.75 (seuil identique à H4b-EN, non ajusté après
  résultat).

## Seuils de clôture (pré-enregistrés, identiques à H4b-EN)

- Couverture ≥ 90% → **CORROBORÉE** (candidat)
- Couverture < 70% → **RÉFUTÉE** (candidat)
- Entre les deux → **INDÉTERMINÉE**, diagnostic §5 méthodologie avant
  reformulation.

## Marge de reproductibilité EN/FR (spécifique à ce sprint)

Le résultat H4b-EN (65.85%) sert de référence pour une marge de ±10
points de pourcentage (55.85%–75.85%). Hors de cette marge, l'écart
anglais/français est un résultat à part entière, pas du bruit — sans que
cela ne modifie les seuils de clôture RÉFUTÉE/CORROBORÉE/INDÉTERMINÉE
ci-dessus, qui restent appliqués indépendamment.

## Garde-fou

Hérité de H4b-EN : pas d'accès à `kb021.md`, `kb021-h4b-clustering-test.md`,
ni au fichier de résultat H4b-EN (`kb021-h4b-esco-test.md` sur l'autre
branche) avant d'avoir produit le résultat propre à ce sprint. Le
chiffre de référence 65.85% cité ci-dessus provient de VARIABLES.md
(déjà transmis comme donnée pré-enregistrée), pas d'une consultation
directe du fichier de résultat H4b-EN.

## Rapport au test clustering (TF-IDF)

Ce chantier est distinct de `kb021-h4b-clustering-test.md`. Le
rapprochement EN/FR et clustering est prévu au Sprint 4 commun, après
clôture indépendante des deux branches.

## Résultat

Couverture : **33/41 = 80.49%** au seuil de similarité cosinus ≥ 0.75.

JSON brut : `data/reference/esco/h4b-fr-results.json` (même structure que
`h4b-esco-results.json` de H4b-EN pour comparaison automatisée
ultérieure). Corpus ESCO utilisé : `data/reference/esco/skills_fr.csv`
(13 960 lignes valides, colonne `preferredLabel`).

| GWA (EN) | Meilleur match ESCO (FR) | Similarité cosinus | ≥0.75 |
|---|---|---|---|
| Performing Administrative Activities | effectuer des tâches administratives | 0.957 | oui |
| Thinking Creatively | avoir un esprit créatif | 0.927 | oui |
| Controlling Machines and Processes | contrôler le fonctionnement de machines | 0.918 | oui |
| Training and Teaching Others | instruire autrui | 0.895 | oui |
| Resolving Conflicts and Negotiating with Others | résoudre les conflits | 0.892 | oui |
| Getting Information | extraction de l'information | 0.888 | oui |
| Developing and Building Teams | construire un esprit d'équipe | 0.886 | oui |
| Organizing, Planning, and Prioritizing Work | organiser le travail | 0.883 | oui |
| Handling and Moving Objects | déplacer des objets | 0.881 | oui |
| Providing Consultation and Advice to Others | conseiller d'autres personnes | 0.880 | oui |
| Performing General Physical Activities | exercer un entraînement physique | 0.876 | oui |
| Analyzing Data or Information | effectuer une analyse de données | 0.874 | oui |
| Repairing and Maintaining Electronic Equipment | réparer des composants électroniques | 0.872 | oui |
| Inspecting Equipment, Structures, or Materials | inspecter des équipements industriels | 0.871 | oui |
| Repairing and Maintaining Mechanical Equipment | réparer des équipements industriels | 0.860 | oui |
| Coaching and Developing Others | coacher des jeunes | 0.857 | oui |
| Developing Objectives and Strategies | transposer la stratégie en actions et objectifs | 0.848 | oui |
| Coordinating the Work and Activities of Others | coordonner des activités de ramonage | 0.842 | oui |
| Communicating with Supervisors, Peers, or Subordinates | communiquer les problèmes à ses supérieurs | 0.840 | oui |
| Processing Information | analyser des processus d'information | 0.840 | oui |
| Drafting, Laying Out, and Specifying Technical Devices, Parts, and Equipment | concevoir des équipements utilitaires | 0.832 | oui |
| Staffing Organizational Units | gérer l'administration du personnel | 0.824 | oui |
| Making Decisions and Solving Problems | résoudre les problèmes | 0.824 | oui |
| Operating Vehicles, Mechanized Devices, or Equipment | entretenir des équipements mécaniques | 0.821 | oui |
| Documenting/Recording Information | archiver la documentation relative à l'œuvre | 0.794 | oui |
| Monitoring Processes, Materials, or Surroundings | surveiller la production d'une installation | 0.792 | oui |
| Working with Computers | utiliser des systèmes d'ingénierie assistés par ordinateur | 0.790 | oui |
| Monitoring and Controlling Resources | gérer des ressources | 0.790 | oui |
| Scheduling Work and Activities | prendre en considération les fuseaux horaires dans l'exécution du travail | 0.789 | oui |
| Communicating with People Outside the Organization | communiquer avec d'autres personnes importantes pour les usagers | 0.783 | oui |
| Evaluating Information to Determine Compliance with Standards | élaborer des normes d'information | 0.782 | oui |
| Guiding, Directing, and Motivating Subordinates | principes de leadership | 0.780 | oui |
| Assisting and Caring for Others | apporter son aide dans des situations d'urgence | 0.771 | oui |
| Selling or Influencing Others | argumentaire de vente | 0.733 | non |
| Establishing and Maintaining Interpersonal Relationships | développer des relations thérapeutiques | 0.731 | non |
| Interpreting the Meaning of Information for Others | techniques de réflexion personnelle fondées sur le retour d'information | 0.718 | non |
| Updating and Using Relevant Knowledge | tenir à jour ses connaissances professionnelles | 0.687 | non |
| Estimating the Quantifiable Characteristics of Products, Events, or Information | traiter des informations qualitatives | 0.681 | non |
| Performing for or Working Directly with the Public | parler de son œuvre en public | 0.669 | non |
| Judging the Qualities of Objects, Services, or People | évaluer un caractère | 0.633 | non |
| Identifying Objects, Actions, and Events | évaluer des évènements | 0.606 | non |

## Verdict proposé

*(à remplir — voir commit "verdict proposé — H4b-FR")*
