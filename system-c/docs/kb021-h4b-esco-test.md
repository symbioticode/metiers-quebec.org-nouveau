# KB021 — H4b-ESCO : correspondance sémantique GWA ↔ ESCO skills

**Branche** : experimental/h4b-esco-onet-closure
**Statut** : méthode pré-enregistrée, résultat non encore produit.

## Question fermée

Les 41 GWA O*NET trouvent-elles une correspondance sémantique dans le
référentiel ESCO skills (13 890 concepts, indépendant de CNP/O*NET) à un
taux suffisant pour traiter GWA comme un sous-ensemble d'un alphabet plus
large et stable, plutôt qu'une taxonomie isolée ?

## Méthode (fixée avant tout résultat)

- **Corpus GWA** : 41 O*NET Generalized Work Activities,
  `data/reference/onet-genome-stability/` (branche phase2-systemc).
- **Corpus ESCO** : dump officiel v1.2.1 (déc. 2025), 13 890 concepts
  skills/knowledge/competence, CSV, langue française, téléchargé
  directement depuis https://esco.ec.europa.eu/en/use-esco/download
  (pas de miroir tiers). Licence CC BY 4.0.
- **Modèle d'embedding** : `paraphrase-multilingual-mpnet-base-v2`
  (Sentence-Transformers) — choisi pour comparaison français↔français,
  exécution locale (pas d'appel API externe, pas de fuite de données).
- **Calcul** : embeddings des 41 GWA et des 13 890 skills ESCO,
  similarité cosinus, meilleur match ESCO retenu par GWA.
- **Métrique de couverture** : % des 41 GWA dont le meilleur match ESCO
  a une similarité ≥ 0.75 (seuil choisi arbitrairement mais fixé ici,
  non ajusté après résultat).

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

*(à remplir après exécution — voir commit "résultat — H4b-ESCO")*

## Verdict proposé

*(à remplir après résultat — voir commit "verdict proposé — H4b-ESCO")*
