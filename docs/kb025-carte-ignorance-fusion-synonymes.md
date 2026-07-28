# KB025 — La fusion des synonymes : une sélection, pas une correction. Carte de ce qu'on ne sait pas.

**Statut** : DRAFT — carte d'ignorance délibérée, pas un verdict. Ce
document ne clôt rien ; il nomme ce qui reste ouvert, en continuité
directe avec kb010 (I, entropie-source/pipeline, Site A comme
photographie unique) et kb023 (H4, l'épisode infirmier autorisé/
infirmière auxiliaire).

**Genealogy et correction de méthode** : ce document remplace une première
version qui traitait la duplication de fiches par synonymes comme un
« incident » à corriger, sans avoir relu kb010 et kb023 dans leur
intégralité. Andrei a nommé le problème directement : cette première
version reproduisait, au niveau de l'analyse elle-même, exactement le
motif qu'elle prétendait décrire — une clôture prématurée, appliquée
cette fois à la question épistémique plutôt qu'aux données.

---

## Ce qu'on a fait, sans le nommer comme tel

Face à 2912 fiches issues de 485 URLs, dont 433 portant plusieurs
appellations, la décision prise (avec mon accord, sans le questionner
sur le moment) a été : fusionner en une fiche par URL, avec un champ
`noms: [liste]`. Justification donnée : « aucune perte d'info, le contenu
était déjà identique ».

Cette décision **présuppose une réponse** à une question qu'elle
n'a jamais posée explicitement : que des appellations multiples pointant
vers un contenu identique désignent *le même métier*, et que la bonne
unité de représentation est donc l'URL, pas l'appellation. C'est un choix
de modélisation sémantique, pas une simple opération de dédoublonnage
technique — et je l'ai traité comme la seconde alors que c'était la
première.

## Pourquoi « contenu identique » ne prouve rien de ce qu'on lui a fait dire

Vérification faite directement dans `corpus_raw_v2/ambulancier.json` :
le scraper ne capture **qu'un seul texte par URL**, quel que soit le
nombre d'appellations qui y mènent depuis l'index alphabétique. Le
contenu ne peut pas différer entre `AMBULANCIER`, `Paramédic` et
`Technicien ambulancier`, parce que Site A ne contient physiquement
qu'une seule page à cette adresse. « Contenu identique » n'est donc pas
une observation empirique qui *confirme* que ces appellations sont
synonymes — c'est une conséquence mécanique et inévitable de ce que le
médium source peut représenter, qui aurait été vraie même si les
appellations avaient désigné des réalités professionnelles distinctes.

C'est très exactement la limite que kb010 nomme déjà, à propos de Site A
dans son ensemble : *« Dany Savard n'a jamais pu représenter qu'un seul
état à la fois »* — ici appliqué non pas au temps (une seule photographie
du marché à la fois), mais à la variance synchronique entre appellations
proches (une seule photographie du sens à la fois, même quand plusieurs
noms coexistent). Le médium ne permettait pas à Dany Savard d'écrire un
texte distinct pour "Paramédic" vs "Technicien ambulancier" même s'il
avait voulu le faire — donc son silence sur la distinction ne prouve pas
son absence.

## Le parallèle qu'on n'a pas vérifié avant de fusionner

kb023, Acte 8, documente un cas concret et déjà résolu dans ce même
projet : « infirmier autorisé » (CNP 31301) et « infirmière auxiliaire »
(CNP 32101) sont deux ordres professionnels réglementés **distincts**,
confondus à tort par un outil de correspondance trop permissif. Le
projet a explicitement traité ça comme un risque à surveiller.

`ambulancier` / `Paramédic` / `Recherche et sauvetage, technicien en` /
`Technicien ambulancier` a la même forme de surface — plusieurs libellés
professionnels regroupés sous une seule entrée, sur la seule base qu'ils
partagent une page web. **Personne n'a vérifié**, avant de fusionner, si
« technicien ambulancier » et « paramédic » sont des synonymes purs dans
la réglementation québécoise du travail préhospitalier, ou des catégories
voisines mais distinctes (formations différentes, statuts différents),
de la même façon que l'étaient les deux catégories d'infirmières avant
que ce projet ne le découvre. La fusion appliquée à ce sprint reproduit
peut-être, à l'identique, l'erreur que kb023 a déjà nommée et corrigée
ailleurs dans le même projet — sans qu'on l'ait testée ici.

## Ce que signifierait une lecture "mutation/sélection" plutôt que "bug/correction"

Ta reformulation mérite d'être prise au sérieux plutôt qu'écartée : les
2912 fiches n'étaient peut-être pas une anomalie à corriger, mais une
**prolifération** — le site source, sur dix-sept ans de mises à jour
manuelles, a indexé un même poste sous plusieurs libellés successifs ou
concurrents (probablement des variations d'usage régional, sectoriel, ou
temporel du même métier — hypothèse non vérifiée). Sous cet angle, la
fusion qu'on a appliquée n'est pas une "correction d'un bug de
duplication" — c'est un **acte de sélection** : on a choisi de retenir
une forme (une entité, plusieurs noms) et d'éliminer l'autre lecture
possible (plusieurs entités proches, potentiellement en cours de
divergence ou de convergence sémantique).

