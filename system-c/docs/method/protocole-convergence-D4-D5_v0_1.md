# Protocole — convergence D4/D5 entre System C et TI-360

**Statut : HYPOTHÈSE DE MÉTHODE, non exécutée · aucune donnée collectée · à valider par Andrei avant tout geste d'implémentation**

**Portée de ce document** : définir *comment* tester une hypothèse, pas trancher si elle est vraie. Rien ici n'est une instruction d'implémentation. RKA n'est invoqué nulle part dans ce protocole — la spécification n'a jamais été formellement utilisée ni dans DUO ni ailleurs, et ce document ne change pas ça.

---

## 0. Rappel du principe qui encadre tout le reste

CHARTE.md (§2bis) nomme déjà l'erreur à ne pas répéter : généraliser un cadre validé sur un seul cas à un projet aux besoins différents est une **hypothèse de continuité**, pas une loi transférée avec preuve. Ce document applique cette discipline à D4/D5 : on ne modifie aucun schéma tant qu'on n'a pas de cas concret, nommé, qui force la modification — conformément à kb013 §3 (« toujours vérifier sur des cas concrets et nommés dans les données produites, jamais seulement sur un compteur global »).

---

## 1. Reformulation à tester (rappel)

- **D4 (irréversibilité tracée)** : identité par contenu (hash) + pointeur vers prédécesseur — modèle chaîné, structurel. Déjà candidat dans System C (GARDE-Irréversibilité) et dans TI-360 (kb018, bloc_canonique non implémenté).
- **D5 (fraîcheur décroissante)** : hypothèse reformulée — la fraîcheur n'est pas une date déclarée sur chaque unité, mais une propriété **dérivée** de la structure (distance depuis dernière confirmation) pondérée par un taux, ce taux vivant au niveau opérationnel, jamais au niveau ontologique de DUO.

## 2. Ce qui existe déjà, non testé

| Système | Champ | Ce qu'il porte | Statut réel |
|---|---|---|---|
| TI-360 | `Question.baseline_cycles` | +1 par round confirmé, RESET si contradiction | Initialisé à 0, jamais confirmé alimenté par un corpus réel |
| TI-360 | `Question.ttl_rounds` | Délai avant `DEGRADING` | Idem — déclaratif dans le schéma, pas observé en usage |
| System C | `ORIGINE.date_captee` | Date de capture d'un FAIT | Date brute déclarée — exactement le modèle que D5 reformulé propose d'abandonner |
| System C | — | Aucun compteur dérivé équivalent à `baseline_cycles`/`ttl_rounds` au niveau `FAIT` | N'existe pas |

Constat de départ : les deux systèmes sont **asymétriques**, pas convergents. TI-360 a un champ dérivé jamais alimenté ; System C a une date brute jamais remise en question. Aucun des deux ne constitue à ce stade une preuve de quoi que ce soit — c'est le point de départ, pas une conclusion.

## 3. Question méthodologique posée par Andrei : modifier le schéma, ou analyser le corpus existant ?

**Réponse proposée : analyser d'abord. Ne pas toucher au schéma tant que l'audit n'a pas produit un cas concret.**

Justification :
- Modifier `schema_v0_3` ou la CHARTE de System C *avant* d'avoir observé un échec réel reproduirait exactement le geste que CHARTE §2bis et kb013 §3 mettent en garde contre — une hypothèse de continuité imposée par le haut plutôt qu'une règle qui émerge d'une contrainte constatée.
- `baseline_cycles`/`ttl_rounds` existent déjà dans TI-360 sans avoir jamais été observés en usage réel. L'étape utile n'est pas de les modifier ou de les étendre à `Extraction` — c'est de vérifier s'ils ont *jamais* servi à quoi que ce soit dans un corpus TOML réel.

## 4. Protocole en deux volets indépendants

### Volet A — TI-360 : audit du corpus existant (pas de nouveau code)

