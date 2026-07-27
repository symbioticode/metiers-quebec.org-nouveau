# kb022 — Durcissement adversarial de `cnp_sha_check.py`

**Type de document** : Rapport d'audit (exécution).
**Rôle** : EXÉCUTION — applique la checklist de
`docs/method/durcissement-outils-classification_v0_1.md` §3 à
`scripts/cnp_sha_check.py` (présent sur `phase2-systemc` depuis le merge
`kb021-genome-stability-test` / `experimental/cnp-sha-check`, cf. kb017.md).

**Consigne reçue et respectée** : ne pas corriger `cnp_sha_check.py` (ni
`build_sha_table.py`) si un cas échoue. Documenter, s'arrêter. La décision de
corriger ou d'abandonner l'outil revient à Andrei + Claude.ai après lecture de
ce rapport. **Aucun fichier de code ou de données n'a été modifié pour
produire ce rapport** — seul un script d'audit autonome
(`scripts/audit_durcissement_cnp_sha_check.py`) a été ajouté ; il lit
`cnp_sha_check.py`, `cnp-sha-table.json` et `cnp-appellations-officielles.json`
sans les écrire.

**Résumé exécutif** : 4 cas sur 7 PASS, 3 cas sur 7 FAIL. Le FAIL le plus
sérieux (Cas 6) n'est pas la limitation attendue (absence de
singularisation, connue et documentée dans kb017.md) mais un **bug de
construction découvert par le balayage exhaustif** dans
`build_sha_table.py` : 7 formes masculines réelles, sur 5 CNP dont les
deux CNP au cœur du Cas 1 (31301, 32101), sont indexées sous une forme
corrompue (mot dupliqué) au lieu de la forme correcte — elles ne
valideront donc jamais, silencieusement, sans qu'aucun signal ne
distingue ce cas d'un terme réellement inconnu.

---

## Méthode

Script d'audit : `scripts/audit_durcissement_cnp_sha_check.py`. Commande
d'exécution complète et sortie brute intégrale reproduites ci-dessous, cas
par cas (aucun résumé — copie exacte du terminal). Reproductible avec :

```
python3 scripts/audit_durcissement_cnp_sha_check.py
```

---

## CAS 1 (obligatoire, testé en premier) — collision connue infirmier/infirmière auxiliaire (31301 vs 32101)

**Statut : PASS (avec nuance — voir ci-dessous)**

Origine du cas (kb015.md, Fix 2) : `cnp_check()` validait par erreur
« infirmière auxiliaire » sous 31301 (infirmier autorisé) via une entrée
générique bare `infirmier/infirmière`, alors que 32101 (infirmier
auxiliaire) existe séparément dans la matrice — deux ordres professionnels
réglementés distincts confondus par un matching trop permissif.

