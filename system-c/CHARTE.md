# CHARTE — Phase 2 (System C)

**Ce fichier est la frontière du projet. Le lire en entier avant toute
action, avant de lire quoi que ce soit d'autre dans ce dépôt.**

---

## 0. Règle d'isolation — à respecter avant tout le reste

Ce projet est un nouveau départ. Il ne dépend d'aucun scraping de site
web existant, d'aucun graphe sémantique préexistant, d'aucune migration
en cours ailleurs dans ce dépôt.

**Interdits, sans exception, sauf instruction explicite et nouvelle
d'Andrei :**
- Lire ou importer quoi que ce soit depuis `data/corpus_raw_v2/`
- Lire ou importer quoi que ce soit depuis `dist/`
- Lire ou importer quoi que ce soit lié à Graphify (graphe, embeddings,
  communautés)
- Utiliser un slug metiers-quebec.org comme identifiant, provisoire ou
  non
- Fusionner ou fusionner mentalement ce projet avec « le projet de
  migration de metiers-quebec.org »

Si une tâche semble nécessiter l'une de ces sources, **s'arrêter et
demander à Andrei** plutôt que de supposer que c'est autorisé. C'est
exactement ce qui a échoué la première fois : une instruction d'isolation
donnée à l'oral, jamais vérifiée dans les faits. Ce fichier existe pour
que la vérification n'ait plus besoin de mémoire ou de bonne volonté —
elle est écrite ici, en premier.

## 1. Objectif

Construire une représentation du sens — ici, la connaissance sur les
métiers et l'emploi au Québec — qui reste **portable et cohérente
indépendamment de son conteneur**. Le conteneur (site web, API, base de
données, format de sérialisation) est une vue temporaire sur cette
représentation, jamais la représentation elle-même.

Ce que ça veut dire concrètement :
- Si on change de moteur de recherche, de base de données, ou de
  technologie web demain, la représentation du sens ne doit pas changer.
- Le conteneur doit pouvoir être supprimé et reconstruit sans perte, à
  partir de la représentation elle-même.
- Les données ne « meurent » jamais dans un format final unique — elles
  transitent par des représentations qui gardent leur provenance.

## 2. Point de départ — un seul fichier

`sources-emploi-quebec.json` — le catalogue des sources tierces
(gouvernementales, institutionnelles) sur l'emploi et les métiers au
Québec. C'est le seul point d'ancrage de départ. Tout le reste se
construit à partir de lui, pas à partir d'un site web existant à migrer.

Aucune autre source de départ n'est présumée. Si une nouvelle source
doit être ajoutée, elle entre par le catalogue, avec sa propre entrée,
pas par contournement.

## 2bis. Généalogie du vocabulaire — d'où vient D/L/C/I, et à quel titre

Le vocabulaire de la §3 (FAIT/GARDE/ORIGINE/CODE) et la notion de GARDE
comme invariant testable descendent d'un cadre formalisé dans un autre
projet (`kb008`, Phase 1 — migration de metiers-quebec.org), lui-même
produit à partir d'un seul cas concret : un bug de collision de préfixe
entre deux slugs siblings dans un graphe sémantique.

Ce cadre pose trois couches — Données (D, un ensemble d'entités avec un
invariant de structure attendu), Logique (L, les règles qui transforment
D), Contradiction (C, une violation prouvée de l'invariant) — et une
hypothèse plus large : ces invariants (I) appartiendraient à un langage
formel abstrait (LFA) indépendant de tout substrat qui les porte (code,
données, pensée humaine ou vectorielle).

**Ce qu'il faut dire clairement ici, pour ne pas répéter l'erreur déjà
commise une fois avec ce même cadre (voir `kb013` §3, note sur la
contamination PCCD/RKA/DUO) :**

- Ce cadre D/L/C/I n'a été démontré que sur **un seul cas** (le bug
  `graph_bridge.py`). Le généraliser à System C, un projet aux besoins
  différents (résolution de conflits multi-sources, représentation
  d'états dans le temps), est une **hypothèse de continuité**, pas une
  loi transférée avec preuve.
- L'extension temporelle (représenter une suite d'états plutôt qu'un
  invariant figé, nécessaire ici pour GARDE-IRRÉVERSIBILITÉ et
  `completude`) n'a **jamais fait partie du cadre original** — elle a
  été ajoutée après coup, dans une discussion distincte, sans être
  elle-même vérifiée sur un cas concret avant d'atterrir ici.
- **L'alternative non retenue** : dériver un vocabulaire entièrement
  nouveau, propre aux besoins réels de System C, sans réutiliser D/L/C/I
  ni le mot GARDE. Cette option aurait évité tout héritage non
  réexaminé, au prix de perdre un processus de détection qui, lui,
  s'est avéré concret et efficace en Phase 1 (trois itérations
  documentées, la dernière correcte et vérifiée).

**Décision assumée** : réutiliser le squelette D/L/C/I et le mot GARDE
comme point de départ, précisément parce que le *processus* de détection
qu'il encode (extraire la logique, tester contre les données réelles,
prouver la violation, corriger l'invariant plutôt que patcher au cas par
cas) a fait ses preuves indépendamment du domaine. Mais ce choix reste
révisable : si les GARDES de System C (§4) s'avèrent mal ajustées aux
problèmes réels rencontrés ici — pas à ceux de `graph_bridge.py` — le
vocabulaire doit être corrigé ou abandonné, pas préservé par inertie
parce qu'il vient d'ailleurs et sonne déjà formel.