Le critère qui a guidé cette sélection, une fois nommé explicitement :
préservation *informationnelle* (aucune chaîne de caractères perdue),
pas préservation *sémantique* (aucune garantie que les distinctions
professionnelles réelles, si elles existent, ne soient pas effacées par
la fusion). Ces deux critères ont été traités comme équivalents sans
justification.

## Le lien avec H4 (kb021/kb023), pas encore exploité

Si un socle de fonctions atomiques stable existe indépendamment des
taxonomies (l'hypothèse H4 de kb021), alors la question de savoir si
`ambulancier`/`Paramédic`/`Technicien ambulancier` sont *une* fonction
atomique ou *plusieurs* fonctions voisines est un test empirique
directement pertinent pour H4 — pas une question secondaire de nettoyage
de données. Mais la fusion, telle qu'on l'a appliquée, a **supprimé la
possibilité même de faire ce test** sur ce cas précis : en collapsant les
5 entrées en 1, on a détruit la trace qui aurait permis de vérifier, plus
tard, si ces appellations recouvrent effectivement le même socle
fonctionnel ou des socles voisins mais distincts. On ne pourra plus tester
ça a posteriori sur cette donnée — seulement en reconstruisant depuis un
nouveau scrape qui garderait la distinction.

## Rattachement à la question ouverte n°1 de kb010 — mesurable maintenant, non mesurée

kb010 posait, sans y répondre : la donnée manquante est-elle de
l'**entropie-source** (Dany Savard n'a pas écrit l'info) ou de
l'**entropie-pipeline** (l'info existe mais le code l'a ratée) ? Ce
sprint offrait une occasion concrète d'instrumenter cette distinction sur
un cas nouveau — la prolifération de synonymes — et ne l'a pas fait.
Reformulée pour ce cas précis, la question devient : la multiplicité des
appellations vers une même URL est-elle **entropie-source** (Dany Savard
indexait volontairement le même poste sous plusieurs entrées, reflétant
un usage réel du terrain), ou **entropie-pipeline** (un artefact de la
façon dont l'index alphabétique du site a été construit, sans rapport
avec une réalité du marché du travail) ? Cette question n'a pas de
réponse actuellement — et, contrairement à ce que la première version de
ce document laissait entendre, ce n'est pas faute de moyen de la tester :
un premier pas serait de vérifier, pour un échantillon des 433 URLs
multi-appellations, si les libellés correspondent à des codes CNP
distincts (test direct et immédiatement disponible via `cnp_check.py` /
`cnp_sha_check.py`, déjà présents dans ce projet).

## Ce que ce document ne fait pas

Il ne recommande pas de défusionner. Il ne prétend pas non plus que la
fusion était une erreur — elle reste défendable comme choix pragmatique
sous contrainte (dépassement de la limite GitHub, décision à prendre dans
l'heure). Ce qu'il fait : **documenter que ce choix n'a pas été soumis au
même niveau d'exigence que le reste du projet** — pas de seuil
pré-enregistré, pas de vérification contre CNP avant de trancher, pas de
test du parallèle avec le cas infirmier autorisé/infirmière auxiliaire
déjà connu dans ce même projet. Le protocole de gouvernance que kb023
décrit (Acte 4 — seuil avant résultat, checklist adversariale avant de
faire confiance à un outil de classification) existe précisément pour ce
genre de décision, et n'a pas été appliqué ici.

## Carte de l'ignorance — ce qui reste à faire, explicitement, pas en filigrane

1. Vérifier, pour l'échantillon des 433 URLs multi-appellations, combien
   correspondent à des codes CNP distincts (test immédiat, outils déjà
   disponibles) — sépare entropie-source réelle (distinction
   professionnelle existante) d'un simple artefact d'indexation.
2. Si une fraction non négligeable correspond à des CNP distincts,
   revenir sur la fusion : au minimum, annoter chaque entrée fusionnée du
   nombre de CNP distincts potentiellement couverts, plutôt que de
   présenter `noms: [liste]` comme une liste de synonymes purs.
3. Documenter explicitement, dans le prochain brief touchant à ces
   données, que « contenu identique entre appellations » ne doit **plus**
   être lu comme une preuve de synonymie — seulement comme la signature
   attendue d'un médium source à un seul état par URL.
4. Si ce test est fait, en faire un point de données pour H4b — pas
   comme confirmation ni réfutation en soi, mais comme un cas de plus
   dans le même registre que « AI Enablement & Literacy Lead » (kb023,
   Acte 7) : une observation directe, ponctuelle, à accumuler plutôt
   qu'à trancher isolément.

---

*Ce document ne se termine pas sur un verdict. Il se termine sur une
question testable, laissée ouverte volontairement, parce que la fermer
maintenant reproduirait l'erreur qu'il documente.*
