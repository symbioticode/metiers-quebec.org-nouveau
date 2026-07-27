# kb021 — Test complémentaire bottom-up : deuxième vague de métiers émergents (2026)

**Statut : test empirique complémentaire, non committé comme conclusion de kb021.md.**

## Contexte et méthode

Ce test complète le test top-down O*NET/CNP (`kb021-genome-stability-onet-test.md`,
section "Test complémentaire — la CNP montre-t-elle le même patron que O*NET ?"). Ce
dernier compare des *comptes* au sommet de hiérarchies. Celui-ci reprend la méthode
bottom-up de kb020 : une deuxième vague de métiers émergents, postérieure au corpus de
kb020 (2024-2025), est décomposée en fonctions atomiques et confrontée à la CNP 2021 —
pour voir si le taux de fonctions réellement nouvelles évolue entre les deux vagues.

**GARDE — ce que ce test ne peut pas établir** : une seule deuxième vague, décalée d'
environ un an par rapport à kb020, sur un échantillon de taille comparable (11 métiers).
Ceci ne constitue PAS une série temporelle (il en faudrait au moins 3-4 vagues pour
observer une tendance) — seulement un deuxième point de comparaison, comme le test
CNP2016→CNP2021 en est un pour le volet top-down.

### Sources du corpus (deux sources indépendantes, disciplines de diversification identiques à kb020)

1. **France Compétences, liste 2026** (officielle, même institution que la source
   principale de kb020, mise à jour ultérieure) — 5 métiers *nouvellement ajoutés* à la
   liste 2026 (donc absents de la vague kb020) : Responsable en approvisionnement et
   performance énergétiques, Préparateur technique d'actes d'expertise automobile, Expert
   en renseignement et investigation sur les cybermenaces, Expert en décarbonation et
   performance environnementale, Coordinateur écoproduction audiovisuelle et cinéma.
   (Note : 2 métiers de kb020 — Coordinateur d'intimité, Spécialiste en jumeau numérique —
   restent sur la liste 2026 sans changement ; ils ne sont pas repris ici puisqu'ils ne
   constituent pas une nouvelle observation.)
2. **Onwardsearch, "The AI Talent Race: Top AI Jobs to Watch in 2026"** (janvier 2026,
   secteur IA/tech, indépendant de France Compétences) — 6 métiers retenus parmi les 16
   listés, en excluant ceux déjà couverts par kb019/kb020 (Prompt Engineer, AI Trainer, AI
   Ethicist, Coordinateur humain-machine) : AI Agent Architect, AI Security & Red Teaming
   Specialist, GEO/AEO Specialist, AI Enablement & Literacy Lead, Chief AI Officer (CAIO),
   AI Data Governance Manager.

Corpus final : 11 métiers, mélangeant à nouveau secteur IA/tech (6) et secteurs non-tech
(énergie, automobile, cybersécurité institutionnelle, environnement, audiovisuel — 5),
selon la même discipline de diversification que kb020.

### Méthode par métier (identique à kb020)

