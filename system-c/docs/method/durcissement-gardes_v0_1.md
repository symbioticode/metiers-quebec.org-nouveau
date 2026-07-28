# Durcissement — code de type GARDE (fonctions de vérification d'invariant)

**Statut : référence opérationnelle légère.** S'applique à tout futur code du type de `gardes.py` — une fonction pure `(données) -> {"conforme": bool, "violations": [...]}`, sans effet de bord. Ne remplace pas la méthodologie de sprint (`methodologie-agentique-system-c.md`) — s'y insère comme checklist à passer avant qu'une GARDE soit considérée solide, pas comme un nouveau processus séparé.

**Pourquoi ce document existe** : `gardes.py` est correct dans son intention (une fonction par axiome, aucune dépendance externe) mais deux failles réelles s'y sont produites malgré ça — un FAIT fabriqué a vécu dans le corpus de production sans qu'aucune GARDE ne le détecte, et une citation de provenance externe (DUO, RKA) est restée en commentaire de code sans jamais passer par un document de filiation déclaré. Aucune des deux n'est un problème de logique de la fonction elle-même — les deux sont des trous *autour* de la fonction.

---

## 1. Provenance de la donnée vérifiée, pas seulement de la donnée écrite

Une GARDE vérifie la forme d'un FAIT déjà présent. Elle ne vérifie jamais comment ce FAIT est arrivé là. C'est le trou exact qui a permis la fabrication de données dans `data/atomic/` : la valeur avait la bonne forme, donc `garde_autojugement` et consorts n'y voyaient rien à redire.

**Règle** : aucun FAIT n'entre dans un corpus de production sans provenir d'un commit d'ingestion tracé et nommé (`ingest_<source>.py`, jamais une édition manuelle du JSON de production, même à des fins de test ou de démonstration). Si un test a besoin de données synthétiques, elles vivent dans `fixture/`, jamais dans `data/atomic/`.

## 2. Toute GARDE doit prouver qu'elle sait dire non

`resoudre_conflits.py` a un `test_egalite()` — un cas synthétique garanti pour vérifier que le chemin « non résolu » se déclenche. C'est le bon réflexe, à généraliser : une suite de tests qui ne contient que des cas où la GARDE doit répondre `conforme: True` ne prouve rien sur sa capacité à détecter une vraie violation.

**Règle** : toute nouvelle GARDE est livrée avec au minimum un cas de test qui la force à retourner `conforme: False`, construit délibérément pour ça — pas découvert après coup.

## 3. Cas adversariaux minimaux avant tout usage en production

Liste plancher à couvrir, même pour une GARDE qui semble triviale :

```
□ Entrée vide ("", [], {})
□ Entrée None / champ manquant
□ Valeur à la limite exacte du seuil (si la GARDE utilise un seuil numérique,
  comme garde_non_reecriture)
□ Deux entrées distinctes mais quasi identiques (le cas qui a fait tomber
  cnp_check() ailleurs — pertinent dès qu'il y a comparaison de deux clés)
```

Une GARDE qui n'a jamais été confrontée à ces cas n'est pas considérée solide, même si tous ses tests existants passent.

## 4. La GARDE ne tranche jamais — elle rapporte

Une GARDE renvoie `{"conforme": bool, "violations": [...]}`. Elle ne corrige jamais silencieusement, ne choisit jamais une valeur par défaut en cas d'ambiguïté, ne complète jamais un champ manquant. Si la GARDE elle-même a besoin de trancher quelque chose (quelle source gagne, quelle valeur retenir), ce n'est plus une GARDE — c'est un résolveur (`resoudre_conflits.py`), qui suit ses propres règles, notamment ne jamais choisir arbitrairement en cas d'égalité.

## 5. Citer une source externe, oui — mais jamais seulement en commentaire

`gardes.py` cite `DUO — axiome D5`, `PCCD INV-01 / RKA-INV-01` directement en docstring. Ce n'est pas un dommage en soi (le grep de vérification l'a confirmé : aucune conséquence fonctionnelle) — mais c'est une filiation qui n'a jamais été déclarée ailleurs que dans le code, invisible à quiconque lit CHARTE.md sans lire aussi le code source ligne par ligne.

**Règle** : si une GARDE traduit un principe externe (un axiome DUO, un invariant RKA/PCCD, un cadre comme LFA), la citation en commentaire de code reste — c'est utile pour qui lit le code — mais la filiation elle-même doit aussi apparaître dans un document déclaré (GLOSSAIRE.md ou équivalent), pas seulement dans le code. Sinon, une future relecture de CHARTE.md seule ne révèle jamais cette dépendance.

---

## Ce que ce document ne demande pas

Pas de suite de personas adversariaux, pas de score go/no-go numérique, pas d'instance Analyste isolée. L'échelle actuelle de System C ne justifie pas ce coût. Cette checklist se passe en quelques minutes par GARDE, pas en sprint dédié.
