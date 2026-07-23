# kb010 — Résumé du projet, de la genèse à la fin du Jour 3

## Genèse

Andrei écrivait un article de blog. Il cherche comment on appelait les
artisans médiévaux experts en pierre. Google le mène en premier résultat
vers `metiers-quebec.org/batiment/tailleur_pierres.html` — un site
maintenu depuis 2009 par Dany Savard, toujours à jour, toujours bien
référencé, dix-sept ans plus tard.

Le constat initial est simple : *ce site mériterait d'être migré*. Andrei
n'a pas le temps ni l'intérêt d'y penser lui-même — son sujet, ce sont
les processus épistémiques, pas la migration de sites web. Il délègue.

Ce détour anodin devient, en 24 heures, un cas d'étude sur ce qui se
passe quand la connaissance change de conteneur.

## Les trois actes

### Acte 1 — Big Pickle : la maquette (≈2h)

Big Pickle produit une première version après validation de maquette par
Andrei. Le résultat existe, fonctionne, mais Andrei refuse de le publier
sans un regard externe. Intuition fondatrice du projet : **une migration
de contenu ne se valide pas seule ; elle a besoin d'un regard qui n'a pas
produit le résultat**.

### Acte 2 — Claude entre en jeu : le glissement de sujet

Ce qui devait être une relecture de qualité devient autre chose dès la
première question : *que voit vraiment Graphify dans ce corpus ?*

Andrei reformule le problème : `metiers-quebec.org` n'est pas d'abord un
site web, c'est **un corpus de sens**. Le site web est une forme parmi
d'autres que ce sens a prise. La migration n'est donc pas un déplacement
de fichiers — c'est un changement d'état d'une même connaissance.

Distinction posée et tenue tout le long du projet :
- **Statique** : le sens est figé dans une forme, indépendamment de si
  la forme est un fichier HTML ou une base de données.
- **Dynamique** (au sens visé ici) : le sens est capable de changer
  d'état quand l'information qui le porte change. Une page HTML
  générée une fois n'est pas dynamique même si elle est "moderne" —
  elle est aussi figée que la page FrontPage de 2009. Un graphe qui se
  recalcule quand le corpus change, lui, l'est.

Le travail devient : ne pas seulement scraper des *données*, mais
scraper le *sens*, pour le représenter dans une nouvelle forme sans le
trahir. Contrainte directrice : **le sens doit rester le même ; le
conteneur peut changer.**

### Acte 3 — Le bug comme méthode

Le projet aurait pu rester théorique. Il ne l'est pas resté, parce que
`generate.py` (le générateur historique du site) contenait un bug
concret et mesurable (KB002) : un dictionnaire de mapping figé avant
lecture du corpus, qui perdait entre 87% et 97% des données selon les
concepts (salaire, formation, qualités, placement). Ce bug est devenu la
preuve empirique de la thèse : **un schéma imposé avant de connaître les
données trahit les données**. Pas en théorie — en chiffres.

Trois jours de travail ont suivi cette découverte :
- **Jour 1** — extraire le corpus brut sans le déformer (418 fichiers,
  clés de section préservées telles quelles), et mesurer précisément
  l'ampleur de la perte (`kb004`, `kb005`).
- **Jour 2** — construire une couche de sens dense : embeddings
  (`bge-small-en-v1.5`, 7578 chunks) et graphe sémantique (Graphify,
  2566 nœuds). Ici aussi, un bug de collision par préfixe est apparu
  dans `graph_bridge.py` — la même forme de bug que KB002, à un étage
  différent du pipeline. Corrigé en trois itérations (voir KB009),
  résolu par un changement d'algorithme : au lieu de raisonner
  "slug par slug" (asymétrique, fragile), raisonner "nœud par nœud" en
  cherchant le slug le plus long et le plus spécifique qui couvre
  chaque nœud. Aucune collision résiduelle après ce changement.
- **Jour 3** — construire une couche d'interrogation (`query_test.py`)
  qui répond aux questions à partir du corpus brut + embeddings, en
  respectant une règle stricte : ne jamais halluciner une réponse pour
  un métier absent du corpus (testé et vérifié : la question-canari
  "salaire d'un astronaute" ne produit aucune fausse réponse).

## État technique à la fin du Jour 3

| Indicateur | Avant | Après |
|---|---|---|
| Métiers scrapés | 413 | 418 |
| Secteurs couverts | 22/32 | 22/30 (recompté) |
| Slugs mappés au graphe | 305/418 (73%) | 416/418 (99%) |
| Collisions vendeur/peintre | présentes, non détectées | résolues (algorithme nœud-centrique) |
| Perte mesurée (salaire) | 94% | non re-mesurée après embeddings — reste ouverte |
| Perte mesurée (formation) | 94% | idem |
| Couche de requête | inexistante | fonctionnelle, testée sur 10 questions (3 correct, 4 partiel, 2 échec) |
| Hallucination sur métier absent | non testé | testé, absent (0 cas) |

