# kb023 — Décisions de gouvernance non capturées ailleurs

**Type de document** : KB (gouvernance, pas hypothèse)

Ce document existe pour une raison précise : plusieurs décisions
structurantes de ce projet n'ont été formulées que dans des sessions de
conversation, jamais committées comme texte sur GitHub — alors que le
principe fondateur du projet est que GitHub est la seule source de
vérité. Ce document répare ce trou pour les décisions déjà prises. Toute
nouvelle décision de gouvernance de cette nature doit être ajoutée ici
au moment où elle est prise, pas reconstituée après coup.

## 1. `cnp-sha-check` — pourquoi archivé « pending », pas rejeté

`experimental/cnp-sha-check` proposait une couche de validation par
hachage SHA-1 exact (`cnp_sha_check.py`), motivée par un cas concret :
la confusion entre CNP 31301 (infirmier autorisé) et CNP 32101
(infirmier auxiliaire), deux ordres professionnels réglementés
distincts, mal distingués par l'outil de correspondance existant
(`cnp_check.py`).

**Décision** : ne pas fusionner cette branche vers `phase2-systemc`, et
la renommer `archive/cnp-sha-check-pending` plutôt que
`-rejected`.

**Raison précise** — à ne pas perdre : le problème n'est pas que la
proposition est mauvaise. Le hachage exact fonctionne, prouvé sur le cas
fondateur et durci depuis (voir `kb022-durcissement-sha-check.md`). Le
problème est que **sa couverture opérationnelle est trop étroite pour
justifier une généralisation** — un seul cas d'usage concret validé
(infirmier/infirmière auxiliaire) ne suffit pas à démontrer que
l'approche vaut la peine d'être intégrée à la ligne principale du
projet. C'est une question de *portée*, pas de *qualité*. La distinction
est directement héritée de la discussion sur kb018 : kb010/kb013
décrivent une invariance sémantique tolérante (la paraphrase reste
acceptable), kb018 décrit une invariance syntaxique exacte, zéro
tolérance — deux fils volontairement non fusionnés tant qu'un deuxième
cas d'usage concret, distinct du premier, ne le justifie pas.

**Condition de sortie de ce statut** : un deuxième cas d'usage concret,
non trivialement dérivé du premier, qui démontre que le hachage exact
apporte une valeur que le matching existant n'apporte pas. Sans ça, la
branche reste `pending` indéfiniment — ce n'est pas un problème, c'est
l'état correct tant que la condition n'est pas remplie.

## 2. Pourquoi les branches expérimentales ne fusionnent jamais sans dry-run

Principe déjà présent dans `methodologie-agentique-system-c.md` mais
valant la peine d'être répété avec l'exemple concret qui l'a confirmé :
lors du ménage de branches (2026-07-26), un rapport d'audit produit par
un agent (Big Pickle) s'est révélé exact sur presque tous les points
sauf un écart mineur de comptage de fichiers (53 annoncés vs 51
recomptés indépendamment) — sans conséquence sur le verdict, mais la
vérification indépendante (dry-run merge rejoué, comptage recalculé) est
ce qui a permis de le détecter. Aucun rapport d'agent, aussi rigoureux
soit-il dans sa présentation, n'est traité comme suffisant sans ce
recalcul.

## 3. Sur la promotion des résultats vers les documents canoniques

Constat fait le 2026-07-27, après plusieurs sprints H4b-ESCO exécutés,
vérifiés indépendamment, mais jamais reflétés dans `kb021.md` — le
document que le projet lui-même désigne comme la source canonique de
l'état de chaque hypothèse. Le protocole (`methodologie-agentique-system-c.md`)
définit des rôles CONSTRUCTION et CRITIQUE, mais aucun rôle n'était
explicitement chargé de la **promotion** : faire passer un résultat
vérifié d'un fichier satellite (`kb021-h4b-*-test.md`) vers le document
canonique. Neuf sprints exécutés dans une session, une seule promotion
effective (H4a) au moment du constat.

**Décision** : la promotion vers le document canonique n'est plus une
étape implicite du Sprint 4/5 — elle doit être son livrable explicite et
vérifiable (un commit qui modifie le fichier canonique lui-même, pas
seulement un fichier satellite). Voir amendement correspondant dans
`methodologie-agentique-system-c.md`.