Commande + sortie brute (`CAS 1` de l'audit) :

```
$ python3 scripts/audit_durcissement_cnp_sha_check.py
======================================================================
CAS 1 — collision connue 31301 (infirmier autorisé) vs 32101 (infirmier auxiliaire)
======================================================================
31301 'infirmiere auxiliaire' -> {'cnp': '31301', 'terme': 'infirmiere auxiliaire', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers autorisés/infirmières autorisées et infirmiers psychiatriques autorisés/infirmières psychiatriques autorisées'}
31301 'infirmieres auxiliaires' -> {'cnp': '31301', 'terme': 'infirmieres auxiliaires', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers autorisés/infirmières autorisées et infirmiers psychiatriques autorisés/infirmières psychiatriques autorisées'}
31301 'infirmier auxiliaire' -> {'cnp': '31301', 'terme': 'infirmier auxiliaire', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers autorisés/infirmières autorisées et infirmiers psychiatriques autorisés/infirmières psychiatriques autorisées'}
31301 'infirmiers auxiliaires' -> {'cnp': '31301', 'terme': 'infirmiers auxiliaires', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers autorisés/infirmières autorisées et infirmiers psychiatriques autorisés/infirmières psychiatriques autorisées'}
32101 'infirmiere auxiliaire' -> {'cnp': '32101', 'terme': 'infirmiere auxiliaire', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
32101 'infirmieres auxiliaires' -> {'cnp': '32101', 'terme': 'infirmieres auxiliaires', 'cnp_existe': True, 'valide': True, 'type_correspondance': 'exacte', 'matched_hash': 'f13b2b7bf4dbbb9c20dc52ebd908c1980a57c392', 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}

sha_lookup("infirmieres auxiliaires") = 32101
sha_lookup("infirmiere auxiliaire")  = None
sha_lookup("Infirmières auxiliaires") = 32101
```

**Analyse** : aucune des 6 combinaisons testées (formes masculine/féminine,
singulier/pluriel, contre les deux CNP) ne produit de confusion croisée —
31301 ne valide jamais pour un terme « infirmier(ère) auxiliaire », quelle
que soit sa forme. `sha_lookup()` renvoie 32101 (le bon CNP) pour la forme
officielle exacte, et `None` (pas 31301) pour la forme singulière non
indexée. **La collision documentée dans kb017.md ne se reproduit pas.**

**Nuance sur « erreur visible »** (exigence explicite de la consigne) : le
script ne lève **aucune erreur explicite** distincte pour ce cas — il
retourne `valide: False, type_correspondance: 'aucune'`, une sortie
structurellement identique à celle d'un terme complètement inconnu et sans
rapport avec le domaine. Rien dans la sortie ne signale « ceci est un cas de
collision connu, correctement rejeté » par opposition à « ceci est un mot
qui n'existe pas dans la table ». Le script **ne masque pas la confusion**
(la propriété de sécurité recherchée tient), mais il ne la **signale** pas
non plus explicitement — la garantie provient de l'architecture (hachage
exact, jamais de faux positif partiel possible par construction), pas d'une
détection active du cas. À noter pour la décision Andrei/Claude.ai : est-ce
suffisant au sens strict de la règle 1 du protocole (« toute ambiguïté doit
lever une erreur explicite ») ou la garantie architecturale suffit-elle ?

---

## CAS 2 — chaîne vide

**Statut : PASS**

```
======================================================================
CAS 2 — chaîne vide
======================================================================
{'cnp': '32101', 'terme': '', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
sha_lookup('') = None
```

Aucun crash, aucun faux positif. Garde explicite dans le code
(`cnp_sha_check.py` ligne 95-100 : test `not norm` après normalisation).

---

## CAS 3 — None / valeur absente

**Statut : PASS**

```
======================================================================
CAS 3 — None / valeur absente
======================================================================
{'cnp': '32101', 'terme': None, 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
sha_lookup(None) = None
{'cnp': None, 'terme': 'infirmieres auxiliaires', 'cnp_existe': False, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': None}
```

`terme_recherche=None` et `cnp=None` sont tous deux gérés sans exception.

---

## CAS 4 — type invalide

**Statut : FAIL**

```
======================================================================
CAS 4 — type invalide (terme_recherche non-string)
======================================================================
12345 -> {'cnp': '32101', 'terme': 12345, 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
3.14 -> {'cnp': '32101', 'terme': 3.14, 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
['infirmiere auxiliaire'] -> {'cnp': '32101', 'terme': ['infirmiere auxiliaire'], 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
{'x': 1} -> {'cnp': '32101', 'terme': {'x': 1}, 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
True -> {'cnp': '32101', 'terme': True, 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
b'infirmiere auxiliaire' -> {'cnp': '32101', 'terme': b'infirmiere auxiliaire', 'cnp_existe': True, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': 'Infirmiers auxiliaires/infirmières auxiliaires'}
sha_lookup 12345 -> None
sha_lookup 3.14 -> None
sha_lookup ['infirmiere auxiliaire'] -> None
sha_lookup {'x': 1} -> None
sha_lookup True -> None
sha_lookup b'infirmiere auxiliaire' -> None

======================================================================
CAS 4 — type invalide (cnp non-string)
======================================================================
31301 -> {'cnp': 31301, 'terme': 'infirmieres auxiliaires', 'cnp_existe': False, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': None}
None -> {'cnp': None, 'terme': 'infirmieres auxiliaires', 'cnp_existe': False, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': None}
['32101'] -> EXCEPTION TypeError unhashable type: 'list'
32101.0 -> {'cnp': 32101.0, 'terme': 'infirmieres auxiliaires', 'cnp_existe': False, 'valide': False, 'type_correspondance': 'aucune', 'matched_hash': None, 'appellation_principale': None}
```