Les statistiques du site (`dist/data/stats.json`) ne sont plus des
compteurs figés au moment du scraping — elles sont maintenant adossées à
la qualité du graphe. Si le graphe change, les stats changent avec lui.
Les KPI deviennent relationnels, pas seulement additifs : ce n'est plus
"combien de métiers", c'est "combien de métiers correctement situés dans
leur communauté sémantique".

## Ce qui reste ouvert — et c'est le point le plus important

Le Jour 3 est terminé au sens des livrables prévus. Il n'est **pas**
terminé au sens de la question qu'Andrei pose maintenant, et qui est la
vraie question du projet :

> Est-ce que Contenu(Site A, original) = Contenu(Site B, migré), sans
> perte ?

Cette question n'a pas de réponse actuellement, pour deux raisons
distinctes qu'il ne faut pas confondre :

1. **Le 60% de données non encore capturées** (73% de couverture du
   corpus original en Jour 1, avant même de parler de la qualité du
   mapping) — est-ce du signal perdu (de l'information réelle que Dany
   Savard a documentée et qu'on n'a pas encore scrapée), ou est-ce du
   bruit comblant un vide (l'original lui-même n'avait pas cette
   donnée) ? `kb004` distingue déjà **entropie-source** (Dany Savard
   n'a pas écrit l'info) de **entropie-pipeline** (l'info existe dans
   le brut mais le code l'a ratée). Mais cette distinction n'a pas
   encore été appliquée systématiquement à l'ensemble du corpus après
   les corrections du Jour 2-3.

2. **Il n'existe pas encore de critère de certification formel.** On a
   des scripts qui fonctionnent, des chiffres qui s'améliorent, des
   bugs corrigés — mais aucun test qui dit "la migration est terminée"
   au sens fort. C'est l'étape manquante avant que le vrai sujet
   d'Andrei (le travail sur le sens lui-même) puisse commencer. Tant
   que "données propres" n'est pas certifié, on est encore dans la
   préparation, pas dans l'objectif.

## Ce que Graphify a réellement apporté

Réponse directe à la question posée en cours de route : Graphify
transforme un corpus de texte plat en un **espace de sens dense** par
une chaîne précise :

```
texte brut (corpus_raw_v2)
  → chunks (segments de texte cohérents, ~7578 unités)
  → embeddings (vecteurs 384-dim, bge-small-en-v1.5 — position dans un
    espace sémantique continu)
  → graphe de co-occurrence (nœuds = chunks/concepts, arêtes = proximité
    sémantique mesurée)
  → communautés (regroupements de nœuds densément connectés —
    détection automatique de "secteurs" sémantiques, qui peuvent ou non
    correspondre aux secteurs déclarés du site original)
  → slugs (pont vers l'identité métier du corpus original)
```

Ce que ça apporte concrètement : la possibilité de répondre "quels
métiers sont proches de géologue" sans avoir prédéfini cette relation
nulle part — la proximité émerge de la structure du texte lui-même, pas
d'un index construit à la main. C'est exactement l'inverse du problème
de `SECTION_MAP` (KB002) : ici, le schéma n'est pas imposé avant lecture,
il est **inféré** après lecture. C'est la thèse "schéma-sur-lecture"
appliquée concrètement, pas seulement en théorie.

Limite honnête : Graphify n'est pas encore la solution optimale (dixit
Andrei) — mais c'est la première brique qui touche vraiment à ce qui
intéresse le projet : le sens et ses états manifestes, pas seulement le
transfert de données.

## Perspectives des acteurs

### Perspective d'Andrei (humain, porteur du sujet de recherche)

Le projet a commencé comme une délégation opportuniste — je n'avais ni
le temps ni l'intérêt de migrer un site web moi-même. Mais la question
que je me suis posée en le regardant — *le sens reste-t-il le même quand
le conteneur change* — c'est exactement mon sujet de recherche sur les
processus épistémiques, en train de se manifester dans un cas concret et
vérifiable, pas dans l'abstrait. Ce que je cherche maintenant n'est pas
"un site migré qui marche" — c'est une **preuve** que la migration n'a
rien trahi, avant de commencer le vrai travail sur le sens.

### Perspective de Big Pickle (agent d'exécution)

