# kb013 — Méthodologie et outillage de détection d'invariants
## Cas d'étude : migration metiers-quebec.org (Phase 1)

**Statut** : Phase 1 close. Ce document clôt le Projet #1 et pointe vers
la Phase 2 (System C), qui démarre comme projet distinct.

---

## Résumé

Ce rapport documente une méthodologie développée pendant la tentative de
migration du site `metiers-quebec.org` (site statique maintenu manuellement
depuis 2009) vers une représentation structurée queryable. La migration
elle-même n'a pas été certifiée complète — voir §5. Ce qui en ressort et
qui a une valeur propre, indépendante de ce projet précis, c'est une
méthode reproductible de détection d'invariants violés dans un pipeline
de transformation de données, développée et validée sur des cas réels
pendant ce travail.

## 1. Contexte et intention de départ

Le projet a démarré comme une délégation pragmatique : moderniser un site
web ancien mais toujours pertinent et bien référencé, sans intention de
recherche a priori. La question de recherche — *le sens reste-t-il le
même quand le conteneur change ?* — a émergé en cours de route, à partir
d'un bug concret et mesurable, pas d'une hypothèse posée d'avance.

## 2. Ce qui a été fait

### 2.1 Extraction et mesure de perte (Jour 1)

Le générateur historique du site (`generate.py`) contenait un dictionnaire
de mapping (`SECTION_MAP`) figé avant lecture du corpus, avec appariement
par sous-chaîne et priorité au premier match. Un script de mesure
(`coverage_split.py`) a quantifié la perte réelle :

| Concept | Présent dans la source | Présent dans le pipeline | Perte |
|---|---|---|---|
| salaire | 85% | 5% | 94% |
| formation | 95% | 6% | 94% |
| qualités | 60% | 3% | 96% |
| placement | 58% | 2% | 97% |
| marché | 73% | 9% | 87% |
| admission | 46% | 40% | 14% |

Cette mesure a distingué deux natures d'entropie, distinction réutilisée
ensuite dans tout le projet :
- **entropie-source** : l'auteur original n'a jamais documenté cette
  information — non récupérable sans retourner à la source humaine.
- **entropie-pipeline** : l'information existe dans le brut mais le code
  de transformation l'a ratée — récupérable localement, sans nouvelle
  collecte.

### 2.2 Construction d'une couche sémantique (Jour 2)

Embeddings (`bge-small-en-v1.5`, 7578 chunks) et graphe sémantique
(Graphify, 2566 nœuds, 83 communautés) construits sur le corpus brut
préservé. Le même bug structurel que §2.1 est réapparu à cet étage,
sous une forme différente : `graph_bridge.py` faisait un appariement par
préfixe qui confondait des métiers distincts partageant un préfixe de
nom (`vendeur` / `vendeur_autos`, `peintre` / `peintre_indl`).

Trois itérations de correction ont été nécessaires :
1. Garde appliquée seulement sur les slugs ayant un nœud exact —
   incomplet, asymétrique.
2. Garde étendue mais appliquée après suppression de la structure
   if/else originale — régression (le compteur de collisions a augmenté
   au lieu de diminuer).
3. Changement d'algorithme : raisonnement nœud-par-nœud plutôt que
   slug-par-slug — chaque nœud du graphe assigné au slug le plus long
   (le plus spécifique) qui le couvre. Résolution complète, vérifiée
   directement sur les cas concrets, sans régression de couverture
   (416/418 slugs mappés, stable).

### 2.3 Couche d'interrogation (Jour 3)

