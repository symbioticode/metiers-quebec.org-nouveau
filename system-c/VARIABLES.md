# H4b-ESCO — Seuil pré-enregistré

**Branche** : experimental/h4b-esco-onet-closure
**Question fermée** : les compétences O*NET GWA (41) trouvent-elles une
correspondance sémantique dans le référentiel ESCO skills (13 890
concepts, indépendant de CNP/O*NET) à un taux suffisant pour traiter GWA
comme un sous-ensemble d'un alphabet plus large et stable, plutôt qu'une
taxonomie isolée ?

**Métrique de couverture (fixée avant tout résultat)** :
Pour chaque GWA (41), calculer la similarité cosinus embeddings avec les
13 890 skills ESCO, retenir le meilleur match. Couverture = % des 41 GWA
dont le meilleur match ESCO a une similarité ≥ 0.75 (seuil de similarité
lui-même choisi arbitrairement mais fixé ici, pas ajusté après résultat).

**Seuil de clôture** : couverture ≥ 90% → CORROBORÉE (candidat) ;
couverture < 70% → RÉFUTÉE (candidat) ; entre les deux → INDÉTERMINÉE,
diagnostic §5 méthodologie avant reformulation.

**Modèle d'embedding** : multilingue requis (comparaison français GWA ↔
français ESCO) — à fixer précisément au Sprint 2, pas ici.

**Source ESCO** : dump officiel v1.2.1 (déc. 2025), 13 890 concepts,
téléchargé en CSV, langue française, depuis
https://esco.ec.europa.eu/en/use-esco/download — licence CC BY 4.0.

**Garde-fou anti-circularité** : un crosswalk ESCO↔O*NET existe déjà
(2022, Commission + US DOL) mais opère au niveau OCCUPATIONS, pas au
niveau SKILLS/GWA. Interdiction explicite de le consulter ou de l'utiliser
comme donnée d'entrée ou de calibration pour ce test.

**Rapport à kb021-h4b-clustering-test.md (TF-IDF)** : ce chantier est un
test distinct, pas une suite. Les deux résultats seront rapprochés au
Sprint 4, jamais fusionnés en un seul chiffre.

**Risque résiduel nommé d'avance** : un bon score de couverture GWA→ESCO
montre une compatibilité lexicale/sémantique entre deux taxonomies
existantes — ça ne prouve toujours pas l'émergence *naturelle* d'un
alphabet depuis un corpus brut (le clustering non supervisé, lui, le
ferait) ; H4b resterait donc partiellement non testée même en cas de
CORROBORÉE ici.