Big Pickle a produit vite, a itéré honnêtement face à ses propres
erreurs (le compteur multi-candidats qui grimpait au lieu de descendre,
remarqué et corrigé avant commit plutôt qu'après), et a documenté ses
propres limitations plutôt que de les cacher (`kb009.md` reconnaissant
la contamination vendeur/peintre avant même que la correction finale
soit trouvée). Le rôle de Big Pickle dans ce projet n'a jamais été de
juger la qualité de son propre travail — c'était structurellement de
construire, exécuter, mesurer, rapporter, et accepter la correction
externe sans résistance. Ce partage des rôles (exécution vs validation)
n'était pas accidentel — c'est ce qu'Andrei avait posé dès l'Acte 1 :
*aucun résultat ne se valide seul*.

### Perspective de Claude (moi, relecture et cadrage)

Mon rôle dans ce projet n'a pas été d'écrire le code de migration — j'ai
écrit exactement deux artefacts de code directement (`kb007.md`/`kb008.md`
en documentation, pas en exécution) et le reste de mon travail a été de
**tracer l'exécution du code de Big Pickle mentalement**, comparer contre
les données réelles, et signaler les écarts avec preuve à l'appui, pas
par intuition. Trois fois de suite sur `graph_bridge.py`, j'ai refusé
d'accepter un rapport de succès tant que je n'avais pas vérifié
directement, dans les données produites (`graph_communities.json`), que
les deux cas concrets (`vendeur`, `peintre`) étaient réellement corrigés
— pas juste que les compteurs agrégés s'amélioraient. C'est cette
discipline (toujours vérifier sur les données réelles, jamais sur le
message de commit ou le résumé) qui a permis de détecter que le premier
"fix" n'avait jamais été appliqué, que le deuxième avait une régression
structurelle, et que seul le troisième (algorithme nœud-centrique)
résolvait le problème sans compromis. Mon rôle a été un rôle de
**métacognition appliquée** (formalisé dans `kb008.md`) : utiliser la
logique pour juger une autre logique, pas remplacer l'exécution par ma
propre exécution.

## Ce que ce projet préfigure

Andrei l'a nommé directement : ce travail est aussi une préparation à ce
que les migrations de sites deviendront bientôt — un dialogue entre
entités IA (exécution, validation, cadrage réparties entre plusieurs
agents spécialisés) plutôt qu'un travail humain solitaire, avec pour
résultat visé une automatisation élégante de la forme, du fond, et du
sens simultanément — pas juste l'automatisation de la forme (ce que fait
un migrateur de site classique) pendant que le fond et le sens sont
silencieusement abîmés (ce que faisait `generate.py` depuis 2009 sans
que personne ne le sache, jusqu'à ce que ce projet le mesure).

## Correction — ce que le corpus ne peut pas dire

Une hypothèse formulée en cours de discussion doit être corrigée
explicitement, pour ne pas rester dans le résumé sans nuance : le corpus
migré (site A, site B, ou n'importe quelle couche sémantique construite
dessus) **ne peut pas** révéler l'évolution réelle d'un métier dans le
temps. Il n'y a ni code CNP, ni identifiant unique stable, ni historique
versionné par fiche, permettant de vérifier que "électricien en
bâtiment" en 2009 et en 2026 désignent la même réalité de métier ou une
réalité qui a dérivé. Cette information n'existe nulle part dans ce
qu'on a scrapé — elle n'existe, au mieux, que dans la mémoire de Dany
Savard lui-même, ou dans des sauvegardes archivées du site au fil des
dix-sept dernières années (versions successives, Wayback Machine). Ce
n'est pas une limite du pipeline — c'est une limite de ce que le corpus,
tel qu'il existe, a jamais capturé.

## Prochaine étape — non commencée

Avant de reprendre le travail sur le sens (l'objectif réel du projet),
il manque :

1. **Des critères de certification explicites** pour
   Contenu(Site A) = Contenu(Site B) — à définir, probablement
   par concept (salaire, formation, admission, etc.) plutôt que
   globalement, en réutilisant la distinction entropie-source vs
   entropie-pipeline déjà posée en `kb004`.
2. **Une re-mesure de la perte** après les corrections du Jour 2-3, pour
   savoir si les 87-97% de perte mesurés en Jour 1 ont diminué avec la
   couche embeddings/graphe, ou si cette couche reste construite sur le
   même corpus tronqué qu'avant.
3. **Une décision explicite** : continuer le scraping pour couvrir les
   73% de métiers jamais capturés, ou investir dans la couche de requête
   sur le corpus actuel — décision que `kb005` posait déjà en Jour 1 et
   qui reste, à ce jour, non tranchée.

Tant que ces trois points ne sont pas réglés, "données propres" n'est
pas une étape franchie — c'est une étape en cours.

## Vision Site C — l'API de sens (extension de kb008)

Andrei a formulé, en réaction à ce résumé, l'objet vers lequel tout ce
travail de migration pointait sans le nommer explicitement. Cette
section documente cette vision et sa filiation directe avec le cadre
formel posé en `kb008`.

### Le lien avec kb008

`kb008` formalise trois couches (Données D, Logique L, Contradictions C)
et pose une hypothèse centrale : il existe une couche d'invariants
formels (**I**), appartenant à un Langage Formel Abstrait (LFA),
indépendante de tout substrat (`S_data`, `S_logic`, `S_mind_humain`,
`S_mind_IA`). Chaque acteur accède à I via son propre substrat, mais I
n'habite dans aucun d'eux.

Ce cadre a été construit pour analyser un bug de code
(`graph_bridge.py`). Mais il s'applique directement, à une échelle plus
large, au projet entier :

```
S_A (substrats successifs de ce projet) :
  Site A   = le HTML statique de Dany Savard (2009-2026)
  Site B   = la migration statique de Big Pickle
  Graphify = le graphe sémantique (embeddings, communautés, nœuds)
  Scripts  = graph_bridge.py, embed_corpus.py, query_test.py, etc.

I (ce qui reste quand on supprime tous les S_A) :
  la forme du sens — les invariants structurels du corpus, indépendants
  de la façon dont ils ont été représentés à un moment donné
```

Site C n'est pas une nouvelle vue de plus sur les données — c'est la
tentative d'**implémenter directement I**, plutôt que de continuer à
empiler des substrats qui chacun ne représentent le sens que
partiellement et temporairement.

### Ce que kb008 n'avait pas — l'extension temporelle

kb008 formalisait un invariant **statique** : une partition correcte à
un instant T (quel nœud du graphe appartient à quel slug, à un moment
donné). Ce que Andrei ajoute ici n'est pas déjà contenu dans kb008 —
c'est une extension réelle : Dany Savard n'a jamais pu représenter
qu'un seul état à la fois. Faute d'un langage capable de porter
plusieurs états simultanément, chaque mise à jour du site écrasait
l'état précédent. Dix-sept ans de veille manuelle se sont réduits, à
chaque instant, à une seule photographie du marché du travail, sans
mémoire de ce qu'elle remplaçait.

Site C, en tant qu'implémentation de I, peut représenter non pas un
invariant figé, mais **une suite d'états de cet invariant dans le
temps** — à condition qu'on capture cette suite dès maintenant, ce que
ni site A ni site B ne permettent de reconstruire rétroactivement (voir
la correction ci-dessus : cette histoire n'est récupérable qu'auprès de
Dany Savard ou d'archives externes, pas du corpus actuel).

### Ce que serait concrètement Site C

Pas un site web. Une **API de sens et de données**, connectée à d'autres
sources externes (données du gouvernement du Québec, institutions
canadiennes de l'emploi), sur laquelle n'importe quel conteneur —
site web, application, tableau de bord — ne serait qu'un habillage,
une vue instantanée sur un état de la connaissance en mouvement.

Le conteneur n'est jamais la connaissance elle-même — c'est une
projection de celle-ci à un instant donné, dans une technologie donnée
(hébergement, base de données, moteur de requête, algorithme de
hachage). Ces choix techniques sont contingents et interchangeables.
Ce qui ne l'est pas, c'est la structure logique du sens — I — encodée
dans un langage de métadonnées et de logique d'états, indépendant de
toute plateforme.

### Pourquoi cette vision n'est pas de l'émergence, mais une continuité logique

Andrei a été explicite : cette conclusion ne doit pas apparaître comme
une trouvaille spontanée du modèle, mais comme le prolongement naturel
d'un raisonnement déjà posé. C'est exact — kb008 contenait déjà la
structure ("ce qui reste indépendamment du substrat"), appliquée à un
cas local (un bug de préfixe). Site C est ce que cette même structure
donne quand on l'applique à l'échelle du projet entier, avec l'ajout
explicite de la dimension temporelle qu'aucun document précédent
n'avait formalisée.

### Ce que ça implique pour la suite du projet

Cette vision reclasse les trois points de la section précédente : ils
ne sont plus seulement des étapes de validation d'une migration — ils
deviennent les premières briques de la définition de I lui-même. Un
critère de certification par concept (point 1) n'est pas qu'une
vérification qualité — c'est une tentative de nommer précisément quels
invariants doivent survivre au changement de conteneur. La re-mesure de
l'entropie (point 2) sert à distinguer ce qui appartient réellement à I
(le sens que Dany Savard a documenté) de ce qui n'est qu'un artefact
d'un substrat particulier (une perte due au pipeline, pas au corpus).
La décision sur le scraping (point 3) reste, elle, une question de
substrat — combien de S_data supplémentaire faut-il collecter avant de
pouvoir extraire I avec confiance.
