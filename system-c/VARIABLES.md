# H4b-FR — Seuil pré-enregistré (réplication translinguistique)

**Branche** : experimental/h4b-esco-fr-replication
**Chantier parallèle** : H4b-EN (experimental/h4b-esco-onet-closure) — CLOS,
verdict RÉFUTÉE (candidat), 27/41 GWA ≥ 0.75, couverture 65.85%.

**Question fermée** : le taux de couverture GWA↔ESCO obtenu en anglais
(65.85%) se reproduit-il en français, à ±10 points de pourcentage
(donc entre 55.85% et 75.85%) ? Hors de cette marge → l'écart n'est pas
du bruit de mesure, c'est un résultat en soi (langue, modèle, ou
couverture ESCO en cause — à diagnostiquer, pas à ignorer).

**Différence méthodologique volontaire vs H4b-EN** : les 41 GWA restent
en ANGLAIS (source O*NET originale, aucune traduction — cf. Amendement 1
de H4b-EN). Seul le référentiel ESCO cible change : anglais → français.
Ce n'est donc pas un test franco-français symétrique, mais anglais-GWA
↔ français-ESCO — teste si le modèle multilingue relie correctement les
deux à travers la frontière de langue, condition nécessaire avant
d'envisager un jour des GWA eux-mêmes traduits.

**Source ESCO française** : system-c/data/reference/esco/skills_fr.csv,
déjà committé (182d7a6), 37 038 lignes de données (+ en-tête), package
v1.2.1, téléchargé manuellement le 2026-07-27.

**Métrique et seuils** : identiques à H4b-EN — cosinus ≥ 0.75 par GWA,
clôture ≥90%/<70%, PLUS la marge de reproductibilité ±10 points définie
ci-dessus pour le rapprochement EN/FR (Sprint 4 commun).

**Modèle d'embedding** : paraphrase-multilingual-mpnet-base-v2 — identique
à H4b-EN, pour que seule la langue varie entre les deux tests, pas le
modèle.

**Garde-fou hérité de H4b-EN** : ne pas consulter kb021.md,
kb021-h4b-clustering-test.md, ni le résultat H4b-EN
(kb021-h4b-esco-test.md sur l'autre branche) avant d'avoir produit son
propre résultat — l'isolement de construction s'applique aussi entre
sprints parallèles du même chantier, pas seulement vs l'historique
général.
