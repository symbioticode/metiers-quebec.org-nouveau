# Audit CNP — fusion synonymes (Sprint isolé A, kb025)

**Horodatage :** 2026-07-28.
**Branche :** `experimental/durcissement-cnp-synonymes` (depuis
`experimental/scrape-v2-hardening`).
**Lu avant de commencer, en entier :** `kb025-carte-ignorance-fusion-synonymes.md`,
`durcissement-outils-classification_v0_1.md`, `durcissement-scraper-generateur_v0_1.md`
§1a (fournis directement par Andrei — non trouvés committés sur aucune
branche au moment de démarrer, voir note ci-dessous).

## Note de statut avant les résultats

`docs/durcissement-outils-classification_v0_1.md` n'existe que sur
`phase2-systemc`, pas sur `experimental/scrape-v2-hardening` comme l'indiquait
le brief (confirmé par Andrei directement). `kb025-carte-ignorance-fusion-synonymes.md`
et `durcissement-scraper-generateur_v0_1.md` n'étaient présents sur aucune
branche du dépôt — fournis directement par Andrei en pièce jointe avant de
démarrer ce sprint. Ce travail n'a commencé qu'après lecture intégrale des
trois, conformément au garde-fou du brief.

**Écart de comptage avec kb025** : kb025 cite 433 URLs multi-appellations.
Comptage direct sur `data/professions_details.json` (485 URLs au total,
2912 fiches — ces deux chiffres correspondent exactement à ceux de kb025,
donc c'est bien le même corpus) donne **407** URLs avec `page_groupee: true`
/ `len(noms) > 1`, pas 433. Écart de 26, non expliqué — signalé tel quel, pas
recalculé pour forcer la correspondance à 433.

## Méthode

- **`sha_lookup()` (`cnp_sha_check.py`) = autoritaire.** Hachage SHA-1 exact
  après normalisation, structurellement incapable de faux positif partiel.
  Table vérifiée avant usage : 516 CNP, 2352 entrées, correctif de kb022
  (formes masculines dupliquées dans l'expansion `/`) déjà présent dans
  `cnp-sha-table.json` sur cette branche — pas de régénération nécessaire.
  C'est la seule source utilisée pour classer une URL « cohérent » ou
  « divergent ».
- **`cnp_check()` (`cnp_check.py`) = signal secondaire uniquement**, utilisé
  seulement quand `sha_lookup()` ne trouve rien pour une appellation
  (balayage des 516 CNP). Matching par sous-chaîne — le mécanisme même qui a
  produit la confusion 31301/32101 documentée dans
  `durcissement-outils-classification`. Ses résultats sont rapportés comme
  « candidat approximatif, non garanti », **jamais** utilisés pour classer
  une URL comme cohérente ou divergente — seulement pour enrichir le statut
  « indéterminé ».
- **Balayage exhaustif des 407 URLs**, cas prioritaire (`ambulancier`)
  traité en premier. Aucune modification de `professions_details.json`.

## Cas prioritaire — `ambulancier` (traité en premier, avant tout autre)

```
AMBULANCIER              -> sha: aucun | cnp_check: 32102 « Personnel ambulancier et paramédical » (partielle)
Paramédic                -> sha: aucun | cnp_check: aucun
Recherche et sauvetage,
  technicien en           -> sha: aucun | cnp_check: aucun
TECHNICIEN AMBULANCIER   -> sha: aucun | cnp_check: aucun
Technicien paramédic     -> sha: aucun | cnp_check: aucun
```

**Statut : indéterminé.** Aucune des 5 appellations n'a de correspondance
CNP confirmée par hachage exact. Une seule (« AMBULANCIER ») a un candidat
approximatif faible (32102), non garanti, non contredit par les autres
(qui ne trouvent rien). **Ce test ne confirme ni n'infirme la fusion** — il
ne trouve tout simplement pas assez de signal officiel pour trancher dans
un sens ou l'autre. kb025 posait la question « entropie-source ou
entropie-pipeline ? » pour ce cas précis : ce test ne la résout pas non
plus — il montre seulement que le référentiel CNP officiel n'a pas
d'appellation qui matche exactement (même approximativement, pour 4
appellations sur 5) aucun des termes utilisés par le site source.

## Résultat global — 407 URLs, verdict factuel

| Statut | Nombre | % |
|---|---|---|
| **Cohérent** | 283 | 69.5% |
|   — dont CNP confirmé identique (hash exact) sur toutes les appellations | 1 | 0.2% |
|   — dont aucun CNP trouvé nulle part (ni hash exact, ni candidat approximatif) | 282 | 69.3% |
| **Divergent** | **0** | **0%** |
| **Indéterminé** | 124 | 30.5% |

**Verdict factuel demandé par Andrei : sur les 407 cas de fusion testés,
zéro (0) montre une divergence CNP confirmée par correspondance exacte.**
Aucune fusion `noms: [liste]` n'a été prise en flagrant délit de regrouper
deux codes CNP distincts confirmés. Ceci **ne prouve pas** que toutes les
fusions sont sémantiquement valides — voir la nuance ci-dessous, obligatoire
pour ne pas sur-lire ce chiffre.

### Nuance obligatoire sur le « 283 cohérent » — ne pas sur-lire

Sur les 283 URLs classées « cohérent », **une seule** (`vendeur_autos`, CNP
64100, appellations : « Automobiles, conseiller en vente d'» / « Conseiller
en ventes d'automobiles » / « Représentant en vente automobile » / « Vendeur
d'automobiles ») a un CNP réellement **confirmé par hachage exact identique**
sur toutes ses appellations — c'est la seule fusion de ce corpus
positivement validée par le référentiel officiel.

Les **282 autres** « cohérent » le sont uniquement parce qu'**aucune**
correspondance CNP n'a été trouvée nulle part pour aucune de leurs
appellations — ni exacte, ni même approximative. C'est la règle §3 du brief
appliquée littéralement (« aucun trouvé → cohérent »), mais l'absence de
preuve n'est pas une preuve d'absence de problème : cela signifie que ces
métiers ne sont simplement pas couverts par le référentiel CNP testé (516
professions), pas qu'ils sont validés comme synonymes sûrs. Cette distinction
est conservée explicitement dans `cnp-synonymes.json` (champ
`cnp_confirmes`, liste vide vs non vide) pour ne pas la perdre en aval.

## Indéterminé (124) — décomposition et signal de divergence potentielle

Sur les 124 URLs indéterminées, **31** ont au moins deux candidats CNP
approximatifs distincts parmi leurs appellations (signal de divergence
possible, jamais confirmé par hash exact — à traiter avec prudence, la
méthode de matching par sous-chaîne est précisément celle en cause dans le
cas infirmier/infirmière auxiliaire déjà documenté) :

```
policier, transport1l, administrateur, administration1, armee1, assurances,
tech_droit, chef_trainl, receptionniste_hotel, avocat, occupationsl,
machiniste, medecin, arch_paysagiste, veterinaire, tech_sante_animale,
bibliol, tech_documentationl, assurances1l, musicienl, chauffeur_camion,
chercheur, chimiste, ing_chimiste, danseurl, commercel, vendeur, ebeniste,
tisserandl, electromecano, infirmier
```

**Deux cas méritent une lecture attentive séparée** (liste complète des
candidats dans `cnp-synonymes.json`) :

- **`medecin`** — candidats approximatifs 31102 (omnipraticiens), 31301
  (infirmier — via l'appellation croisée « infirmier/infirmière de cabinet
  de médecins »), 31303 (adjoints au médecin). Appellations réelles de cette
  URL : « médecin » / « MÉDECIN » — deux graphies du même mot, pas deux
  métiers distincts. Le signal multi-CNP vient de la permissivité de
  `cnp_check()` sur un terme générique, pas d'une vraie diversité
  d'appellations fusionnées à tort.
- **`infirmier`** — candidats approximatifs couvrant **31300, 31301, 31302,
  32101, 33102** — dont précisément **31301 (infirmier autorisé) et 32101
  (infirmier auxiliaire)**, la collision déjà documentée par kb023. Mais là
  encore, les deux appellations réelles de cette URL sont « INFIRMIER » /
  « infirmier » — même mot, casse différente, pas une fusion entre
  « infirmier autorisé » et « infirmière auxiliaire ». **Ce n'est donc pas
  une reproduction du cas kb023 sur ce site** (les deux catégories ne sont
  pas fusionnées ensemble ici) — c'est une démonstration supplémentaire que
  le mot seul « infirmier », en recherche libre par sous-chaîne, est
  intrinsèquement ambigu contre le référentiel CNP, ce qui est cohérent
  avec kb023 sans le reproduire au sens strict du brief.

Pour les 29 autres cas de la liste, la diversité de candidats provient de
véritables listes d'appellations multiples et variées (ex. `administrateur`,
13 candidats CNP distincts pour une URL qui regroupe un grand nombre
d'appellations administratives réellement différentes) — ces cas
mériteraient un examen manuel ciblé si une décision de re-fusion/séparation
devait être prise, mais ce rapport ne tranche pas, conformément au
garde-fou.

## Ce que ce rapport ne fait pas

- Ne modifie ni ne re-défusionne `professions_details.json`.
- Ne classe aucun cas indéterminé par défaut dans « cohérent » — les 124 cas
  restent explicitement non tranchés.
- Ne coordonne pas avec le travail de Big Pickle sur
  `experimental/durcissement-checklist-scraper`.
- Ne prétend pas que « 0 divergent confirmé » signifie « fusion validée » —
  voir la nuance ci-dessus sur les 282 cas « cohérent par absence de
  signal ».

## Fichier de données brutes

`data/reference/migration-sens-structure/cnp-synonymes.json` — 407 entrées
complètes (toutes les appellations, tous les hash/candidats trouvés, statut
et justification par URL).
