# kb008-bis — Nomenclature interne : du LFA aux specs fonctionnelles retenues

## Contexte

kb008 formalise une couche d'invariants (I) indépendante du substrat (D/L/I/C).
Cette suite répond à une question pratique : avant de bâtir le format atomique
de « système C », faut-il importer une pile de standards externes (RDF, OWL,
SHACL, PROV-O, JSON-LD, ESCO, O*NET...) ou en extraire seulement les
**principes fonctionnels**, sous une nomenclature propre au projet ?

Décision : la seconde option. La matrice complète est dans la conversation
qui a produit ce document. Résumé : sur 8 standards examinés, 3 principes
fonctionnels distincts survivent, et 2 existent déjà dans le projet sous
d'autres noms (CNP comme clé canonique, « garde » comme invariant testable
dans kb008 lui-même).

## Principe de nomenclature

**On ne nomme jamais un concept d'après le standard qui l'a documenté.**
On nomme d'après ce qu'il fait dans notre système. Si demain on doit changer
de technologie (autre moteur d'embeddings, autre base, autre format de
sérialisation), les quatre mots ci-dessous ne changent pas — parce qu'ils
décrivent I, pas S_A.

## Les quatre concepts retenus

### 1. FAIT

Unité atomique de donnée. Remplace la notion de « triple RDF » sans en
importer la syntaxe.

```
FAIT = (code_metier, champ, valeur, origine)
```

- `code_metier` : identifiant canonique (voir §4)
- `champ` : nom du concept décrit (`salaire_median`, `formation_requise`, ...)
- `valeur` : la donnée elle-même
- `origine` : voir §3

Un FAIT est indivisible : on ne le fragmente pas, on ne le fusionne pas avec
un autre FAIT sans passer par une GARDE.

### 2. GARDE

Règle testable automatiquement qui vérifie qu'un ensemble de FAITS respecte
un invariant. C'est le mot déjà utilisé dans kb008 pour la correction du
bug de collision `vendeur`/`vendeur_autos` — on le généralise ici comme
concept de premier plan plutôt que comme détail de correction ponctuelle.

```
GARDE = fonction(ensemble_de_FAITS) → { conforme: bool, violations: [...] }
```

Exemples de GARDES pour ce projet :
- partition disjointe : deux `code_metier` distincts ne partagent jamais
  le même FAIT
- provenance obligatoire : aucun FAIT sans `origine`
- non-vacuité : un `champ` marqué absent doit l'être explicitement
  (`completude: false`), jamais par omission silencieuse

Une GARDE se code en Python aujourd'hui, pourrait se coder en SHACL demain,
ou se vérifier à la main par un humain — la GARDE elle-même ne change pas,
seule son exécution change de substrat.

### 3. ORIGINE

Métadonnée de provenance attachée à chaque FAIT. Remplace PROV-O sans en
importer l'ontologie complète — on ne retient que le besoin réel : savoir
d'où vient une donnée et avec quelle confiance.

```
ORIGINE = {
  source: "metiers_quebec" | "imt_en_ligne" | "isq" | ...,
  date_captee: "2026-07-21",
  methode: "scraping" | "manuel" | "api",
  confiance: "haute" | "moyenne" | "basse"
}
```

`confiance` permet d'arbitrer quand deux sources donnent des valeurs
différentes pour le même `champ` (ex. salaire ISQ vs salaire scrapé de
metiers-quebec.org) — la GARDE de résolution de conflit choisit la source
à `confiance` la plus haute, ou signale la divergence si égalité.

### 4. CODE

Identifiant canonique et stable d'un métier. **Décision : c'est le CNP 2021,
déjà utilisé par les 16 sources de `sources-emploi-quebec.json`.** Pas
d'import d'ESCO ni d'O*NET-SOC — ce sont des classifications équivalentes
pour d'autres marchés (UE, US), et en importer une ferait doublon avec ce
qu'on a déjà de fonctionnel pour le Québec/Canada.

```
CODE = code_cnp_2021  (ex. "31301")
```