Une couche de requête (`query_test.py`) a été construite et testée sur
10 questions fixes couvrant plusieurs secteurs et cas de lacune source
réelle. Le test décisif : vérifier qu'une question sur un métier absent
du corpus (« salaire d'un astronaute ») ne produit jamais de réponse
hallucinée. Ce test a passé. Une faiblesse a été identifiée après coup
par l'agent d'exécution lui-même : le seuil de similarité (0.3) est trop
permissif et l'embedding ne discrimine pas toujours fiablement entre
sections d'un même métier — question restée ouverte, non résolue en
Phase 1.

## 3. Méthode de détection — ce qui a été formalisé

Le point commun aux deux bugs structurels (§2.1 et §2.2) a été formalisé
comme cadre de détection en trois couches :

- **Données (D)** — un ensemble d'entités et leurs relations, avec un
  invariant attendu (ex. : partition disjointe — chaque entité n'a
  qu'un seul propriétaire légitime).
- **Logique (L)** — les règles de transformation appliquées à D,
  extraites du code pas supposées.
- **Contradiction (C)** — une violation prouvée de l'invariant, obtenue
  en simulant l'exécution de L sur des cas réels de D, pas en devinant.

Le processus de détection suivi dans les deux cas : lire L, poser la
question « L préserve-t-elle l'invariant sur D ? », chercher un contre-
exemple concret dans D, prouver la violation formellement, puis corriger
L en restaurant l'invariant — jamais par un patch ad hoc non justifié
par la structure du problème.

Ce processus a également révélé sa propre limite en pratique : une
correction peut sembler résoudre l'invariant globalement (compteur
agrégé qui s'améliore) tout en le violant encore localement sur des cas
spécifiques. La leçon opérationnelle retenue : **toujours vérifier sur
des cas concrets et nommés dans les données produites, jamais seulement
sur un compteur global ou un message de commit.**

## 4. Ce qui est exportable — indépendant de metiers-québec

Ce qui suit ne dépend d'aucune spécificité du corpus metiers-québec et
peut être réutilisé sur n'importe quel projet de migration ou de
transformation de données :

1. **La distinction entropie-source / entropie-pipeline** — séparer ce
   qu'une source n'a jamais documenté de ce qu'un pipeline a raté, avant
   de conclure qu'une donnée est « perdue ».
2. **Le cadre de détection D/L/C** — une méthode générale pour localiser
   et prouver formellement une violation d'invariant dans un pipeline de
   transformation, indépendante du domaine.
3. **La règle de vérification par cas concret** — ne jamais accepter un
   rapport de correction sur la seule foi d'un agrégat ; vérifier
   directement, sur des exemples nommés, dans les données produites.
4. **La séparation des rôles exécution / vérification** — un exécutant
   compétent ne produit pas spontanément le niveau de vigilance qui
   protège un invariant ; il faut un acteur distinct qui pose la
   question et vérifie contre les faits, pas contre le rapport.

## 5. Ce qui n'a pas été atteint — limites du Projet #1

La question posée dès le départ du travail sur le sens — Contenu(Site A)
= Contenu(Site B), sans perte — n'a jamais reçu de critère de
certification explicite, et n'a donc jamais été tranchée. Ce n'est pas
un oubli technique : c'est resté une décision non prise, faute de seuil
défini par concept (salaire, formation, admission, etc.).

Deux causes distinctes, à ne pas confondre :
- Une partie de la perte est **structurelle** au pipeline (corrigible,
  comme démontré en §2.1-2.2).
- Une partie de la perte peut être **irrécupérable** : le corpus scrapé
  ne contient tout simplement pas certaines données à sa source — par
  exemple, aucun salaire structuré n'a jamais été extrait du texte brut
  de `corpus_raw_v2` pour la majorité des métiers, bien que le texte
  brut en contienne (ex. « architecte : 68 300$ annuel ») — un gap
  d'extraction documenté mais non résolu au moment de la clôture.

Continuer ce projet dans le détail cosmétique (corriger un slug de plus,
recalibrer un seuil de similarité) rapportait de moins en moins, une fois
la méthode de détection elle-même validée sur des cas réels et
documentée. La décision de clore ici plutôt que de continuer à raffiner
est délibérée, pas un abandon.

## 6. Conclusion — vers la Phase 2

Ce travail a révélé, sans le chercher au départ, une question plus large
que la migration d'un site précis : qu'est-ce qui reste d'une
connaissance quand on retire tous les substrats successifs qui l'ont
portée (le HTML d'un webmestre, un scraper, un graphe sémantique, un
script de requête) ? La méthode développée ici (§3, §4) répond en partie
à « comment détecter qu'un substrat a trahi le sens », mais pas encore à
« comment représenter le sens indépendamment de tout substrat, dès le
départ, plutôt que de le vérifier après coup sur un substrat déjà
choisi ».

C'est l'objet de la **Phase 2 (System C)** — un projet distinct,
documenté séparément (`CHARTE.md`), qui ne dépend pas de la migration de
`metiers-quebec.org`, ne réutilise aucun de ses fichiers de scraping, et
part uniquement de sources tierces structurées. Le lien entre les deux
projets est méthodologique (le cadre D/L/C, le vocabulaire FAIT/GARDE/
ORIGINE développé en marge de Phase 1), pas architectural — Phase 2 ne
lit rien de ce que Phase 1 a produit comme données.

## 7. Questions en suspens (Phase 1, non transférées à Phase 2)

- Faut-il continuer le scraping de `metiers-quebec.org` pour couvrir les
  73% de métiers jamais capturés, ou ce projet reste-t-il figé à son
  état actuel (418/1500 métiers, Phase 4 terminée, Phase 6 en attente) ?
- Le seuil de similarité de `query_test.py` (0.3) reste mal calibré —
  à recalibrer si ce projet reprend un jour.
- Les gaps d'extraction identifiés en `kb012` (salaires non extraits du
  texte brut de `corpus_raw_v2`) restent non résolus.

Ces questions n'ont pas de déclencheur de réouverture fixé — Phase 1
reste dans l'état où elle est ici, comme référence méthodologique, pas
comme projet actif.