**Analyse** :
- Côté `terme_recherche` : la garde `isinstance(terme_recherche, str)`
  (ligne 96) intercepte proprement tout type non-string — comportement
  cohérent, pas de crash, pas de faux positif.
- Côté `cnp` : **aucune garde de type n'existe**. Un `cnp` entier (`31301`
  au lieu de `"31301"`) ou flottant (`32101.0`) ne lève aucune erreur et
  retourne silencieusement `cnp_existe: False` — un résultat qui, lu seul,
  laisse croire que le code CNP 31301 n'existe pas dans le référentiel,
  alors que le vrai problème est un type d'appel incorrect. C'est
  exactement le « `True`/`False` par défaut qui masque le doute » que la
  règle 1 du protocole interdit. Un `cnp` non hachable (liste) ne retourne
  pas non plus d'erreur contrôlée : il lève un `TypeError` Python brut et
  non géré (« unhashable type: 'list' »), visible mais pas explicite au
  sens du protocole (pas un message métier, une trace d'implémentation).

---

## CAS 5 — casse différente

**Statut : PASS**

```
======================================================================
CAS 5 — casse différente
======================================================================
'INFIRMIÈRES AUXILIAIRES' -> valide= True type= exacte
'Infirmières Auxiliaires' -> valide= True type= exacte
'infirmières auxiliaires' -> valide= True type= exacte
'InFiRmIèReS aUxIlIaIrEs' -> valide= True type= exacte
```

La normalisation (`_normalize()`, minuscule + retrait des accents) absorbe
toute variation de casse, y compris une casse mixte aléatoire.

---

## CAS 6 — singulier vs pluriel

**Statut : FAIL** (limitation attendue + bug de construction découvert par balayage exhaustif)

```
======================================================================
CAS 6 — singulier vs pluriel
======================================================================
'infirmière auxiliaire' -> valide= False type= aucune
'infirmier auxiliaire' -> valide= False type= aucune
'infirmières auxiliaires' -> valide= True type= exacte
'infirmiers auxiliaires' -> valide= False type= aucune
```

Le premier volet (singulier « infirmière auxiliaire » non reconnu) est la
limitation **connue et documentée** de `cnp_sha_check()` (kb017.md,
Catégorie C : 0/7 sur les variantes jamais vues exactement — propriété du
hachage, pas un bug). Ce n'est pas la partie qui déclenche le FAIL.

Ce qui déclenche le FAIL : **« infirmiers auxiliaires » (masculin pluriel,
forme officielle valide de l'appellation principale de 32101) est aussi
refusé** — alors qu'il s'agit d'une variante grammaticale légitime de la
forme exacte qui, elle, valide (« infirmieres auxiliaires »). Investigation
par balayage exhaustif de la matrice complète (§5 du protocole — pas
seulement l'échantillon du cas testé) :

```
======================================================================
CAS 6 (suite) — sweep exhaustif : bug de construction dans l'expansion '/' (build_sha_table.py)
======================================================================
Appellations avec '/' balayées : sweep complet des 516 CNP de la matrice
Variantes générées avec mot dupliqué consécutif (motif de bug) : 7
  ('33103', 'Assistants techniques/assistantes techniques en pharmacie et assistants/assistantes en pharmacie', 'assistants techniques techniques en pharmacie et assistants/assistantes en pharmacie')
  ('31301', 'infirmier spécialiste/infirmière spécialiste en soins respiratoires', 'infirmier specialiste specialiste en soins respiratoires')
  ('31301', 'infirmier clinique/infirmière clinique', 'infirmier clinique clinique')
  ('31301', 'infirmier scolaire/infirmière scolaire', 'infirmier scolaire scolaire')
  ('32101', 'Infirmiers auxiliaires/infirmières auxiliaires', 'infirmiers auxiliaires auxiliaires')
  ('21320', 'Ingénieurs chimistes/ingénieures chimistes', 'ingenieurs chimistes chimistes')
  ('12200', 'agent budgétaire/agente budgétaire', 'agent budgetaire budgetaire')
```

Cause : `_expand_slash_variants()` dans `build_sha_table.py` (regex
`r"(.+?)(/\S+)(.*)"`) reconstruit la variante masculine en concatenant
`prefix + suffix` — mais quand le mot juste après le « / » (capturé par
`\S+`, glouton mais borné aux caractères non-blancs) ne couvre pas tout le
mot féminin suivant le préfixe, le suffixe restant se retrouve dupliqué
(« auxiliaires auxiliaires », « clinique clinique », etc.) au lieu de la
forme masculine correcte (« infirmiers auxiliaires », « infirmier
clinique », etc.). Vérification (intégrée au script d'audit) que les formes masculines
correctes (mot dupliqué retiré) ne sont **pas** indexées sous une autre
variante :

```
Vérification : la forme masculine correcte (mot dupliqué retiré) est-elle indexée quand même (sous une autre variante) ?
  33103: forme masculine correcte attendue = 'assistants techniques en pharmacie et assistants/assistantes en pharmacie' -> indexée: False
  31301: forme masculine correcte attendue = 'infirmier specialiste en soins respiratoires' -> indexée: False
  31301: forme masculine correcte attendue = 'infirmier clinique' -> indexée: False
  31301: forme masculine correcte attendue = 'infirmier scolaire' -> indexée: False
  32101: forme masculine correcte attendue = 'infirmiers auxiliaires' -> indexée: False
  21320: forme masculine correcte attendue = 'ingenieurs chimistes' -> indexée: False
  12200: forme masculine correcte attendue = 'agent budgetaire' -> indexée: False
```

**Confirmé : les 7 formes masculines correctes ne sont indexées sous
aucune variante.** Elles retournent silencieusement `valide: False,
type_correspondance: 'aucune'`, indistinguable d'un terme réellement
inconnu — alors qu'il s'agit d'une appellation officielle réelle mal
construite par un bug de la chaîne de construction de la table, pas d'un
terme jamais vu par le domaine.

**Portée** : 7 appellations touchées sur 516 CNP × ~2352 entrées (sweep
exhaustif complet de la matrice, pas un échantillon). Touche 5 CNP :
33103, 31301, 32101, 21320, 12200 — dont **les deux CNP au centre du Cas 1**
(31301, 32101). Le bug n'introduit aucune confusion inter-CNP (aucune des
formes corrompues ne pointe vers le mauvais CNP — vérifié : Cas 1 reste
PASS), mais il dégrade silencieusement la couverture exactement là où la
rigueur était la plus attendue.

---

## CAS 7 — entités HTML non décodées

**Statut : FAIL**

```
======================================================================
CAS 7 — entités HTML non décodées
======================================================================
'infirmières auxiliaires' | 32101: True exacte | 72300: False aucune
'infirmi&egrave;res auxiliaires' | 32101: False aucune | 72300: False aucune
'plombiers/plombi&egrave;res' | 32101: False aucune | 72300: False aucune
'Plombiers/plombières' | 32101: False aucune | 72300: True exacte

======================================================================
Vérification source : entités HTML restantes dans cnp-appellations-officielles.json
======================================================================
Entités HTML restantes dans la matrice source : 0
```

**Analyse** : `_normalize()` ne fait aucun `html.unescape()`. Un terme de
recherche entrant contenant une entité HTML non décodée (ex. scrapé d'une
offre d'emploi réelle, « &egrave; » au lieu de « è ») échoue à valider
même quand la forme équivalente décodée valide correctement — sans aucune
distinction avec un terme réellement inconnu. La matrice source elle-même
est propre (0 entité restante, nettoyage confirmé par kb015.md), donc ce
n'est pas un problème de données de référence, mais d'absence de
traitement des entrées au moment de la requête.

**Note de portée** : `cnp_check.py` utilise la **même** fonction
`_normalize()` (vérifié — aucun appel à `html.unescape` dans
`cnp_check.py` non plus). Ce n'est donc pas une régression propre à
`cnp_sha_check.py` par rapport à son prédécesseur — kb015.md décrit un
nettoyage ponctuel de la matrice source (139 `&rsquo;` → 0), pas un
traitement des entrées utilisateur au moment de l'appel. Le FAIL est réel
et touche les deux outils identiquement.

---

## Couverture de la suite de tests existante (`test_cnp_sha_check.py`)

23/23 tests déclarés passent — mais la règle 4 du protocole (« N tests
passent n'est pas une preuve de robustesse ») s'applique directement ici :
sur les 23 tests, aucun ne couvre le Cas 4 (type invalide autre que
`None`), aucun ne couvre le Cas 7 (entités HTML), et aucun ne couvre le
bug de construction du Cas 6 (formes masculines corrompues). Les noms de
tests existants (sortie brute) :

```
test_empty_string_never_valid ... ok
test_exact_appellation_principale_12200 ... ok
test_exact_appellation_principale_64100 ... ok
test_exact_appellation_principale_72300 ... ok
test_exact_autre_appellation_21222 ... ok
test_exact_case_insensitive_31301 ... ok
test_exact_forme_slash_complete_31301 ... ok
test_exact_slash_variant_plombier ... ok
test_no_hash_collision_in_table ... ok
test_none_terme_no_crash ... ok
test_nonexistent_cnp ... ok
test_sha_lookup_21222 ... ok
test_sha_lookup_connu ... ok
test_sha_lookup_inconnu ... ok
test_sha_lookup_none ... ok
test_sha_lookup_variante_slash ... ok
test_sha_lookup_vide ... ok
test_table_has_all_target_cnps ... ok
test_table_nb_entrees_coherent ... ok
test_unknown_partial_plombier_mecanique ... ok
test_unknown_variant_infirmier_autorise ... ok
test_unknown_variant_infirmiere_auxiliaire_singulier ... ok
test_whitespace_only_never_valid ... ok

Ran 23 tests in 0.012s
OK
```

---

## Tableau récapitulatif

| Cas | Description | Statut |
|---|---|---|
| 1 | Collision connue 31301/32101 (infirmier/infirmière auxiliaire) | **PASS** (nuance : pas d'erreur explicite, garantie architecturale seulement) |
| 2 | Chaîne vide | **PASS** |
| 3 | None / valeur absente | **PASS** |
| 4 | Type invalide | **FAIL** (`cnp` non gardé — silencieux pour int/float, exception brute non contrôlée pour liste) |
| 5 | Casse différente | **PASS** |
| 6 | Singulier vs pluriel | **FAIL** (limitation attendue + bug de construction réel dans `build_sha_table.py`, 7 formes masculines corrompues sur 5 CNP dont 31301/32101) |
| 7 | Entités HTML non décodées | **FAIL** (partagé avec `cnp_check.py`, pas une régression propre à cet outil) |

**4/7 PASS, 3/7 FAIL.**

---

## Ce que ce rapport ne fait pas

Conformément à la consigne reçue : aucune correction n'a été appliquée à
`cnp_sha_check.py` ni à `build_sha_table.py` ni à la table SHA générée.
Le bug du Cas 6 (mots dupliqués dans l'expansion « / ») n'est pas corrigé
ici — seulement localisé et quantifié par balayage exhaustif. La décision
de corriger, de reformuler l'outil, ou de l'abandonner revient à Andrei +
Claude.ai après lecture de ce rapport.
