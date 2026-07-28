# KB024 — Le bug KB002 persiste : verdict consolidé (deux audits indépendants)

**Statut : CORROBORÉ.**
**Genealogy** : test direct de la question posée par KB002 (dette technique, 2026),
sur le pipeline `scraper/scrape_v2.py` → `data/professions_details.json` →
`scraper/generate.py`. Deux audits indépendants et aveugles, produits sans
concertation, convergents sur 9 sections/10 au chiffre exact.

**Preuves** :
- `docs/audit-fidelite-template-2026.md` (Claude Code Web — 2e opinion)
- `docs/audit-big-pickle-fidelite-2026.md` (Big Pickle — audit indépendant,
  produit sans lecture préalable du document CCW)
- `docs/audit-claude-code-web-structure-site.md` (CCW — audit structurel
  complémentaire, lecture aveugle du site live)
- Données brutes : `data/reference/migration-sens-structure/fidelite-template.json`,
  `fidelite-template-big-pickle.json`, `audit-2e-opinion.json`

---

## Question testée

KB002 (2026, `docs/kb002.md`) documentait un mapping de clés fragile entre
le scraper et le générateur du site, mesurant une couverture par section
allant de 92% (Tâches) à 0,2% (Placement) sur 420 fiches. Cette étude
posait une question ouverte, jamais tranchée depuis : **ce bug a-t-il été
corrigé ?**

## Méthode

Deux instances distinctes (Claude Code Web, Big Pickle/Claude Code CLI) ont
reçu le même brief révisé : reproduire l'algorithme de mapping **exactement
tel qu'il est exécuté aujourd'hui** dans `scraper/generate.py`, sur les
mêmes 420 fiches et les mêmes 10 sections que KB002, avec la même formule
de comptage (contenu non vide après mapping, pas simple présence de clé).
Big Pickle a travaillé sans consulter le résultat de CCW avant d'avoir figé
le sien — condition explicite du brief, vérifiée dans son document (§0,
« sans consultation préalable »).

## Verdict

**Le bug documenté par KB002 n'a pas été corrigé.** La couverture mesurée
aujourd'hui, sur 9 sections sur 10, reproduit les chiffres KB002 à ±2
points près — c'est-à-dire de la stagnation, pas une amélioration. Une
seule section montre une dégradation réelle au-delà du bruit de mesure
(Admission, −5,2 points).

Les deux audits, produits indépendamment, sont arrivés au **chiffre exact**
sur 9 sections/10 :

| Section | KB002 (baseline) | Aujourd'hui | Delta |
|---|---|---|---|
| Description | 31% | 31,0–33,1%* | ~0 à +2,1 |
| Tâches | 92% | 93,6% | +1,6 |
| Milieu | 60% | 60,2% | +0,2 |
| Qualités | 1% | 2,6% | +1,6 |
| Marché | 9% | 9,8% | +0,8 |
| Formation | 6% | 5,7% | −0,3 |
| Admission | 45% | 39,8% | **−5,2** |
| Salaires | 4% | 5,0% | +1,0 |
| Placement | 0,2% | 1,9% | +1,7 |
| Perspectives | 39% | 38,3% | −0,7 |

*Description est la seule vraie divergence entre les deux audits (33,1%
Big Pickle vs 31,0% CCW) — cause identifiée : Big Pickle inclut un filet de
secours regex actif dans le code (`gen_profession()`, lignes 253-282) que
CCW n'a apparemment pas reproduit. Divergence méthodologique tracée, pas un
désaccord sur les faits.

### Le mécanisme causal a changé de place, pas disparu

KB002 diagnostiquait un problème de mapping en aval : le générateur ne
reconnaissait pas les clés produites par le scraper. **Ce mapping a depuis
été implémenté** — `section_key_map` dans `generate.py` est quasi identique
mot pour mot à la solution que KB002 proposait elle-même. Mais la
couverture finale n'a pas bougé, pour trois raisons convergentes,
confirmées par les deux audits :

