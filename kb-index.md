# kb-index.md — registre canonique, source unique de vérité pour la numérotation

Toute instance qui crée un nouveau document `kbNNN` DOIT :
1. Lire ce fichier en premier.
2. Vérifier le numéro proposé contre la colonne "Numéro" ci-dessous, PAS
   contre un souvenir de conversation ni une supposition sur ce qui est
   "probablement libre".
3. Ajouter sa ligne ICI, dans le MÊME commit que la création du fichier.
   Un kb créé sans ligne correspondante ici est considéré non enregistré,
   même s'il existe sur GitHub.

| Numéro | Projet | Chemin | Titre court |
|---|---|---|---|
| kb001–009 | Phase 1 | `docs/kb00X.md` | (corpus, scraping, structure) |
| kb010 | Phase 1 | `docs/kb010-resume-projet.md` | Résumé projet Phase 1 |
| kb011 | Phase 1 | `docs/kb011-perspective-bigpickle.md` | Perspective Big Pickle |
| kb013 | Phase 1 | `docs/kb013-rapport-methodologie.md` | Méthodologie D/L/C |
| kb015–020 | System C | `system-c/docs/kb0XX.md` | (structure, H1-H3) |
| kb021 | System C | `system-c/docs/kb021.md` | H4a/H4b — génome stable |
| kb022 | System C | `system-c/docs/kb022-durcissement-sha-check.md` | Audit adversarial cnp_sha_check |
| kb023 | System C | (project knowledge, pas encore sur GitHub) | `kb023-resume-projet.md` — résumé kb010→H4b |
| kb024 | Phase 1 | `docs/kb024-verdict-consolide-bug-kb002.md` | Verdict bug kb002 |
| kb025 | Phase 1 | `docs/kb025-carte-ignorance-fusion-synonymes.md` | Carte ignorance fusion synonymes |
| kb026 | System C | `system-c/docs/kb026-verdict-consolide-H4a-H4b.md` | Verdict consolidé H4a/H4b |
| **kb027** | **libre** | — | **prochain numéro disponible** |

**Règle d'arbitrage** : les deux projets (Phase 1, System C) partagent
CETTE séquence unique, même si leurs fichiers vivent à des chemins
différents (`docs/` vs `system-c/docs/`). Ne jamais attribuer un numéro
en ne regardant qu'un seul des deux arbres de fichiers.
