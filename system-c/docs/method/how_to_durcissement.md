Ni l'un ni l'autre exactement — c'est une troisième catégorie de travail, et la confusion vaut la peine d'être levée avant de la caser de force dans le cycle de sprint.

## Ce n'est pas un sprint au sens de §2.2

Un sprint, tel que défini dans `methodologie-agentique-system-c.md`, ferme une **question épistémique** (une hypothèse sur le domaine emploi-Québec, binaire ou N-aire). Le contenu des deux documents de durcissement n'est pas ça — c'est une checklist d'ingénierie appliquée au code lui-même (`gardes.py`, `cnp_check()`), pas une hypothèse sur les métiers. Forcer ce travail dans le moule construction/critique à deux mains, seuil pré-enregistré par commit, etc., serait exactement le genre de surcharge que tu signalais comme risque il y a quelques tours (« trop lourd ») — le protocole de clôture d'hypothèses n'a pas été pensé pour ce type de tâche.

## Ce n'est pas non plus « en dehors » de System C

C'est le code fondateur de System C lui-même — `gardes.py` porte les 5 GARDES de CHARTE.md, `cnp_check()` (ou son équivalent futur) arbitre une clé canonique du projet. Le sortir du projet n'aurait aucun sens.

## Et surtout : ça ne doit pas toucher les données existantes

C'est le point le plus important, explicite dans les deux documents. §1 de `durcissement-gardes_v0_1.md` : *« aucune écriture manuelle du corpus de production, même à des fins de test »*. §3 de `durcissement-outils-classification_v0_1.md` : les cas adversariaux (chaîne vide, collision connue, etc.) sont des cas synthétiques, construits délibérément — pas extraits de `data/atomic/`. Utiliser les 413 fiches réelles pour ce travail répéterait exactement l'erreur du CORRECTIF (données de test mélangées au corpus de production). Ce travail vit dans `fixture/`, jamais dans `data/atomic/`.

## Ce que je proposerais concrètement

Une passe de maintenance légère, séparée du cycle de sprint hypothèse :
- Garder la discipline de commit vérifiable (§2.5 du protocole — seuil/résultat/verdict traçable par `git log`) parce que c'est gratuit et déjà en place ailleurs, pas parce que c'est un sprint.
- Ne pas exiger de main séparée construction/critique pour ce travail-là spécifiquement, sauf si `cnp_check()` sert à nouveau à trancher quelque chose d'aussi sensible qu'infirmier/infirmier auxiliaire — dans ce cas, oui, la même isolation qu'un vrai sprint se justifie, proportionnellement à l'enjeu (règle 6 de `durcissement-outils-classification_v0_1.md`).
- **Point de séquencement à retenir** : tant que cette passe n'est pas faite, tout sprint épistémique en cours (H4b, ou un futur test qui s'appuierait sur `gardes.py` ou un outil de classification pour produire son verdict) hérite silencieusement de la même fragilité que celle qui a produit les deux incidents documentés. Ce n'est pas un sprint en soi, mais c'est un prérequis silencieux pour la fiabilité de tout sprint qui viendrait après et qui dépendrait de ces outils.


Dépend du sprint, pas une réponse universelle — mais la règle de décision est simple à appliquer : **avant, uniquement pour tout sprint dont le verdict s'appuie sur `gardes.py` ou un outil de classification type `cnp_check()` ; en parallèle ou après pour tout le reste.**

## Pourquoi pas une règle absolue

Bloquer tous les sprints en attendant le durcissement reproduirait l'erreur inverse de celle qu'on corrige — de la sur-ingénierie préventive sur des sprints qui n'ont rien à voir avec ces deux outils. La méthodologie elle-même (`methodologie-agentique-system-c.md` §2.2) dit qu'un sprint atomique ne doit jamais dépendre de plus que ce qu'il lui faut réellement.

## Comment trancher pour un sprint donné

```
Le verdict de ce sprint appelle-t-il gardes.py (une des 5 GARDES) 
ou un outil de matching/classification de type cnp_check() 
pour produire son état proposé/confirmé ?

  OUI → durcissement d'abord, sprint après. 
        Sinon le verdict hérite silencieusement de la même fragilité 
        que les deux incidents documentés — exactement le problème 
        nommé la dernière fois.

  NON → le sprint peut avancer sans attendre. Le durcissement se fait 
        en parallèle ou après, comme passe de maintenance normale.
```

## Cas concret — H4b

Si H4b s'appuie, même partiellement, sur un outil de matching d'appellations/CNP (ce qui semble être le cas vu qu'il descend de la lignée kb020/kb021 sur la classification) — alors le durcissement de `cnp_check()` (ou son équivalent) passe **avant**, pas après. Un verdict H4b produit avec un outil non testé adversarialement serait exactement le type de « 6 violations légitimement expliquées » qu'on a nommé comme patch fable deux tours plus tôt — sauf que cette fois ce ne serait plus une conversation rejetée, ce serait le sprint courant.

Si H4b ne touche à aucun des deux outils, il n'y a aucune raison de le retarder pour ça.

**Point pratique** : la vérification elle-même — est-ce que H4b (ou tout autre sprint prévu) appelle réellement l'un des deux outils — ne prend que quelques minutes à trancher en regardant le plan de test avant de lancer la construction. C'est la première chose à faire, pas une supposition de ma part.