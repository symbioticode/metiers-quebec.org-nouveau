# KB021 — H4b-FR : réplication translinguistique GWA (EN) ↔ ESCO skills (FR)

**Branche** : experimental/h4b-esco-fr-replication
**Statut** : méthode pré-enregistrée, résultat non encore produit.

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

*(à remplir après exécution — voir commit "résultat — H4b-FR")*

## Verdict proposé

*(à remplir après résultat — voir commit "verdict proposé — H4b-FR")*
