# Audit Claude Code Web — 2e opinion indépendante sur la structure du site live

**Horodatage de la lecture aveugle (étape 1) :** 2026-07-27, ~05:45–06:15 UTC.
**Méthode :** lecture directe du site live `metiers-quebec.org` via `curl`
(HTML brut, pas de rendu navigateur), **avant** toute lecture de
`scraper/scrape_v2.py`, de `data/corpus_raw_v2/`, ou de tout résultat produit
par Big Pickle sur cette branche. Cette section (§1–§3) est écrite et figée
avant que je n'ouvre un seul de ces fichiers — voir §4 pour la déclaration
d'indépendance et le contrôle d'horodatage.

## Avertissement en tête — instant de comparaison non garanti identique

Je n'ai aucun moyen de savoir à quel instant Big Pickle a lu le site live
pour produire son propre résultat, ni si son script a scrapé le site avant
ou après les modifications que j'observe ci-dessous (§3, notamment les
en-têtes HTTP `Last-Modified` en 2026 sur les trois pages échantillonnées).
**Si le site live a été modifié entre le passage de Big Pickle et le mien,
les deux audits ne comparent techniquement pas le même instant du site.**
Je ne peux pas trancher cette question moi-même — je la signale ici pour
qu'Andrei l'ait en tête en lisant les écarts trouvés plus bas : un écart
« Big Pickle seul » ou « Claude Code Web seul » peut refléter soit une
vraie différence de lecture, soit un site qui a changé entre les deux
passages. Aucun résultat de Big Pickle n'était présent sur cette branche
au moment où j'ai créé la branche (`experimental/kb0XX-migration-sens-structure`
n'existait pas avant ce travail) — donc au moment de rédiger ce document,
je n'ai **aucun élément de comparaison temporelle** pour trancher.

## 1. Structure de navigation observée (top-level)

Le site est une **frameset FrontPage** classique de 2009, jamais migrée
hors de ce modèle :

- `index.html` → `<FRAMESET COLS="25%,*">` avec deux frames :
  - `cadre.html` : menu de navigation latéral (liens statiques vers pages
    hors-métiers : orientation, admission, études, etc.)
  - `accueil.html` : contenu principal, avec un menu déroulant JavaScript
    (`CreeTableau`) qui liste **31 secteurs** et pointe chacun vers une page
    `secteur/secteur.htm` (ex. `../batiment/batiment.htm`,
    `../protection/protection.htm`).

