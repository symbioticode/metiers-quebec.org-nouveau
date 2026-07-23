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

## Emprunts validés depuis PCCD / RKA / DUO

Revue du corpus élargi (PCCD_Doc1_Hypothesis_v0_5, SYNAPSE_Architecture_v0_1,
DUO_Fondements_Theoriques_v0_1, RKA_Formalisation_v4) pour vérifier si des
invariants déjà formalisés ailleurs dans l'écosystème s'appliquent sans
alourdir kb008-bis. Quatre éléments retenus, traduits dans notre nomenclature
(FAIT/GARDE/ORIGINE/CODE) — aucun nouvel acronyme importé.

### GARDE-AUTOJUGEMENT (source : PCCD INV-01 / RKA-INV-01)

Une source ne fixe jamais elle-même sa propre `confiance`. Si `imt_en_ligne`
et `metiers_quebec` divergent sur un `salaire_median`, la GARDE de résolution
de conflit — pas l'un des deux ingesteurs — tranche. Un ingesteur ne fait que
proposer un FAIT avec son ORIGINE ; il ne se prononce jamais sur sa propre
fiabilité relative aux autres sources.

### GARDE-NON-RÉÉCRITURE (source : PCCD INV-08 / RKA-INV-08)

`valeur` d'un FAIT ne doit jamais s'écarter sémantiquement de la source
brute (`sources_raw` / `corpus_raw_v2`). Toute normalisation (nettoyage de
newlines, extraction depuis texte scrapé) doit rester vérifiable par
comparaison directe avec le brut — pas de paraphrase ou d'interprétation
introduite silencieusement lors de l'ingestion.

### Fraîcheur (source : DUO — axiome D5)

Un FAIT non reconfirmé perd sa validité présumée avec le temps. On n'ajoute
pas de champ à remplir manuellement — `perimee` est **dérivé**, pas stocké :

```
perimee(FAIT) = (aujourd'hui - FAIT.origine.date_captee) > seuil(FAIT.champ)
```

Seuils par défaut, ajustables : `salaire_median` périmé après 1 an,
`description`/`formation` après 3 ans (contenu plus stable). Sans ce calcul,
un salaire de 2023 non marqué se présenterait comme aussi valide qu'un
salaire de 2026 — DUO nomme précisément ce silence comme une fausse
déclaration de validité permanente.

### GARDE-IRRÉVERSIBILITÉ (source : DUO — axiome D4)

Jamais d'écrasement en place d'un FAIT existant. Une nouvelle donnée pour le
même `code` + `champ` s'ajoute comme un nouveau FAIT avec sa propre
`date_captee` ; l'ancien reste présent dans la liste. La GARDE de résolution
de conflit (voir GARDE-AUTOJUGEMENT) choisit lequel exposer en priorité —
mais aucun FAIT n'est supprimé ou modifié rétroactivement. Le design en liste
de FAITS le permettait déjà ; cette GARDE le rend obligatoire, pas seulement
possible.

## Ce qui a été examiné et écarté

| Écarté | Raison |
|---|---|
| Cascade N0/N1/N2 (PCCD/RKA/SYNAPSE) | Conçue pour la navigation IA sur un corpus hétérogène en croissance continue. Sur 420 fiches statiques, `completude` + GARDES suffisent — pas de hiérarchie de lecture à construire. |
| 8 statuts épistémiques RKA (PENDING…VOID) | `confiance` + `completude` couvrent le besoin réel. Le vocabulaire à 8 états sert à tracer des désaccords théoriques entre agents sur des hypothèses, pas des écarts entre ISQ et un scraping. |
| SYNAPSE (couches, exocortex, TIE) | Résout l'agrégation inter-projets multi-agents. Site C a une seule source de vérité — pas de couche d'agrégation supplémentaire à construire par-dessus le format atomique lui-même. |
| DUO — distinction connaissance/croyance/décision | Pertinente pour de la connaissance organisationnelle contestée entre acteurs. Une fiche métier est une donnée factuelle sourcée, pas une croyance d'acteur — la distinction n'apporte rien ici. |

## Prochaine étape suggérée

Écrire les GARDES comme tests automatisés (`scripts/gardes.py` ou
équivalent) vérifiés sur `corpus_raw_v2` en premier, avant d'ajouter
d'autres sources — pour prouver que le format tient sur les données
existantes avant de l'étendre.