Note pour plus tard, pas une priorité actuelle : si le projet devait un
jour s'interfacer avec des données européennes ou américaines, un crosswalk
CNP↔O*NET-SOC↔ESCO existe déjà publiquement (maintenu par l'UE et le
département du Travail US) — inutile de le recréer, à consulter seulement
si le besoin se présente.

## Ce qu'on n'importe pas, et pourquoi

| Rejeté | Raison |
|---|---|
| RDF / Turtle / JSON-LD littéral | Ce sont des sérialisations (S_A). FAIT capture le même principe sans imposer une syntaxe particulière — le format d'encodage physique (JSON aujourd'hui) reste un détail d'implémentation, jamais un invariant. |
| OWL | Recouvre en bonne partie GARDE ; l'inférence de classes n'est pas un besoin actuel du projet (420 métiers, pas une taxonomie qui évolue par héritage). |
| SPARQL | Langage de requête pour un graphe RDF distribué — surdimensionné pour un corpus local de cette taille. `query_test.py` (kb007) fait déjà le travail nécessaire. |
| ESCO / O*NET-SOC | Classifications équivalentes à CNP pour d'autres marchés. Les importer maintenant créerait une redondance de clé canonique sans bénéfice actuel. |
| schema.org `Occupation` | Vocabulaire utile *seulement* si site C publie du HTML public avec balisage SEO structuré — à réévaluer au moment de la génération du site, pas au niveau du format atomique. |

## Format atomique révisé (remplace la proposition initiale)

```json
{
  "code": "31301",
  "noms": ["Infirmière", "Infirmier"],
  "secteur": "sante",
  "faits": [
    {
      "champ": "description",
      "valeur": "...",
      "origine": {
        "source": "metiers_quebec",
        "date_captee": "2026-07-15",
        "methode": "scraping",
        "confiance": "moyenne"
      }
    },
    {
      "champ": "salaire_median",
      "valeur": 78000,
      "origine": {
        "source": "isq",
        "date_captee": "2026-05-01",
        "methode": "api",
        "confiance": "haute"
      }
    }
  ],
  "completude": {
    "description": true,
    "salaire": true,
    "qualites": false,
    "formation": false
  }
}
```

Différence avec la version précédente : `champs_consolides` (une structure
ad hoc) est remplacé par une liste de FAITS uniformes, chacun portant sa
propre ORIGINE — ce qui permet d'écrire des GARDES génériques qui
s'appliquent à n'importe quel `champ`, sans code spécial par type de donnée.

## Implication pour le pipeline existant

- `corpus_raw_v2` (kb005) devient une source d'ingestion qui produit des
  FAITS avec `origine.source = "metiers_quebec"`, `confiance = "moyenne"`
  (donnée brute non vérifiée par une source officielle).
- Les 16 sources de `sources-emploi-quebec.json` deviennent, une par une,
  des ingesteurs qui produisent des FAITS avec `confiance` calibrée selon
  le type de source (`api_disponible: true` → confiance plus haute par
  défaut, à ajuster).
- Le graphe sémantique (kb006/kb007) devient un **consommateur** de FAITS,
  pas leur dépositaire — il peut être reconstruit avec un autre modèle
  d'embedding sans jamais toucher au format atomique.

## Emprunts et invariants dérivés

Quatre GARDES dérivées de PCCD/RKA/DUO, formalisées dans kb012 §2 :
- GARDE-AUTOJUGEMENT (PCCD INV-01 / RKA-INV-01)
- GARDE-NON-RÉÉCRITURE (PCCD INV-08 / RKA-INV-08)
- Fraîcheur (DUO axiome D5)
- GARDE-IRRÉVERSIBILITÉ (DUO axiome D4)

## Voir aussi

- **kb012** : implémentation concrète des GARDES, algorithme de résolution
  de conflits, résultats de validation, état de Phase 3
- **scripts/gardes.py** : les cinq GARDES en Python stdlib
- **scripts/test_gardes.py** : 17 tests unitaires
- **scripts/smoke_test_atomique.py** : validation bout-en-bout