1. **Un mapping alternatif mort coexiste dans le même fichier.**
   `SECTION_MAP` / `normalize_section()` (lignes 61-83) construit un
   attribut (`p["sn"]`) jamais relu ailleurs — code qui tourne, consomme du
   CPU, et ne sert à rien dans le chemin de génération réel. Quiconque lit
   le fichier en diagonale peut croire le mapping plus complet qu'il ne
   l'est.

2. **Des variantes orthographiques manquent encore du dictionnaire actif.**
   Ex. `EXIGENCE DU MARCHÉ DU TRAVAIL` (singulier) n'est listée nulle part
   dans `source_keys["marche"]`, seule la variante plurielle l'est — 19
   fiches perdent leur section Marché pour cette seule raison.

3. **Les collisions de clés au sein d'une même fiche perdent le contenu le
   plus riche dans une majorité de cas.** 53 collisions détectées (mêmes
   comptages dans les deux audits sur Milieu/Admission/Salaires) ; sur les
   collisions vérifiées en détail, l'algorithme « premier match gagne »
   choisit arbitrairement la clé la plus courte, pas la plus complète. Cas
   extrême confirmé par lecture directe des données brutes : la fiche
   `Chorégraphe` (slug `danseurl`) garde 86 caractères de renvoi vide et
   perd 40 756 caractères de données salariales réelles.

4. **La cause structurelle en amont reste non résolue** (audit
   complémentaire CCW, `docs/audit-claude-code-web-structure-site.md`) :
   `scrape_v2.py` utilise une liste fermée de 15 regex de titres de
   section — toute section réelle du site dont le titre ne matche aucune
   de ces 15 regex est fusionnée silencieusement dans la section
   précédente, avant même d'atteindre `professions_details.json`. Sur
   `ambulancier.htm`, ~20 sections réelles sont ainsi réduites à 7 clés
   dans le corpus. **Aucun mapping en aval ne peut récupérer une section
   jamais capturée en amont.**

### Deux mécanismes non documentés par KB002, découverts en cours d'audit

- **Deux sections à fort volume, jamais suivies** : `LIENS RECOMMANDÉS`
  (91% des fiches, 383) et `VOIR AUSSI` (74%, 309) sont présentes dans les
  données mais absentes de `section_order` — non par bug de mapping, mais
  parce qu'aucune section cible ne leur correspond dans le schéma de sortie
  actuel. Mieux couvertes dans les données brutes que 8 des 10 sections
  officiellement suivies, et pourtant invisibles sur le site généré.
- **Pertes structurelles en amont du scraper** (audit CCW) : ~30% de liens
  perdus sur certaines pages du site source à cause d'un regex qui n'accepte
  pas de balises imbriquées dans le texte de lien ; un secteur complet
  (« Études multidisciplinaires ») absent du corpus car son URL ne suit pas
  le patron attendu ; des pages regroupant plusieurs appellations de métier
  réduites à une seule entrée.

## Discipline de vérification appliquée

- Big Pickle a travaillé sans lire le document CCW avant d'avoir figé le
  sien (condition vérifiée dans son propre document, §0 et §7).
- Chaque chiffre cité ici a été revérifié par lecture directe des données
  brutes (`data/professions_details.json`), pas seulement recopié des
  résumés d'agents — notamment le cas `Chorégraphe` (86 vs 40 756
  caractères, confirmé exact) et le compte de 30 secteurs sur 31 dans le
  corpus (confirmé exact, le seul manquant étant « Études
  multidisciplinaires »).
- Une incohérence arithmétique interne au document CCW (« 54 fiches » en
  texte vs 36+16+1=53 dans son propre tableau) a été repérée par Big
  Pickle et vérifiée indépendamment — erreur mineure de rédaction, sans
  incidence sur le verdict global, mais signalée pour traçabilité plutôt
  que corrigée silencieusement.
- Une coquille reste à corriger dans `audit-claude-code-web-structure-site.md`
  (« 420 fichiers » pour `corpus_raw_v2`, alors que le compte réel est 418
  — 420 est le compte de `professions_details.json`, un fichier distinct).

