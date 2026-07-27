# Méthodologie agentique — System C

**Statut : opérationnel.** Ce document remplace l'improvisation prompt-par-
prompt qui a produit une chaîne d'hypothèses ouvertes sans clôture nette
(H3 → H4 → H4a/H4b, plusieurs sprints avant qu'un protocole existe). Toute
nouvelle hypothèse testable dans System C suit ce document dès sa
formulation, pas seulement à la clôture.

---

## 1. Le problème que ce document résout

Sans structure, chaque test génère le suivant en réaction à sa propre
faiblesse plutôt que d'être conçu pour fermer une question précise. Le
symptôme observé : un seuil de succès jamais écrit avant de voir le
résultat, un diagnostic d'échec jamais distingué d'une hypothèse mal
formée, un état de test jamais confirmé par un regard qui n'a pas produit
le résultat.

Ce document compartimente quatre tâches qui ont des profils cognitifs
différents et ne doivent jamais être confiées à la même main (humaine ou
IA) au même moment : **formuler** une hypothèse fermable, **construire**
un test, **critiquer** un résultat, **décider** GO/NO-GO.

## 2. Les principes

**2.1 — La source de vérité est le dépôt Git, jamais une conversation.**
Toute production se termine par un commit vérifiable. Toute session
commence par un `git fetch` réel, pas par la lecture d'un résumé. Une
conversation Claude.ai ou Claude Code peut se dégrader ou se terminer sans
prévenir — le dépôt, non.

**2.2 — Les sprints sont atomiques.**
Un sprint = une question fermée (binaire ou N-aire finie) = un livrable =
un critère de clôture écrit avant le test. Un principe directeur non
fermable (kb010, "le sens survit au conteneur") n'est jamais traité comme
un sprint — voir §5.

**2.3 — Construction et critique sont deux mains différentes.**
Qui produit un résultat ne l'évalue jamais. Concrètement dans l'outillage
disponible :

| Rôle | Outil | Pourquoi |
|---|---|---|
| Construction (produit le résultat) | Claude Code local (CLI/NPM) | Accès filesystem/bash direct pour extraction, calcul, tests. |
| Critique (évalue le résultat) | Claude Code Web, session neuve | Isolement garanti par construction — aucun accès à la conversation ni au contexte de production de la construction. |
| Vérification factuelle en amont (licences, existence de sources, chiffres officiels) | opencode + DeepSeek | Tâche de vérification, pas de raisonnement profond — coût nul, à ne pas gaspiller sur du Claude Opus/Sonnet cher. |
| Exécution parallèle de sous-tâches | Big Pickle | Pas de rôle épistémique — exécution seule. |
| Synthèse GO/NO-GO | Andrei + Claude.ai (cette instance) | Décision humaine assistée, jamais automatisée. |

**2.4 — Les états sont numérotés et à deux mains.**
Voir `plan-cloture-hypotheses.md` pour le détail complet (états Belnap à
quatre valeurs + PRINCIPE, deux champs proposé/confirmé, règle
d'agrégation feuille→parent). Ce document-ci ne le répète pas — il indique
seulement où l'appliquer dans le cycle de sprint.

**2.5 — Le seuil est pré-enregistré, vérifiable par commit.**
Un commit "seuil" (méthode + critère de passage) strictement antérieur au
commit "résultat", lui-même antérieur au commit "verdict". Vérifiable par
`git log`, jamais par simple affirmation dans le texte du rapport.

## 3. Cycle opérationnel d'un sprint

```
ANDREI
  │
  ├─ Formule la question fermée (une phrase, binaire ou N-aire finie)
  ├─ Valide ou corrige le classement Type de document (KB/Hx/Mixte, 
  │  voir plan-cloture-hypotheses.md) si un nouveau KB est créé
  │
  ▼
CLAUDE.AI (cette instance) — cadrage
  ├─ Génère le prompt de construction : question, seuil, méthode, garde-fous
  ├─ Vérifie le corpus/matériau isolé de tout historique de discussion 
  │  avant de le transmettre
  │
  ▼
CONSTRUCTION (Claude Code local)
  ├─ Commit "seuil pré-enregistré — [nom du test]"
  ├─ Exécute, produit les données brutes
  ├─ Commit "résultat — [nom du test]"
  ├─ Rédige état proposé + verdict
  ├─ Commit "verdict — [nom du test]"
  ├─ Push (systématiquement — ne jamais présumer qu'un commit local suffit)
  │
  ▼
CRITIQUE (Claude Code Web, session neuve)
  ├─ git pull, lit UNIQUEMENT les fichiers committés
  ├─ Vérifie : seuil respecté tel qu'écrit, méthode conforme, résultat 
  │  présenté sans dépasser ce qu'il démontre
  ├─ Remplit état confirmé (jamais la même main que l'état proposé)
  │
  ▼
CLAUDE.AI — vérification indépendante avant synthèse
  ├─ git fetch réel (pas de confiance sur le texte du rapport)
  ├─ Relit les fichiers/commits bruts, recompte si nécessaire
  ├─ Exécute scripts/check_kb_states.py sur le KB concerné
  │
  ▼
ANDREI + CLAUDE.AI — synthèse GO/NO-GO
  ├─ Si résultat non tranchant : diagnostic avant reformulation ou 
  │  déclaration de principe (voir §5, jamais après une seule tentative 
  │  sans distinguer test mal calibré / hypothèse mal formée)
  └─ Clôture : état confirmé écrit, risque résiduel nommé, agrégation 
     parent mise à jour si applicable
```

## 4. Scriptable vs non-scriptable

Ne jamais faire vérifier par un script ce qui exige un jugement — et ne
jamais faire vérifier "à la main" ce qu'un script peut faire sans ambiguïté.

**Scriptable (mécanique, aucun jugement)** : présence et énumération des
champs d'état, ordre chronologique des commits seuil/résultat/verdict,
cohérence de l'agrégation parent↔enfants si les états sont en format
structuré, présence de la ligne de risque résiduel. Outil : 
`scripts/check_kb_states.py`.

**Non-scriptable (jugement humain/IA requis)** : la valeur de l'état
elle-même (est-ce que "corroborée" est justifié par les données),
l'isolement réel de la critique (impossible à prouver mécaniquement),
le diagnostic §5 (test mal calibré vs hypothèse mal formée), la qualité
du risque résiduel nommé, la question de départ est-elle vraiment
fermable. Un script qui prétendrait juger ces points réintroduirait
l'autojugement que le protocole exclut, sous une apparence trompeuse
d'objectivité.

## 5. Reformulation vs déclaration de principe

Une hypothèse qui résiste à la fermeture après un test au seuil respecté
ne sort jamais du cycle sur une seule tentative. La critique isolée
diagnostique d'abord :

```
□ Test bien calibré, résultat réellement flou 
    → reformuler en sous-hypothèses plus étroites (comme H4 → H4a/H4b)
□ Seuil ou méthode probablement mal calibrés (corpus trop petit, méthode 
  trop grossière — ex. TF-IDF au lieu d'embeddings sémantiques)
    → un deuxième essai avec seuil ajusté, jamais un abandon
□ Aucun seuil raisonnable ne peut la rendre fermable
    → PRINCIPE — non fermable (proposé), soumis à la même confirmation 
      indépendante que tout autre état avant d'être opposable
```

## 6. Ce que cette méthodologie ne règle pas

Nommé explicitement, pas laissé implicite :

- **Aucune garantie contre un biais de substrat partagé** entre
  construction et critique si les deux tournent sur des modèles de la
  même famille. Atténué par l'usage occasionnel de DeepSeek/opencode pour
  la vérification factuelle, jamais éliminé.
- **Aucune propagation automatique antérograde** : si un KB futur dépend
  d'un KB déjà clos et que ce dernier change d'état, rien ne notifie le
  KB futur — seule la relecture manuelle à chaque nouvelle clôture
  l'attrape, et elle peut rater. Un graphe de dépendances a été
  explicitement écarté (`piste-dependance-hypotheses_v0_1.md`, garde-fou
  §4 non déclenché) — à reconsidérer seulement si un cas concret et nommé
  démontre une conséquence observable de cette lacune.
- **Aucun contrôle indépendant de la qualité du diagnostic (§5)
  lui-même** — il repose sur le jugement de la critique isolée, sans
  troisième regard prévu pour l'auditer à son tour.

Recherche faite — et elle change la réponse : Claude Code a déjà un mécanisme natif de sous-agents (`Task`/`Agent`, `/batch`, git worktrees pour l'isolation fichier) qui couvre exactement le cas "construction parallèle indépendante" que j'avais identifié comme intérêt réel pour Ruflo. Ça réduit le champ légitime de Ruflo à presque rien pour l'échelle actuelle de System C — sauf un cas structurel précis (délégation à plus d'un niveau, que les sous-agents natifs ne permettent pas).

Voici la règle de décision, formulée comme instruction activable/désactivable, à ajouter au document de méthodologie :


## 7. Règle de décision — sous-agents natifs vs Ruflo

**Par défaut : sous-agents natifs de Claude Code (`Task`/`Agent`, `/batch`).**
Ne jamais proposer Ruflo sans avoir d'abord vérifié que les sous-agents natifs
ne suffisent pas. Les deux couvrent le même besoin de base (contexte isolé,
exécution parallèle, rapport au parent) sans dépendance externe ni mémoire
partagée entre sessions.

Aucun FAIT n'entre dans data/atomic/ sans provenir d'un commit d'ingestion tracé et nommé — jamais d'écriture manuelle directe dans le corpus de production, y compris à des fins de test.

### Quand je (Claude.ai, orchestrateur) identifie un sprint candidat

```
□ Le sprint est-il décomposable en sous-tâches VRAIMENT indépendantes 
  (aucune n'a besoin du résultat d'une autre pour démarrer) ?
    NON → pas de parallélisation, ni sous-agent ni Ruflo — sprint séquentiel normal.
    OUI → continuer

□ Le nombre de sous-tâches dépasse-t-il ce qu'un seul niveau de délégation 
  couvre (les sous-agents natifs ne peuvent pas eux-mêmes spawner d'autres 
  sous-agents — pas de délégation imbriquée sans la feature expérimentale 
  Agent Teams) ?
    NON → sous-agents natifs Claude Code. Instruction type : 
          "Utilise des sous-agents pour traiter en parallèle : [liste des 
          sous-tâches indépendantes]" ou /batch pour un périmètre de fichiers.
    OUI, et la structure a réellement besoin de plus d'un niveau 
    (ex. un agent coordinateur qui répartit lui-même le travail entre 
    plusieurs agents spécialisés, sur une tâche assez large pour le justifier) 
        → candidat Ruflo, MAIS voir garde-fou ci-dessous avant d'activer.

□ Le rôle concerné est-il CONSTRUCTION (produit un résultat) ou 
  CRITIQUE (évalue un résultat, §2.3 du protocole) ?
    CRITIQUE → Ruflo exclu, sans exception. Sa mémoire persistante 
               auto-apprenante entre sessions contamine structurellement 
               l'isolement que la critique exige. Rester sur une session 
               Claude Code Web neuve, jamais Ruflo, pour ce rôle.
    CONSTRUCTION → Ruflo reste un candidat possible si le critère de 
                   nesting ci-dessus est rempli.
```

### Garde-fou avant d'activer Ruflo, même pour un rôle CONSTRUCTION admissible

- Désactiver explicitement toute persistance de mémoire inter-sprints avant
  usage (`memory_store`/apprentissage cross-session) — un sprint reste
  atomique par principe (§2.2), un swarm qui "apprend" d'un sprint précédent
  rompt cette atomicité même côté construction.
- Un seul sprint suffit pour évaluer l'outil au premier usage réel — ne pas
  l'adopter par défaut avant d'avoir vu, sur un cas concret nommé, qu'il
  apporte quelque chose que les sous-agents natifs ne faisaient pas.
- Si ce premier usage ne révèle aucun avantage net sur les sous-agents
  natifs, ne pas réessayer Ruflo sur les sprints suivants — noter la
  décision une fois, ne pas la rouvrir sans nouveau cas nommé (même
  discipline que le garde-fou de `piste-dependance-hypotheses_v0_1.md`).
```

**Concrètement, à ce stade du projet** : je n'ai identifié aucun sprint passé (extraction CNP, tests O*NET, clustering) qui aurait dépassé un seul niveau de délégation — tous étaient soit séquentiels par nature, soit parallélisables à plat (plusieurs fichiers/métiers indépendants, un seul niveau). Le cas d'activation réel de Ruflo ne s'est donc pas encore présenté dans ce projet — la règle ci-dessus sert à le repérer s'il apparaît, pas à le déclencher maintenant.

---

*Document vivant. Toute modification à ce protocole suit la même
discipline qu'il impose aux hypothèses : pas de changement silencieux,
un commit, une justification.*

---

## Amendement 1 (2026-07-27) — deux leçons empiriques

**Séparation seuil/résultat, y compris temporellement.** H4a a été
corroborée avec un seuil et un résultat committés dans le même commit —
la séparation en deux commits distincts (déjà pratiquée depuis) ne
suffit pas si les deux sont poussés ensemble sans qu'une vérification
indépendante ait eu le temps de contester le seuil avant de voir le
résultat. Règle ajoutée : le commit de seuil doit être poussé et,
idéalement, laissé visible au moins le temps d'un aller-retour avant que
le commit de résultat ne soit produit — même par la même instance.

**Le balayage exhaustif doit dépasser la question posée.** Le Cas 6 du
durcissement `cnp_sha_check.py` (kb022) visait à tester singulier vs
pluriel sur un exemple ciblé ; le balayage exhaustif de toute la matrice
(516 CNP, pas un échantillon) a révélé un bug de construction sans
rapport direct avec la question testée. Règle ajoutée : tout test
d'audit ou de durcissement doit inclure, en plus du cas ciblé, un
balayage exhaustif du domaine complet quand le domaine est fini et de
taille raisonnable (ici : 516 CNP) — pas seulement le cas qui a motivé
le test.

**Promotion explicite (2026-07-27).** Le Sprint 4/5 de tout chantier
d'hypothèse doit produire, comme livrable vérifiable, un commit qui
modifie le document canonique de l'hypothèse (`kbXXX.md`) lui-même — pas
seulement un fichier satellite de sprint. Un résultat vérifié qui ne
modifie pas le document canonique n'est pas considéré comme clos, quel
que soit son niveau de vérification par ailleurs.