1. Désambiguïsation si le titre est polysémique.
2. Décomposition en fonctions atomiques candidates (verbes d'action).
3. Vérification contre `cnp2021-appellations-index.json` (29 767 entrées).
4. Verdict (i) recombinaison pure / (ii) recombinaison + fonction limite / (iii) fonction
   réellement sans précédent.

## Tableau

| # | Métier (source) | Désambiguïsation | Fonctions atomiques candidates | Statut CNP par fonction | Verdict | CNP touché(s) |
|---|---|---|---|---|---|---|
| 1 | Responsable en approvisionnement et performance énergétiques (France Compétences 2026, énergie) | Non ambigu | piloter une stratégie d'approvisionnement en énergie ; auditer la performance énergétique d'une installation ; négocier un contrat d'approvisionnement énergétique | "chef de la section de l'approvisionnement" (10012) couvre le volet achat/appro générique ; rien ne combine explicitement approvisionnement + performance énergétique (0 hit) | **(ii)** — recombinaison achat (10012) + expertise énergétique, la combinaison spécifique non nommée | 10012 (proche) |
| 2 | Préparateur technique d'actes d'expertise automobile (France Compétences 2026, automobile) | Non ambigu (pré-expertise/chiffrage technique de dommages avant intervention d'un expert en assurance) | réaliser une inspection technique préliminaire d'un véhicule endommagé ; documenter un rapport de préparation pour expert ; chiffrer une estimation de réparation | "estimateur/estimatrice de dommages à la carrosserie automobile" (72411), "estimateur/estimatrice d'assurance-automobile" (12201) couvrent directement des fonctions quasi identiques | **(i)** — recombinaison quasi directe, la CNP a déjà des appellations très proches | 72411, 12201 |
| 3 | Expert en renseignement et investigation sur les cybermenaces (France Compétences 2026, cybersécurité) | Ambigu : pourrait désigner (a) un analyste de threat intelligence en entreprise ou (b) un enquêteur habilité (contexte judiciaire/étatique) — non tranché faute de précision dans la source | surveiller des sources de renseignement sur les menaces informatiques ; investiguer un incident de cybersécurité ; produire un rapport de renseignement sur une menace émergente | "analyste en cybersécurité" (21220), "analyste en sécurité informatique" (21220) couvrent l'analyse générale ; 0 hit "cybermenace"/"renseignement" combinés — la dimension investigation/threat-intel spécifique non nommée | **(ii)** — recombinaison analyse sécurité (21220) + fonction investigation/renseignement non nommée telle quelle | 21220 |
| 4 | Expert en décarbonation et performance environnementale (France Compétences 2026, environnement/industrie) | Non ambigu | mesurer une empreinte carbone d'un site industriel ; élaborer un plan de décarbonation ; conseiller une organisation sur une trajectoire de réduction d'émissions | "chef du développement durable" (00012/00013), "directeur/directrice des sciences de l'environnement" (20011), "chimiste spécialiste en environnement" (21101) couvrent le conseil environnemental général | **(ii)** — fonctions de conseil durabilité déjà nommées, "décarbonation" (mesure + trajectoire GES) comme fonction spécifique non nommée | 00012, 20011, 21101 |
| 5 | Coordinateur écoproduction audiovisuelle et cinéma (France Compétences 2026, audiovisuel) | Non ambigu (coordination des pratiques éco-responsables sur un tournage : déchets, énergie, transport de plateau) | auditer l'empreinte environnementale d'un tournage ; mettre en œuvre des pratiques de réduction de déchets sur un plateau ; coordonner des fournisseurs pour des choix éco-responsables de production | Le secteur (cinéma, `52119` "Autre personnel technique et personnel de coordination du cinéma", déjà identifié pour Coordinateur d'intimité en kb020) existe ; 0 hit "écoproduction" ; aucune fonction combinant coordination de plateau + durabilité environnementale trouvée | **(ii)-(iii)**, frontière — même patron que "Coordinateur d'intimité" en kb020 : le secteur existe, la fonction précise (audit+mise en œuvre environnementale sur un plateau) n'a aucun équivalent, même approximatif | 52119 (secteur seulement) |
| 6 | AI Agent Architect (Onwardsearch 2026, IA/tech) | Non ambigu dans la source (orchestration de la collaboration entre agents IA autonomes) | concevoir une architecture d'orchestration multi-agents ; définir des garde-fous de performance pour un système autonome ; superviser la collaboration entre plusieurs agents IA | 0 hit combiné "agent"+"orchestr" ; proche de "scientifique de données" (21211) et de fonctions d'ingénierie logicielle (21230/21311) sans les recouvrir | **(ii)-(iii)**, frontière haute — le geste central (orchestrer la collaboration entre agents autonomes) est distinct des fonctions d'ingénierie logicielle classiques, sans équivalent trouvé même approximatif | 21211, 21230 (proches) |
| 7 | AI Security & Red Teaming Specialist (Onwardsearch 2026, IA/tech) | Non ambigu (simulation d'attaques adversariales contre des systèmes IA) | simuler une attaque adversariale contre un modèle ; documenter une vulnérabilité découverte ; recommander un correctif de sécurité pour un système IA | "analyste en sécurité informatique" (21220), "ingénieur/ingénieure en sécurité informatique" (21220), "consultant/consultante en sécurité informatique" (21220) couvrent le test d'intrusion/sécurité en général | **(ii)** — recombinaison de la fonction de test de sécurité déjà bien couverte (21220), appliquée à un nouvel objet (modèle IA plutôt qu'infrastructure réseau) — changement d'objet, pas de fonction nouvelle | 21220 |
| 8 | GEO/AEO Specialist — Generative/Answer Engine Optimization (Onwardsearch 2026, IA/tech) | Non ambigu (optimiser un contenu pour être cité par des moteurs de réponse génératifs, évolution du SEO classique) | analyser comment un contenu est cité par un moteur de génération de réponse ; adapter la structure d'un contenu pour maximiser sa citabilité par une IA ; mesurer la visibilité d'une marque dans des réponses générées | "chargé/chargée de projet en marketing numérique", "expert-conseil/experte-conseil en marketing numérique" (11202) couvrent le marketing numérique général, y compris probablement le référencement classique ; rien de spécifique "GEO"/citabilité IA trouvé | **(ii)** — évolution directe du référencement (11202), objet nouveau (moteurs génératifs) mais geste de travail inchangé | 11202 |
| 9 | AI Enablement & Literacy Lead (Onwardsearch 2026, IA/tech) | Recoupe directement la lecture (d) de kb019 ("coacher des humains sur l'usage de l'IA") — même fonction, nouveau nom, un an plus tard | former des équipes à l'adoption d'un outil IA ; accompagner un changement organisationnel lié à l'IA ; concevoir un programme de littératie IA | Mêmes constats que kb019(d) : "conseiller/conseillère en formation" (11200) proche ; "accompagner un changement organisationnel" reste faiblement couvert / possiblement inédit (déjà signalé en kb019) | **(ii)**, cohérent avec kb019(d) — pas de nouvelle fonction, confirmation que la même fonction atomique persiste sous un intitulé différent un an plus tard | 11200 |
| 10 | Chief AI Officer / CAIO (Onwardsearch 2026, IA/tech) | Non ambigu (cadre dirigeant responsable de la stratégie IA d'une organisation) | définir une stratégie d'adoption de l'IA à l'échelle de l'organisation ; arbitrer des priorités d'investissement technologique ; superviser la gouvernance éthique d'une organisation en matière d'IA | Cadres supérieurs génériques bien couverts (00011/00012/00013 — chefs de la direction, directions TI, etc.) ; aucune appellation combinant explicitement direction générale + intelligence artificielle (0 hit "directeur"+"intelligence artificielle") | **(i)-(ii)**, frontière basse — recombinaison très directe de fonctions de cadre supérieur déjà nommées (00011-00013), seul l'objet (IA) est nouveau, pas le geste de travail dirigeant lui-même | 00011, 00012, 00013 (proches) |
| 11 | AI Data Governance Manager (Onwardsearch 2026, IA/tech) | Non ambigu | auditer la qualité d'un jeu de données destiné à l'entraînement d'un modèle ; définir une politique de gouvernance des données ; assurer la conformité réglementaire d'un pipeline de données | "agent/agente de la conformité réglementaire" (11201), "scientifique de données"/"scientifique principal(e) de données" (21211) couvrent séparément conformité et données ; rien combinant explicitement "gouvernance des données" (0 hit) | **(ii)** — recombinaison de fonctions déjà connues (conformité 11201, données 21211), combinaison spécifique non nommée | 11201, 21211 |

## Résultats agrégés

- (i) pur : **1/11** (Préparateur technique d'actes d'expertise automobile)
- (i)-(ii) frontière basse : **1/11** (Chief AI Officer)
- (ii) recombinaison + fonction limite : **7/11** (Responsable approvisionnement énergie,
  Expert renseignement cybermenaces, Expert décarbonation, AI Security & Red Teaming, GEO/AEO
  Specialist, AI Enablement & Literacy Lead, AI Data Governance Manager)
- (ii)-(iii) frontière haute (aucun (iii) net) : **2/11** (Coordinateur écoproduction
  audiovisuelle, AI Agent Architect)

Aucun cas n'est classé (iii) net dans cette vague — contrairement à kb020 qui avait un cas
net ("Coordinateur d'intimité") — mais 2 cas sur 11 atteignent la même frontière
(ii)-(iii) qu'un cas de kb020 ("Technicien valoriste du réemploi").

## Comparaison avec la vague kb020 (2024-2025)

| | kb020 (2024-2025, n=13) | Ce test (2026, n=11) |
|---|---|---|
| (i) pur | 2/13 (15%) | 1/11 (9%) |
| (ii) | 9/13 (69%) | 7/11 (64%) — 8/11 (73%) si on inclut la frontière (i)-(ii) |
| (iii) net | 1/13 (8%) | 0/11 (0%) |
| Frontière (ii)-(iii) | 1/13 (8%) | 2/11 (18%) |
| "Inédit ou frontière" (iii net + (ii)-(iii)) | 2/13 (~15%) | 2/11 (~18%) |

**Lecture** : la proportion de fonctions "inédites ou à la frontière de l'inédit" est du
même ordre de grandeur entre les deux vagues (~15% vs ~18%) — ni effondrement ni explosion.
C'est compatible avec l'hypothèse 4 (le taux de fonctions réellement nouvelles ne croît pas
de façon débridée), mais avec un échantillon de cette taille (11 et 13) et un seul
intervalle d'un an entre les deux vagues, cette stabilité de proportion **ne peut pas être
distinguée d'un simple artefact d'échantillonnage** — deux tirages différents d'un même
processus bruité donneraient facilement des proportions dans cette fourchette même sans
aucune propriété de stabilité sous-jacente. Il faudrait au moins 3-4 vagues pour commencer à
distinguer un motif d'un bruit d'échantillonnage.

**Constat qualitatif le plus fort de ce test complémentaire** : l'item #9 (AI Enablement &
Literacy Lead) reproduit très exactement la fonction déjà identifiée dans kb019, lecture
(d), sous un intitulé de métier complètement différent, un an plus tard, dans une source
indépendante. C'est la première observation directe et concrète (plutôt qu'une simple
compatibilité statistique) d'une fonction atomique qui persiste pendant qu'un titre de
métier change — exactement le phénomène que l'hypothèse 4 prédit. Un seul cas ne prouve
rien, mais c'est le type d'observation qu'il faudrait accumuler pour construire un
véritable test longitudinal bottom-up.

## GARDE — limites de ce test complémentaire

- **Deux points, pas une série** : kb020 (vague 1, 2024-2025) et ce document (vague 2,
  2026) sont deux instantanés séparés d'environ un an, pas une série temporelle. Aucune
  tendance ne peut en être tirée — seulement un deuxième point de comparaison, documenté
  comme tel.
- **Tailles d'échantillon modestes** (13 et 11) : les proportions ci-dessus ont des
  intervalles de confiance larges ; une différence de 15% à 18% n'est pas significative à
  ces tailles.
- **Chevauchement partiel des sources** : la source France Compétences 2026 partage 2
  métiers avec kb020 (Coordinateur d'intimité, Spécialiste en jumeau numérique), exclus ici
  car non nouveaux — mais cela signifie que la partie France Compétences de ce corpus est
  contrainte aux 5 seuls métiers *ajoutés* en 2026, un sous-échantillon plus petit que celui
  du secteur IA/tech (6). La diversification sectorielle est donc légèrement déséquilibrée
  en faveur du secteur IA/tech par rapport à kb020.
- **Périmètre CNP inchangé** : comme kb019/kb020, seules les appellations et la hiérarchie
  de titres CNP2021 ont été consultées (pas les "Fonctions principales" détaillées) ; les
  verdicts (ii) pourraient évoluer avec ce niveau de détail.
- **`docs/kb021.md` n'est pas modifié par ce document.** Conformément à la règle de mise à
  jour conditionnelle : le résultat n'est pas net dans un sens ou dans l'autre (proportions
  comparables mais non significatives à ces tailles, sur seulement 2 points de mesure) — il
  est documenté ici comme finding en soi, comme kb020 l'avait fait pour l'hypothèse 3. Ce
  test bottom-up et le test top-down CNP/O*NET (`kb021-genome-stability-onet-test.md`)
  sont désormais tous deux disponibles pour la décision d'Andrei sur une éventuelle mise à
  jour de kb021.md — cette décision n'est pas prise ici.
