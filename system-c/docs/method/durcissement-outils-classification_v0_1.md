# Durcissement — outils de classification/matching à conséquence externe

**Statut : référence opérationnelle légère.** S'applique à tout futur code du type de `cnp_check()` — un outil qui compare, matche ou classe des clés dont le résultat peut avoir une conséquence en dehors du système (juridique, financière, irréversible pour un tiers). Ne remplace pas la méthodologie de sprint — s'y insère comme checklist obligatoire avant qu'un tel outil serve à trancher quoi que ce soit.

**Pourquoi ce document existe** : `cnp_check()` a confondu deux ordres professionnels réglementés distincts (infirmière autorisée / infirmière auxiliaire) parce qu'un matching par sous-chaîne sur texte libre a été utilisé pour arbitrer une distinction dont on savait déjà, avant même d'écrire l'outil, qu'elle avait des conséquences réelles (permis de travail, reconnaissance d'ordre). L'outil annonçait « 16 tests, tous passent » — aucun de ces tests ne couvrait une chaîne vide, une valeur `None`, ou une collision entre deux codes voisins.

---

## 1. Nommer la conséquence avant d'écrire une ligne de code

Avant de choisir une méthode d'implémentation : est-ce que cette clé/distinction a un effet en dehors du système (statut légal, éligibilité, montant, décision irréversible) ?

- **Si oui** — le mode « best effort silencieux » est interdit dès la conception. Toute ambiguïté ou entrée invalide doit lever une erreur explicite, jamais retourner un `True`/`False` par défaut qui masque le doute.
- **Si non** — le texte libre et le matching approximatif restent acceptables, l'enjeu ne le justifie pas autrement.

## 2. Choix d'implémentation proportionné à la conséquence

Dès qu'une distinction a une conséquence réelle (règle 1), préférer une correspondance exacte sur une liste fermée et normalisée à un matching par sous-chaîne sur texte libre. Le texte libre laisse `"" in x` toujours vrai, laisse une abréviation d'un métier matcher un autre par accident — ce n'est pas un cas limite exotique, c'est le comportement par défaut d'un substring match non gardé.

## 3. Suite de tests adversariaux obligatoire *avant* tout usage pour trancher

Pas après un premier usage en production — avant. Liste plancher :

```
□ Chaîne vide
□ None / valeur absente
□ Type invalide (non-string là où une string est attendue)
□ Casse différente (majuscules/minuscules)
□ Singulier vs pluriel
□ Entités HTML non décodées (ex. &rsquo;)
□ Collision connue entre deux clés voisines dans le domaine
  (si le domaine a déjà une distinction sensible identifiée — ici,
  31301/32101 était connue avant même l'écriture de l'outil)
```

Si le domaine a un cas connu et documenté à l'avance (comme ici, infirmier/infirmier auxiliaire), ce cas précis doit être le **premier** testé, pas découvert après coup par un audit externe.

## 4. « N tests passent » n'est pas une preuve de robustesse

Un test qui confirme ce que l'auteur avait déjà en tête en écrivant la fonction n'est pas un test, c'est une répétition. Une suite de tests n'est recevable comme preuve de robustesse que si elle couvre explicitement chacun des cas de la liste §3 — sinon, l'annoncer comme validé est un patch fable, pas un résultat.

## 5. Test à l'échelle réelle avant confiance générale

Si l'outil touche une matrice ou un référentiel complet, il doit être testé contre l'ensemble du référentiel (balayage exhaustif), pas seulement contre l'échantillon utilisé aujourd'hui. Un audit ciblé sur 5 cas ne détecte pas une collision qui n'apparaît qu'au 400ᵉ élément.

## 6. Une correction n'est pas auto-vérifiée

Toute correction d'un tel outil est revérifiée par une main différente de celle qui l'a écrite avant d'être déclarée fiable — jamais par l'instance qui vient de produire le correctif. Si un audit exhaustif (§5) a été relancé après correction, son résultat lui-même suit la même règle : quelqu'un d'autre que le correcteur confirme qu'il est correct.

---

## Ce que ce document ne demande pas

Pas de conseil de personas adversariaux, pas de score go/no-go, pas d'instance Analyste dédiée. Le niveau de rigueur demandé est proportionné au fait que l'erreur touche un statut réel, pas à l'ambition du projet — cette checklist s'applique en une passe, avant le premier usage de l'outil pour trancher quoi que ce soit, pas comme un processus récurrent.
