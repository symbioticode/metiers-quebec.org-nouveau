# kb026 — Verdict consolidé : H4a et H4b (alphabet de fonctions atomiques)

**Type de document** : KB (verdict consolidé, résultats de recherche
uniquement — pour la gouvernance et le déroulement des sprints, voir
`rapport-audit-branches.md`)

Ce document répond à une seule question, en langage simple : **est-ce
qu'il existe un socle de fonctions de travail atomiques, stable,
indépendant de la façon dont on découpe les métiers ?** C'est la
question que kb021 pose sous le nom H4. Elle se décompose en deux
volets, testés séparément.

## H4a — le socle O*NET reste-t-il le même dans le temps ?

**Question posée** : entre 2003 et 2026, est-ce que la liste des 41
« activités de travail généralisées » d'O*NET (des verbes d'action assez
abstraits — « obtenir de l'information », « prendre des décisions »,
etc.) a changé, alors que les métiers eux-mêmes se sont énormément
transformés en dessous ?

**Réponse, simplement** : non, elle n'a pas bougé. Zéro ajout, zéro
retrait, sur 23 ans et 17 mises à jour du système. C'est une confirmation
forte et vérifiée deux fois (recalculée à la main depuis les données
brutes, pas juste lue dans un rapport).

**Ce que ça veut dire, et ce que ça ne veut pas dire.** Ce résultat
montre qu'un socle de ce type *peut* être parfaitement stable — c'est
encourageant pour l'hypothèse générale. Mais il faut rester prudent :
ces 41 activités sont figées *par construction*, elles font partie de la
structure même d'O*NET, pas d'un phénomène qu'on observe de l'extérieur.
Un peu comme si on demandait "est-ce que les 26 lettres de l'alphabet
ont changé depuis 100 ans" — la réponse est oui-stable, mais ça ne prouve
pas que n'importe quel découpage de la langue en unités serait
stable, seulement que celui-là l'est. H4a montre qu'un socle stable est
*possible*, pas que le socle qu'on cherche pour Site C en est
nécessairement un.

## H4b — cet alphabet existe-t-il indépendamment de la taxonomie qui le mesure ?

C'est la question plus difficile, et la vraie cible : si on prend le
même socle (les 41 activités O*NET) et qu'on le compare à un référentiel
*complètement différent, construit par quelqu'un d'autre, dans un autre
pays* — est-ce qu'on retrouve les mêmes fonctions ? Si oui, ce n'est plus
une propriété d'O*NET, c'est une propriété du travail lui-même.

**Premier essai, raté pour de bonnes raisons.** On a d'abord essayé de
faire émerger un tel alphabet directement depuis nos propres données
(88 fonctions extraites du corpus), en regroupant les termes qui se
ressemblent. La méthode utilisée (comparaison de mots lettre par lettre)
s'est révélée trop grossière : elle regroupait seulement les termes
presque identiques mot pour mot, jamais les termes qui veulent dire la
même chose avec des mots différents. Ce n'était pas un résultat, c'était
un instrument mal calibré — donc on l'a mis de côté et changé
d'approche, plutôt que d'insister.

**Deuxième essai — comparer contre ESCO, un référentiel européen
indépendant.** ESCO est construit par la Commission européenne, sans
lien avec O*NET ni avec la classification canadienne CNP. Question :
est-ce que les 41 activités O*NET trouvent une activité "jumelle" dans
ESCO (13 939 compétences), en utilisant un modèle qui comprend le sens
des mots (pas juste leur orthographe) ?

- **En anglais, avec les données ESCO récupérées automatiquement** :
  66% des 41 activités trouvent un jumeau clair dans ESCO. Sous le seuil
  qu'on s'était fixé pour dire "oui, ça marche" (70%) — donc, en l'état,
  plutôt un signal négatif.
- **En français, avec le fichier ESCO complet téléchargé à la main** :
  80% trouvent un jumeau. Nettement mieux, presque suffisant pour dire
  "oui, ça marche" (le seuil était 90%).
- **Vérification : est-ce que l'écart entre les deux vient juste du fait
  que la version anglaise était incomplète ?** On a retesté en anglais,
  mais cette fois avec le fichier complet (comme pour le français). Le
  résultat reste à 68% — presque identique au premier essai anglais. **Donc
  non, ce n'est pas un problème de données manquantes.** L'écart entre
  anglais (68%) et français (80%) est réel.

**Ce que ça veut dire, en clair.** On a un résultat à moitié positif :
le socle des 41 activités *retrouve bel et bien un écho* dans un
référentiel totalement extérieur, ce qui est en soi un signal
encourageant — ce n'est pas rien que 66 à 80% des activités aient un
jumeau reconnaissable. Mais le résultat change selon la langue dans
laquelle on fait le test, et pour l'instant on ne sait pas dire
pourquoi : est-ce que le français décrit le travail d'une façon qui
colle mieux au vocabulaire des 41 activités ? Est-ce que le contenu
d'ESCO est simplement plus riche ou mieux écrit en français qu'en
anglais pour ce type de vocabulaire ? Ou est-ce que l'outil qu'on utilise
pour comparer le sens des mots (le modèle d'IA) est simplement meilleur
en français qu'en anglais pour ce vocabulaire précis ? Les trois pistes
restent ouvertes, aucune n'a encore été testée directement.

**Verdict honnête, sans forcer une conclusion** : ni corroborée, ni
réfutée. Un signal réel, mais dépendant de la langue de mesure — ce qui
n'est normalement pas censé arriver si on teste vraiment une propriété
du travail lui-même plutôt qu'un artefact de l'outil de mesure. C'est ce
point précis qu'il faut clarifier avant de pouvoir répondre franchement
à H4b.

## Ce que ces deux verdicts, ensemble, disent pour Site C

H4a montre qu'un socle *peut* rester identique très longtemps — bonne
nouvelle en soi, mais une preuve faible parce que ce socle particulier
est figé par construction, pas observé "dans la nature". H4b montre
quelque chose de plus intéressant et de plus inconfortable : quand on
teste ce même socle contre un référentiel vraiment indépendant, on
trouve un vrai signal — ni un échec net, ni une confirmation nette — et
ce signal bouge selon un facteur (la langue) qui ne devrait normalement
pas avoir d'importance si l'hypothèse est vraie telle qu'énoncée. C'est
exactement le genre de résultat qui mérite d'être creusé plutôt
qu'ignoré ou forcé dans une case : ni la victoire facile, ni l'échec
propre — un vrai signe que quelque chose d'intéressant se passe, pas
encore compris.

## Ce qui reste à faire pour clore H4b proprement

Une seule question ferme la porte ou l'ouvre plus grand : **l'écart
anglais/français est-il dû à la langue, au contenu du référentiel, ou
au modèle d'IA utilisé pour comparer le sens des mots ?** Le prochain
test utile isole cette variable directement — par exemple en changeant
seulement le modèle d'IA (en gardant la même langue), ou en comparant
un sous-ensemble d'ESCO qui existe à l'identique dans les deux langues
(pas juste traduit, mais dont on sait que le contenu source est
équivalent). Tant que ce test n'est pas fait, H4b reste un signal
intéressant, pas un verdict.