Liste exacte des 31 secteurs telle qu'exposée dans le menu déroulant
`accueil.html` (ordre d'apparition, orthographe telle quelle sur le site,
casse d'origine préservée) :

1. Administration, secrétariat et informatique
2. Aérospatial
3. Agriculture, agroalimentaire et pêcheries
4. Armée
5. Arts appliquées et d'expression
6. bâtiment et construction *(minuscule initiale sur le site — anomalie de saisie d'origine)*
7. Bois (meubles) et matériaux connexes
8. Chimie et biologie
9. Communication, documentation et médias
10. Communications graphiques, multimédia et imprimerie
11. Dessin et fabrication mécanique
12. Éducation, enseignement et services de garde
13. Électrotechnique
14. Entretien d'équipements motorisés
15. Études multidisciplinaires
16. Environnement et aménagement du territoire
17. Foresterie et papier
18. Lettres et langues
19. Mécanique d'entretien
20. Métallurgie
21. Mines, pétrole et travaux de génie
22. Mode et production textile
23. Protection publique
24. Restauration, hôtellerie et tourisme
25. Santé
26. Sciences et techniques humaines
27. Sciences naturelles
28. Sciences physiques et mathématiques
29. Services sociaux et juridiques
30. Soins esthétiques et beauté
31. Transport

**Note structurelle :** 31 secteurs exposés dans le menu du site live. Ce
nombre est à comparer explicitement avec le nombre de `secteur`/`secteur_nom`
distincts présents dans le corpus stocké (étape 3) — un écart ici serait un
écart **structurel** au sens de la grille de classification.

## 2. Structure d'une fiche métier (échantillon de 4 pages lues intégralement)

Pages lues en HTML brut (`curl`, sans JS, sans navigateur) :

- `batiment/tailleur_pierres.html` (référence historique du projet, kb010)
- `protection/ambulancier.htm` (présent dans le corpus/search.json actuel)
- `batiment/architecte.htm`
- `batiment/occupations.html` (page groupée, voir §2.4)

### 2.1 Format brut du HTML

Toutes les pages sont un export **Microsoft Word → FrontPage** (`mso-*`
classes CSS, balises `<o:DocumentProperties>`, `<w:WordDocument>`, encodage
`windows-1252`). Il n'y a **aucune balise sémantique** (`<section>`,
`<article>`, `<h2>` structuré par section) — les « sections » sont des
paragraphes `<p class=MsoNormal>` dont le premier `<span>` est mis en
**gras + souligné** (`<b><u>…</u></b>`) et sert de titre visuel. La
structure n'existe donc que par convention typographique, pas par le DOM.
Une extraction fiable doit repérer les motifs `<b><u>TITRE</u></b>` (ou
variantes avec espaces/retours ligne insérés au milieu du titre par Word,
ex. `<b><u>PROFESSIONS<br>APPARENTÉES</u></b>` sur `ambulancier.htm`).

### 2.2 Sections observées — `tailleur_pierres.html` (métier non réglementé)

Ordre d'apparition, titres exacts (accents recomposés) :

1. TÂCHES ET RESPONSABILITÉS
2. APTITUDES ET QUALITÉS REQUISES
3. PROFESSIONS APPARENTÉES
4. EMPLOYEURS POTENTIELS
5. EXIGENCE DE L'EMPLOI
6. PLACEMENT *(texte : « Selon les données disponibles au 1er juin 2018 »)*
7. SALAIRE *(texte : « Selon les données en 2026 »)*
8. PORTRAIT DU MÉTIER *(statistiques 2018, genre/âge/répartition régionale)*
9. PERSPECTIVES D'AVENIR *(voir §3 — section stylistiquement différente)*
10. LE PROGRAMME D'ÉTUDES
11. EXIGENCE D'ADMISSION
12. STATISTIQUES D'ADMISSION
13. ENDROIT DE FORMATION
14. LIENS RECOMMANDÉS

### 2.3 Sections observées — `ambulancier.htm` (métier réglementé, schéma élargi)

1. TÂCHES ET RESPONSABILITÉS
2. QUALITÉS ET APTITUDES
3. PROFESSIONS APPARENTÉES
4. EMPLOYEURS POTENTIELS
5. CARTE DE COMPÉTENCE *(absent chez tailleur_pierres)*
6. AUTRES EXIGENCES DU MARCHÉ DU TRAVAIL *(absent chez tailleur_pierres)*
7. EXIGENCES DES EMPLOYEURS *(absent chez tailleur_pierres)*
8. PLACEMENT
9. SALAIRE
10. PORTRAIT [DU MARCHÉ DU TRAVAIL — titre tronqué dans l'extraction texte brut]
11. PERSPECTIVES D'AVENIR
12. PORTRAIT DES SERVICES PRÉHOSPITALIERS D'URGENCE AU QUÉBEC *(sous-section propre au métier, non générique)*
13. **PORFORMATION PRÉPARATOIRE** — coquille orthographique présente telle
    quelle dans le HTML source (« PORFORMATION » au lieu de
    « FORMATION PRÉPARATOIRE »). Signalé ici comme fait brut, pas corrigé.
14. LE PROGRAMME D'ÉTUDES
15. EXIGENCES D'ADMISSION
16. AUTRES EXIGENCES D'ADMISSION *(absent chez tailleur_pierres)*
17. CRITÈRES DE SÉLECTION *(absent chez tailleur_pierres)*
18. [section de statistiques d'admission par cégep, titre non capturé
    par le motif `<b><u>`, repérée via en-têtes de tableau : NOMBRE DE
    RÉPONDANTS / NOMBRE EN EMPLOI RELIÉ / NOMBRE À TEMPS COMPLET / etc.,
    datée « à l'automne 2025 »]
19. ENDROITS DE FORMATION
20. LIENS RECOMMANDÉS

### 2.4 Constat structurel majeur : le schéma n'est PAS uniforme entre métiers

`tailleur_pierres.html` a 14 sections, `ambulancier.htm` en a au moins 20,
avec des sections propres à la réglementation du métier (CARTE DE
COMPÉTENCE, CRITÈRES DE SÉLECTION, sous-section spécifique « PORTRAIT DES
SERVICES PRÉHOSPITALIERS D'URGENCE »). **Un schéma fixe imposé à toutes les
fiches (un seul jeu de champs pour 420 métiers) trahirait structurellement
les métiers réglementés**, qui portent des sections que les métiers non
réglementés n'ont pas. C'est un signal indépendant qui rejoint directement
le sujet du projet (kb002 : schéma figé avant lecture du corpus = perte de
données) — je le note ici sans avoir lu ni `generate.py` ni `scrape_v2.py`
au moment de l'écrire.

De plus, `batiment/occupations.html` (« métiers non spécialisés en
construction ») est une page qui **regroupe plusieurs appellations de
métiers sous une seule URL** — ce n'est pas une fiche 1-métier-1-page.
Plusieurs liens internes du site (`batiment/batiment.htm`) pointent vers
cette page groupée plutôt que vers des fiches individuelles. Une
extraction qui suppose « 1 page = 1 métier = 1 slug » manquera
structurellement ce cas, ou produira un seul slug pour plusieurs
appellations distinctes.

## 3. Indices de mise à jour récente (sans consultation de version control)

Deux signaux de fraîcheur, de fiabilité très différente, ont été trouvés :

**a) Métadonnées Word/FrontPage intégrées au HTML (`<o:LastSaved>`,
`<o:Created>`) — TROMPEUSES.** Sur les 4 pages échantillonnées, ces
métadonnées datent de 2002–2007 (ex. `tailleur_pierres.html` :
`Created 2002-07-17`, `LastSaved 2007-01-13`). Ce sont des reliques du
document Word d'origine, jamais mises à jour par les éditions
ultérieures — **ne pas s'y fier comme indicateur de fraîcheur**, alors
qu'elles pourraient sembler être la source la plus évidente.

**b) En-tête HTTP `Last-Modified` — FIABLE et récent.**

| Page | `Last-Modified` (HTTP) |
|---|---|
| `batiment/tailleur_pierres.html` | Sun, 24 May 2026 |
| `protection/ambulancier.htm` | Sat, 07 Mar 2026 |
| `batiment/architecte.htm` | Sun, 21 Jun 2026 |

Ces dates sont cohérentes avec les mentions **dans le texte** des pages :
`tailleur_pierres.html` mentionne « Selon les données en 2026 » (section
SALAIRE) et des chiffres de revenu annuel moyen « En 2026 » (section
PERSPECTIVES D'AVENIR) ; `ambulancier.htm` mentionne « à l'automne 2025 »
(section statistiques d'admission par cégep). **Le site est activement
maintenu jusqu'à des dates très récentes par rapport à aujourd'hui
(2026-07-27)** — ce n'est pas un site figé depuis 2009 malgré son moteur
de rendu FrontPage. Toute extraction figée à un instant T doit s'attendre
à ce que le contenu ait de nouveau changé quelques mois plus tard.

**c) Contraste stylistique interne, section PERSPECTIVES D'AVENIR
(`tailleur_pierres.html`).** Le ton de cette section (« La pierre naturelle
est de plus en plus plébiscitée dans l'architecture moderne comme
alternative écologique au béton », « l'utilisation de robots de découpe
automatise le dégrossissage ») diffère nettement, en registre et en
fluidité, du reste de la page (prose FrontPage plus datée/administrative).
Je signale cette observation comme **indéterminée au sens de la grille de
classification** : je ne peux pas trancher si cette section a été
réécrite/enrichie récemment (peut-être avec assistance rédactionnelle) ou
si c'est simplement un effet de style de l'auteur — je ne le tranche pas
arbitrairement, mais le corrèle avec la date `Last-Modified` 2026 récente
de la même page comme indice convergent, sans en faire une preuve.

## 4. Déclaration d'indépendance

Ce document (§1 à §3) a été rédigé avant toute ouverture de :

- `scraper/scrape_v2.py`
- `data/corpus_raw_v2/*.json`
- tout fichier produit par ou attribué à Big Pickle sur cette branche
  (recherche effectuée : aucun fichier de ce type n'existait sur la
  branche `experimental/kb0XX-migration-sens-structure` avant la création
  de celle-ci par ce travail — voir §0 ci-dessus)

La suite du document (§5 et suivants, ci-dessous) documente la comparaison
effectuée **après** cette lecture indépendante, conformément à l'étape 2
du brief.

---

## 5. Comparaison avec le corpus stocké (étape 2)

*(rédigé après §1–§4, une fois la lecture indépendante figée ci-dessus)*

Corpus de référence utilisé : `data/corpus_raw_v2/*.json` (420 fichiers,
un par slug), généré par `scraper/scrape_v2.py`, tel que présent sur cette
branche (issue de `main`). Aucun résultat distinct de Big Pickle n'était
disponible sur la branche au moment de cette comparaison (voir §0) — la
comparaison porte donc uniquement contre le corpus stocké, pas contre un
second résultat d'extraction. Le score de convergence demandé à l'étape 4
du brief est donc **non calculable pour l'instant** ; voir §7.

### 5.1 Ce que `scrape_v2.py` capture réellement

Lecture du script après figeage de §1–§4. Contrairement à ce que
j'anticipais à la lecture du seul nom du fichier (« v2 » suggérant un
correctif du bug historique kb002), `scrape_v2.py` contient **deux
mécanismes de schéma fixé avant lecture des données**, tous deux vérifiés
directement contre les pages lues en §2 :

1. **Découverte de liens vers les fiches métier** (`scrape_sectors`,
   ligne 388) : `re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', html)`.
   Le groupe `[^<]+` exige que le texte du lien ne contienne **aucune
   balise imbriquée**. Or une bonne partie des liens du site (export
   FrontPage/Word) enveloppent le texte du lien dans un `<span>`
   (`<a href="..."><span ...>Texte</span></a>`) — ce motif ne matche
   jamais un tel lien.
2. **Découpage en sections** (`parse_sections`, ligne 202) : une liste
   fermée de 15 regex de titres de section (`TÂCHES ET RESPONSABILITÉS`,
   `DONNÉES SALARIALES`, `STATISTIQUES DE PLACEMENT`, `PERSPECTIVES
   D'EMPLOI`, etc.), utilisée en `re.split`. **Tout titre réel qui ne
   matche aucune de ces 15 regex est silencieusement fusionné dans le
   texte de la section précédente** au lieu de créer sa propre clé.

### 5.2 Écarts structurels — mesurés, pas estimés

| # | Écart | Preuve directe | Classification |
|---|---|---|---|
| S1 | Secteur « Études multidisciplinaires » absent du corpus | Live : 31 secteurs dans `accueil.html` (§1). Corpus : 30 `secteur_nom` distincts comptés sur les 420 fichiers de `data/corpus_raw_v2/` — le seul manquant est « Études multidisciplinaires ». Cause mécanique confirmée en lisant `scrape_v2.py` : son URL (`/autres-pages/multi.html`) ne suit pas le patron `/{slug}/{slug}.htm(l)` attendu par `scrape_sectors` → page marquée « SKIP (pas de page) », jamais visitée. | **structurel, confirmé** |
| S2 | Perte de liens vers des fiches métier à cause du texte de lien imbriqué dans `<span>` | Sur `batiment/batiment.htm` (téléchargé en §2, indépendamment) : 104 balises `<a href>…</a>` au total, dont seulement 73 matchent le regex du scraper (`[^<]+` sans balise imbriquée) → **31 liens perdus (≈30 %)**, incluant précisément `tailleur_pierres.html` — la page qui a déclenché ce projet (kb010). Contre-exemple : `protection/protection.htm` a 45/45 liens matchés (0 perte) — le taux de perte dépend du style d'édition HTML propre à chaque page du site, pas d'un taux uniforme. | **structurel, confirmé, non uniforme selon les pages** |
| S3 | Sections réelles non capturées par la liste fermée de 15 regex | `data/corpus_raw_v2/ambulancier.json` ne contient que 7 clés de section (`intro`, `LIENS RECOMMANDÉS`, `TÂCHES ET RESPONSABILITÉS`, `VOIR AUSSI`, `EXIGENCES DU MARCHÉ DU TRAVAIL`, `MILIEU DE TRAVAIL`, `EXIGENCES D'ADMISSION`) contre **au moins 20 sections réellement présentes** sur `protection/ambulancier.htm` telles que lues indépendamment en §2.3 (QUALITÉS ET APTITUDES, PROFESSIONS APPARENTÉES, EMPLOYEURS POTENTIELS, CARTE DE COMPÉTENCE, PLACEMENT, SALAIRE, PORTRAIT, PERSPECTIVES D'AVENIR, sous-section préhospitalière, LE PROGRAMME D'ÉTUDES, AUTRES EXIGENCES D'ADMISSION, CRITÈRES DE SÉLECTION, ENDROITS DE FORMATION, etc.). Cause : aucune des 15 regex ne matche des titres réels tels que `SALAIRE` (regex attend `DONNÉES SALARIALES`), `PLACEMENT` (regex attend `STATISTIQUES DE PLACEMENT`), `PERSPECTIVES D'AVENIR` (regex attend `PERSPECTIVES D'EMPLOI`), `LE PROGRAMME D'ÉTUDES` (regex attend `PROGRAMMES D'ÉTUDES REQUIS`), et `PROFESSIONS APPARENTÉES` / `CARTE DE COMPÉTENCE` / `CRITÈRES DE SÉLECTION` n'ont **aucune regex correspondante du tout**. | **structurel, confirmé — c'est une reproduction du bug kb002 (schéma figé avant lecture du corpus) à l'intérieur même du script censé le corriger** |
| S4 | Pages regroupant plusieurs appellations de métier sous 1 URL, traitées comme 1 seul métier | `batiment/occupations.html` (titre réel : « métiers non spécialisés en construction », plusieurs appellations distinctes) est scrapé sous le slug `occupationsl`, avec `nom = "Aide briqueteur-maçon"` — une seule appellation retenue pour représenter toute la page groupée. Les autres appellations bundlées sur cette page (confirmées présentes dans le HTML source en lecture indépendante, §2.4) n'apparaissent pas comme entrées distinctes dans le corpus. | **structurel, confirmé** |

Le cas S1+S2 combinés expliquent concrètement pourquoi `tailleur_pierres`
n'a **aucun fichier dans `data/corpus_raw_v2/`** — vérifié par recherche
exhaustive (`grep -r "pierre"` sur les 420 fichiers ne retourne que
`bijoutier.json` / « Tailleur de pierres précieuses », un métier
différent).

### 5.3 Comptage exact des secteurs

Fait (voir §5.2, S1) : 30 `secteur_nom` distincts dans
`data/corpus_raw_v2/*.json` contre 31 dans le menu live. Écart unique :
« Études multidisciplinaires ».

### 5.4 Écarts sémantiques

Non audités en profondeur dans cette passe au-delà de ce qui est déjà
documenté en §5.2/S3 (qui est en réalité un écart structurel — sections
manquantes — plutôt que sémantique — contenu divergent à l'intérieur
d'une section présente des deux côtés). Un audit sémantique fin (ex. :
le texte de la section TÂCHES ET RESPONSABILITÉS, présente des deux
côtés, est-il fidèle mot pour mot ?) nécessiterait un échantillon plus
large que les 4 pages lues ici — signalé comme **hors du périmètre
couvert par cette 2e opinion**, pas tranché arbitrairement.

## 6. Fichier de sortie classifié

Voir `data/reference/migration-sens-structure/audit-2e-opinion.json` pour
la version structurée (JSON) des écarts listés en §5, au même format que
prévu pour la grille de comparaison avec le résultat de Big Pickle.

## 7. Convergence avec Big Pickle — non disponible au moment de la rédaction

Aucun résultat produit par Big Pickle n'était présent sur la branche
`experimental/kb0XX-migration-sens-structure` au moment de ce travail (la
branche n'existait pas avant sa création dans le cadre de cette tâche —
voir §0). **Le score de convergence demandé à l'étape 4 du brief n'a donc
pas pu être calculé.** Les deux listes brutes demandées (écarts trouvés
uniquement par Claude Code Web / écarts trouvés uniquement par Big Pickle
/ recoupement) ne peuvent pas être produites tant que le résultat de Big
Pickle n'est pas accessible sur cette branche. Dès qu'il le sera, cette
section devra être complétée sans lisser les écarts non résolus — ce
document reste donc à l'état DRAFT au sens du brief, avec cette section
explicitement ouverte.
