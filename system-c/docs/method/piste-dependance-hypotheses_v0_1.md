# Piste — dépendance structurelle entre hypothèses

**Statut : PISTE, non prescriptive. Rien à construire par défaut.**
Ce document ne propose pas une architecture à adopter — il expose une logique possible, fondée sur des cadres théoriques établis, pour que System C juge lui-même si un besoin réel la justifie. L'arbitrage LLM en place reste inchangé quoi qu'il arrive.

---

## 1. Le problème, posé de façon générique

Quand un système évalue plusieurs hypothèses candidates sur un même objet, chaque hypothèse est généralement traitée isolément : vérifiée, confirmée ou infirmée pour elle-même. Rien, dans une évaluation isolée, ne répond à la question suivante : **la fermeture (ou l'infirmation) d'une hypothèse a-t-elle une conséquence sur le statut d'une autre hypothèse qui lui est liée ?**

Ce n'est pas un problème de vérification (est-ce que l'hypothèse A est vraie) — c'est un problème de **structure entre affirmations déjà évaluées**. Un système peut avoir une méthode de vérification parfaite pour chaque hypothèse prise seule, et rester complètement aveugle à ce deuxième problème.

## 2. Trois familles théoriques, à ne pas confondre entre elles

### 2.1 Logique à quatre valeurs (Belnap, 1977)

Résume l'état épistémique d'**une** affirmation à un instant donné, face à des preuves qui peuvent être absentes, cohérentes ou contradictoires : vrai, faux, les deux (contradiction), ni l'un ni l'autre (silence). C'est un outil de **classification d'état**, pas de raisonnement sur plusieurs affirmations liées entre elles. Il ne dit rien sur la relation entre deux hypothèses distinctes — seulement sur l'état de chacune, séparément.

### 2.2 Réseaux bayésiens et propagation de croyance (Pearl)

Un cadre où les hypothèses sont représentées comme des nœuds dans un graphe orienté, avec des arêtes explicites de dépendance. Changer la probabilité d'un nœud modifie, par propagation le long des arêtes, la probabilité des nœuds qui en dépendent. C'est le seul des trois cadres qui modélise **directement** la question posée en §1 : la dépendance structurelle entre hypothèses, pas seulement l'état de chacune.

### 2.3 Combinaison de sources et localisation du conflit (Dempster-Shafer ; PCR5, Dezert-Smarandache)

Quand plusieurs sources indépendantes produisent chacune une évaluation (une masse de croyance) sur un même ensemble d'hypothèses, ce cadre définit une règle pour les combiner en une seule évaluation, et surtout pour **localiser** précisément quelles paires de sources, sur quelles hypothèses, sont en désaccord — plutôt que de se contenter d'un score global de conflit. C'est utile uniquement si l'évaluation d'une hypothèse vient de plusieurs sources distinctes à réconcilier ; inutile s'il n'y a jamais qu'une seule source par hypothèse.

**Les trois ne se substituent pas l'un à l'autre.** Belnap répond à « quel est l'état de cette affirmation ». Pearl répond à « qu'est-ce que ça change pour les affirmations liées ». Dempster-Shafer/PCR5 répond à « comment concilier plusieurs évaluateurs indépendants sur la même affirmation, et où exactement ils divergent ». Un système peut avoir besoin d'un seul de ces trois éléments, de deux, ou d'aucun — ça dépend uniquement de la forme réelle de ses données.

## 3. Ce qu'une architecture minimale pourrait ressembler, si le besoin est confirmé

Uniquement à titre d'illustration — pas une spécification :

- Un **graphe de dépendances** entre hypothèses : chaque hypothèse déclare, si elle le sait, quelles autres hypothèses sa fermeture affecte. Structure la plus simple possible — un index, pas un moteur d'inférence complet.
- Un **état résumé par hypothèse**, dérivé de son évaluation courante — jamais l'inverse (l'état résumé ne doit jamais être la source de vérité, seulement une lecture de la vérification réelle).
- Une **fonction de combinaison**, activée seulement si une même hypothèse reçoit des évaluations de plusieurs sources distinctes — sinon elle ne sert à rien et ne devrait pas exister.

Si un jour ceci devait devenir du code, la forme la plus honnête serait un utilitaire autonome et minimal (à la manière d'un `kb.py` local) — jamais un service, jamais une dépendance externe, jamais quelque chose qui remplace l'arbitrage LLM déjà en place.

## 4. Garde-fou avant toute implémentation

Ne rien construire de ceci tant qu'un cas réel et nommé n'a pas démontré qu'une hypothèse fermée dans System C aurait dû faire rouvrir ou reconsidérer une autre hypothèse, et que cette omission a eu une conséquence observable. Sans un tel cas, ce document reste une carte de ce qui existe dans la littérature — pas une dette à résorber.

---

## Références (littérature d'autorité — pas des sources à importer)

- Belnap, N. (1977) — *A Useful Four-Valued Logic*
- Pearl, J. — réseaux bayésiens et propagation de croyance (belief propagation)
- Dezert, J. & Smarandache, F. — PCR5 (redistribution proportionnelle du conflit)
- CLAIM (protocole d'échange épistémique multi-agents, hors de ce projet) — illustration existante de la combinaison des trois cadres ci-dessus dans une architecture opérationnelle, citée ici pour référence, pas comme source à reproduire
- SECS (protocole comparatif inter-substrats, hors de ce projet) — constat empirique que la convergence entre évaluateurs indépendants n'est jamais une conclusion en soi, et que la divergence localisée porte plus d'information que l'accord

---

*Note v0.1 · PISTE, non prescriptive · à évaluer par System C selon ses propres besoins*