1. Sur le corpus TOML réel (`kb.py`), chercher toute `Question` où `baseline_cycles > 0` ou `ttl_rounds > 0`.
2. Si le résultat est vide : les champs D-SIG sont un schéma déclaré sans donnée — ce n'est ni une confirmation ni une infirmation de la reformulation D5, c'est une absence d'évidence. Le protocole s'arrête là pour ce volet tant qu'aucun cycle réel n'a produit de donnée.
3. Si le résultat est non vide : documenter chaque cas nommé (comme kb013 l'exige) — quelle Question, combien de cycles, est-ce que `DEGRADING` a jamais été atteint, et qu'est-ce que ça a changé dans une `Decision`.

### Volet B — System C : ne pas implémenter, observer d'abord le comportement réel

1. Ne pas ajouter de compteur dérivé au schéma FAIT/GARDE maintenant.
2. Sur les cas réels déjà rencontrés par `resoudre_conflits.py` (s'il y en a eu), vérifier après coup : est-ce qu'un FAIT en conflit aurait été résolu différemment si sa fraîcheur avait été un compteur dérivé plutôt que `date_captee` brute ? C'est une réévaluation rétrospective, pas une implémentation.
3. Si aucun conflit réel n'a encore eu lieu dans System C, ce volet reste en attente — pas de donnée, pas de test possible. Le premier livrable (API enrichie / espace des FAITS) est l'occasion d'observer ça en marchant, pas de le construire par anticipation.

### Ce que les deux volets ont en commun, sans partager de vocabulaire

Le pattern à surveiller, indépendamment dans les deux corpus : **identité par contenu (hash/chaîne) pour D4**, **compteur dérivé plutôt que date déclarée pour D5**, **taux/seuil tenu hors de l'objet ontologique, au niveau opérationnel**. Si les deux corpus font émerger ce pattern séparément, sans que l'un ait copié l'autre, c'est un signal au sens ÉTAU — pas avant.

## 5. Hypothèses formelles

- **H0** — Les champs `baseline_cycles`/`ttl_rounds` (TI-360) et une éventuelle fraîcheur dérivée sur `FAIT` (System C) sont sans rapport structurel : une coïncidence de vocabulaire, pas un invariant partagé.
- **H1** — Les deux instancient, indépendamment, le même motif : fraîcheur comme propriété dérivée de la structure plutôt que comme date déclarée. Confirmer H1 renforcerait la reformulation D5 comme candidate à un axiome révisé, pas encore comme axiome validé.

## 6. Ce qui compterait comme divergence — et ce que ça apprendrait

Si l'audit du Volet A montre que `baseline_cycles`/`ttl_rounds` n'ont jamais servi à rien de décisif, et que le Volet B montre que `date_captee` brute a toujours suffi à `resoudre_conflits.py` sans qu'un compteur dérivé n'aurait rien changé — ce n'est pas un échec du protocole. C'est une information réelle : ça suggérerait que la fraîcheur-dérivée est une solution à un problème que ni System C ni TI-360 n'ont encore réellement rencontré, et que D5 reste, pour l'instant, correctement formulée comme une déclaration simple (date + horloge murale) tant qu'aucun cas concret n'exige mieux. Une hypothèse élégante sans cas d'usage n'est pas fausse — elle est prématurée, ce qui est différent et doit être nommé comme tel plutôt que forcé.

## 7. Seuil de convergence actée

Convergence ne devrait être déclarée que si **toutes** les conditions suivantes sont réunies :
1. Les deux volets produisent chacun **au moins deux cas concrets, nommés** (pas un seul — kb013 documente trois itérations avant la correction finale sur `graph_bridge.py`, un seul cas n'a jamais suffi dans ce corpus).
2. Le motif observé (identité par hash + fraîcheur dérivée) apparaît dans les deux corpus **sans qu'aucun n'ait lu ou copié l'autre** au moment de sa construction — condition déjà respectée par construction (CHARTE §0, isolation stricte).
3. Une contestation explicite (une instance cherchant activement un contre-exemple, pas seulement confirmant) échoue à produire un cas où le motif ne tient pas.

En-dessous de ce seuil : documenter comme HYPOTHÈSE compatible, jamais comme CONFIRMÉ — même si les premiers signaux semblent favorables.

## 8. Prochain geste concret

Aucun code, aucun schéma modifié. Le seul prochain geste utile est le **Volet A, étape 1** : une requête en lecture seule sur le corpus TOML existant de TI-360 pour savoir si `baseline_cycles`/`ttl_rounds` ont jamais dépassé zéro. C'est vérifiable immédiatement, sans risque, et ça détermine si ce protocole a quoi que ce soit à observer avant même de toucher à System C.

---

*Protocole v0.1 · statut HYPOTHÈSE DE MÉTHODE · aucune donnée collectée à ce jour*
