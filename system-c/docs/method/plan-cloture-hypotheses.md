# Plan — clôture disciplinée des hypothèses System C

**Statut : opérationnel, v2 — corrections intégrées avant premier usage réel (H4b).**
Aucun nouvel outil, aucun nouveau fichier de registre séparé. Ce sont des conventions
d'écriture et de commit, applicables aux KB existants tel quels.

---

## 1. État d'une hypothèse — deux champs, jamais un seul

Chaque KB portant une hypothèse déclare, en tête de document, deux champs distincts :

```
**État proposé (auteur)** : corroborée / infirmée / contradictoire / indéterminée / 
  PRINCIPE — non fermable (proposé)
**État confirmé (relecture indépendante)** : corroborée / infirmée / contradictoire /
  indéterminée / PRINCIPE — non fermable (confirmé) / EN ATTENTE
```

Le champ "confirmé" n'est jamais rempli par la même main (humaine ou IA) que le champ
"proposé" — **y compris pour `PRINCIPE — non fermable`**, qui suit exactement la même
discipline à deux mains que n'importe quel autre état. Personne ne se retire seul du
protocole de test. Tant que le champ confirmé reste "EN ATTENTE", l'hypothèse (fermable
ou déclarée principe) n'est pas opposable — citable comme piste, jamais comme fondement
d'une décision en aval.

## 2. Construction / critique — qui fait quoi

```
Construction (produit l'état proposé)
  → reçoit UNIQUEMENT le corpus/matériau vérifié, jamais l'historique de la 
    discussion qui a mené à l'hypothèse, jamais les tentatives précédentes.

Critique (produit l'état confirmé)
  → session neuve, reçoit UNIQUEMENT le livrable de construction, aucun contexte 
    de production. Vérifie : le seuil annoncé a-t-il été respecté tel qu'écrit 
    (voir §3), la méthode correspond-elle à ce qui était prévu, le résultat 
    est-il présenté sans dépasser ce qu'il démontre — y compris quand la 
    construction propose "PRINCIPE — non fermable" : la critique vérifie que ce 
    n'est pas une sortie de confort (voir §5).
```

## 3. Seuil pré-enregistré — vérifiable par commit, pas par affirmation

Avant tout test : un commit distinct contenant uniquement le seuil, la méthode, et le
critère de passage — rien du résultat.

```
Commit N   : "seuil pré-enregistré — [nom du test]"  (seuil + méthode + critère)
Commit N+1 : "résultat — [nom du test]"               (données brutes)
Commit N+2 : "verdict — [nom du test]"                (état proposé)
```

**Vérification immédiate, sans attendre la fin du sprint** : `git log --oneline` doit
montrer le commit de seuil strictement antérieur au commit de résultat. Si l'ordre est
inversé ou fusionné en un seul commit, le test est disqualifié d'office, sans discussion
sur le fond du résultat.

## 4. Règle d'agrégation feuille → parent

Quand une hypothèse est décomposée en sous-hypothèses pour devenir fermable :

```
état(parent) = 
  si au moins un enfant est "EN ATTENTE"        → EN ATTENTE (priorité absolue, 
                                                     avant toute autre règle)
  sinon, si tous les enfants sont "corroborée"  → corroborée
  sinon, si un enfant est "contradictoire"      → contradictoire
  sinon, si un enfant est "indéterminée"        → indéterminée
  (l'état le plus faible l'emporte toujours — jamais de moyenne, jamais de majorité)
```

`EN ATTENTE` bloque tout le reste par construction : c'est le cas le plus fréquent en
pratique (les branches ne se ferment jamais toutes en même temps), et il doit être
tranché en premier, pas en dernier recours. Écrite explicitement dans le KB parent dès
qu'une sous-hypothèse ferme, pas seulement à la fin de toutes les branches.

## 5. Reformulation ou déclaration de principe — après diagnostic, pas après un échec

Si une hypothèse résiste à la fermeture après une tentative de test avec seuil
pré-enregistré respecté, **la critique isolée (§2) tranche d'abord un diagnostic avant
toute sortie du protocole** :

```
□ Le test était bien calibré et le résultat reste flou 
    → candidat légitime à la reformulation (sous-hypothèses plus étroites)
□ Le seuil était probablement mal calibré (ex. corpus trop petit, méthode trop 
  grossière pour la question posée)
    → un deuxième essai avec seuil ajusté, PAS un abandon ni une reformulation
□ Aucun test raisonnable ne peut la rendre fermable, quel que soit le corpus ou 
  le seuil
    → seule cette issue autorise "PRINCIPE — non fermable (proposé)", et encore 
      soumis à confirmation indépendante (§1, §2) avant d'être opposable
```

Une seule tentative non tranchante n'ouvre jamais directement la sortie "principe" —
le diagnostic ci-dessus est un passage obligé, produit par la critique isolée, pas par
la construction qui a produit le résultat flou.

`PRINCIPE — non fermable (confirmé)` ne bloque jamais un parent en aval par la règle du
§4 — il est traité comme une justification de portée, pas comme un nœud de l'arbre de
clôture, une fois confirmé selon la même discipline à deux mains que tout autre état.

## 6. Risque résiduel — nommé, pas neutralisé

Chaque note de clôture (Sprint de synthèse) porte une ligne fixe :

```
**Risque résiduel non couvert par ce protocole** : [une phrase — ex. biais de substrat 
partagé entre construction et critique, absence de vérification antérograde pour les 
KB futurs qui dépendront de celui-ci, calibration du diagnostic §5 elle-même non 
vérifiée par un troisième regard]
```

Pas de tentative de le résoudre dans le même sprint — juste l'obligation de l'écrire.

---

## Séquence, avant/pendant les sprints

```
AVANT tout sprint
  □ Question fermée à réponse binaire ou N-aire finie, écrite en une phrase
  □ Seuil et méthode écrits et committés (§3, commit N)
  □ Corpus/matériau isolé de tout historique de discussion, prêt à transmettre 
    à la construction

PENDANT le sprint
  □ Construction produit résultat + état proposé (commits N+1, N+2)
  □ Critique (session neuve) produit état confirmé — sans avoir vu le contexte
  □ Si résultat non tranchant : critique isolée applique le diagnostic §5 avant 
    toute reformulation ou déclaration de principe
  □ Si divergence construction/critique : documentée telle quelle, jamais moyennée

RÉSULTAT VÉRIFIABLE IMMÉDIAT, sans attendre la fin du chantier
  □ git log montre l'ordre seuil → résultat → verdict, non falsifiable a posteriori
  □ Le KB porte les deux champs d'état (§1), jamais un seul — y compris pour 
    "PRINCIPE — non fermable"
  □ Le KB parent (si applicable) reflète la règle du §4 dès la clôture de la 
    feuille, EN ATTENTE en priorité si applicable
  □ La ligne de risque résiduel (§6) est présente, même si courte
```