## Limites

- Les deux audits testent le mapping *en aval* (`generate.py`) avec la même
  méthode ; seul CCW a testé la capture *en amont* (`scrape_v2.py`), sur un
  échantillon de 4 pages — pas une reproduction exhaustive du bug scraper
  sur l'ensemble des 418 pages du corpus.
- L'échantillon structurel (CCW, §2) reste petit (4 pages lues
  intégralement) ; les 4 écarts structurels (S1-S4) sont chacun confirmés
  par preuve directe, mais leur fréquence exacte sur l'ensemble du site
  n'est pas mesurée en population complète.
- La question de savoir si le contenu texte lui-même (au sein d'une section
  correctement mappée) est fidèle au site source n'a pas été auditée
  (signalé hors périmètre par CCW, §5.4).

---

## Ce que ça signifie pour la suite

### Pour la migration du site

Le constat central — **le mapping en aval a été corrigé sur le papier mais
la couverture réelle n'a pas bougé** — déplace la priorité de correction.
Retravailler `section_key_map` dans `generate.py` (ajouter des variantes,
fusionner avec `SECTION_MAP`) ne produira quasiment aucun gain mesurable
tant que le scraper en amont continue de fusionner silencieusement les
sections non reconnues. **La priorité de correction doit remonter d'un
cran : `scrape_v2.py`, pas `generate.py`.** Concrètement, avant toute
nouvelle passe de mapping :

1. Remplacer la liste fermée de 15 regex de `parse_sections` par une
   détection plus générique du motif structurel réel (`<b><u>TITRE</u></b>`,
   documenté par CCW §2.1) — sans präsupposer la liste des titres possibles.
2. Corriger le regex de découverte de liens pour accepter les
   balises imbriquées (`<span>` dans `<a>`), source confirmée de ~30% de
   liens perdus sur au moins une page.
3. Traiter les pages multi-appellations (`occupations.html`) comme des
   entrées multiples, pas une seule.
4. Décider explicitement du sort de `LIENS RECOMMANDÉS` et `VOIR AUSSI` —
   soit les ajouter à `section_order` (elles sont mieux couvertes que la
   moitié des sections déjà suivies), soit documenter que leur exclusion
   est un choix de scope, pas un oubli.
5. Supprimer le mécanisme mort (`SECTION_MAP`/`normalize_section()`) ou le
   fusionner avec le mapping actif — le code mort a activement induit en
   erreur la lecture du fichier pendant cet audit lui-même.

### Pour la recherche System C

Ce résultat a une valeur qui dépasse la correction de bug elle-même. Il
démontre, à l'intérieur du projet, la même leçon que kb021/H4b cherche à
établir à plus grande échelle : **un schéma de classification imposé avant
lecture complète des données trahit structurellement ce qu'il prétend
représenter** — pas en théorie, mesuré deux fois indépendamment, à un
chiffre près. Le mécanisme est local ici (une liste fermée de 15 regex, un
dictionnaire de clés incomplet) plutôt que conceptuel (CNP, O*NET), mais la
structure du problème est identique : *une taxonomie a priori qui ne peut
pas absorber ce qui n'était pas prévu au moment où elle a été figée.*

Ça renforce aussi, méthodologiquement, la valeur de la vérification
indépendante et aveugle comme discipline reproductible dans ce projet — pas
seulement comme garde-fou abstrait. La convergence à 9/10 sections
identiques au chiffre exact, obtenue sans concertation entre deux agents,
est le résultat le plus robuste produit à ce jour sur cette branche, et un
patron réutilisable pour valider de futures hypothèses (H4b notamment,
où un seul test — le clustering TF-IDF — n'a justement pas suffi à
trancher).

---

*Prêt à committer sur `experimental/kb0XX-migration-sens-structure`. Ne pas
fusionner vers `phase2-systemc` sans revue explicite d'Andrei — ce
document constitue le verdict de la branche, pas une autorisation de merge.*