Aucune autre filiation externe (PCCD, RKA, DUO, ou tout autre cadre de
gouvernance) n'entre dans ce projet sans être documentée ici, avec la
même franchise sur ce qui est prouvé et ce qui est hypothèse.

## 3. Vocabulaire retenu

Quatre concepts, choisis pour ce qu'ils font dans ce système, pas
d'après un standard externe qu'ils imiteraient.

### FAIT
Unité atomique de donnée : une seule valeur, pour un seul champ, d'un
seul objet (ici, un métier), avec sa provenance.
```
FAIT = { champ, valeur, origine }
```
Indivisible. On ne le fragmente pas, on ne le fusionne pas avec un autre
FAIT sans passer par une GARDE.

### ORIGINE
Provenance attachée à chaque FAIT.
```
ORIGINE = {
  source: str,
  date_captee: "AAAA-MM-JJ",
  methode: "scraping" | "manuel" | "api",
  confiance: "haute" | "moyenne" | "basse",
  reference: str (optionnel, URL de la page source)
}
```

### CODE
Identifiant canonique et stable de l'objet décrit. Pour ce projet : le
code CNP 2021 dès le départ — pas de slug provisoire, pas de mapping à
résoudre après coup, puisqu'on ne part d'aucun site web dont hériter un
slug.

### GARDE
Règle testable automatiquement qui vérifie qu'un ensemble de FAITS
respecte un invariant.
```
GARDE = fonction(ensemble_de_FAITS) → { conforme: bool, violations: [...] }
```

### completude
Déclaration explicite, champ par champ, de présence ou d'absence d'une
donnée. Un champ absent doit être marqué `false`, jamais simplement omis.

## 4. Les GARDES retenues au départ

Cinq invariants, dérivés des besoins propres de ce projet — pas importés
tels quels d'un cadre de gouvernance externe sans re-justification ici :

| GARDE | Vérifie | Pourquoi ici, précisément |
|---|---|---|
| Partition | Un `code` n'apparaît jamais deux fois | Un métier = une fiche, jamais dupliquée par erreur de source |
| Autojugement | Une source ne fixe jamais elle-même sa `confiance` comme critère de résolution | Avec plusieurs sources tierces en entrée dès le départ, aucune ne doit pouvoir s'auto-arbitrer face à une autre |
| Non-réécriture | La `valeur` d'un FAIT ne s'écarte pas sémantiquement de sa source | Empêche la paraphrase ou l'interprétation silencieuse lors de l'ingestion |
| Irréversibilité | Un FAIT existant n'est jamais écrasé, seulement complété | Préserve l'historique des états — condition nécessaire pour représenter une connaissance qui évolue dans le temps, pas juste un instantané |
| Complétude explicite | Chaque champ mentionné a une entrée `completude` correspondante | Empêche le silence sur ce qui manque |

Si d'autres GARDES sont ajoutées plus tard, elles doivent être justifiées
par un besoin réel constaté dans ce projet — pas importées d'un autre
cadre de gouvernance sans réexamen explicite de leur pertinence ici.

## 5. Ce qu'on ne fait pas, et pourquoi

- **Pas de mapping slug → CODE.** Il n'y a pas de slug à mapper : on part
  du CNP directement, dès le premier FAIT ingéré.
- **Pas de site A ou B à égaler.** Aucun contenu existant à reproduire
  fidèlement — la question n'est pas « avons-nous tout capturé d'une
  source unique » mais « chaque FAIT capturé est-il correctement
  attribué et vérifiable ».
- **Pas de graphe sémantique au démarrage.** Un graphe de connaissances
  peut être construit plus tard, comme consommateur des FAITS déjà
  structurés — jamais comme dépositaire des données lui-même. Tant qu'il
  n'est pas nécessaire pour répondre à un besoin réel, ne pas
  l'introduire.

## 6. Structure de départ (à ajuster, pas figée)

```
system-c/
├── CHARTE.md                    # ce fichier
├── sources-emploi-quebec.json   # catalogue des sources — point de départ unique
├── scripts/
│   ├── gardes.py                 # les 5 GARDES, stdlib pur
│   ├── test_gardes.py            # tests unitaires
│   ├── resoudre_conflits.py      # résolution de conflits par confiance
│   └── ingest_<source>.py        # un ingesteur par source du catalogue
├── data/
│   └── atomic/{code_cnp}.json    # une fiche par métier, format FAIT
└── docs/
    └── (nouveau, propre à ce projet — pas de renumérotation kb00X hérité)
```

## 7. Comment vérifier qu'on n'a pas dérivé

Test simple, à repasser périodiquement : est-ce qu'un fichier de ce
projet fait référence à `metiers-quebec.org`, `corpus_raw_v2`, `dist/`,
`Graphify`, ou un slug de métier en français simple (`vendeur`,
`infirmier`) plutôt qu'un code CNP ? Si oui, quelque chose a fusionné à
nouveau les deux projets — s'arrêter et vérifier avec Andrei avant de
continuer.
