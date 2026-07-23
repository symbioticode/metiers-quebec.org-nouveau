# TRANSITION.md — reprise Phase 2

## État au moment du transfert
- main (ebee422) : Phase 1 close, voir docs/kb013.md
- archive/system-c-tentative-1 (0393c23) : cliché figé, ne pas modifier
- phase2-systemc (e120106) : 12 fichiers, isolation vérifiée 3x

## Discipline à conserver dans la nouvelle conversation
- Ne jamais accepter un rapport de Big Pickle sur la seule foi du texte —
  toujours redemander la sortie brute des commandes git (log, ls-remote,
  ls-tree) et vérifier soi-même.
- Fetch explicitement toutes les branches avant de conclure quoi que ce
  soit (`git fetch origin '+refs/heads/*:refs/remotes/origin/*'`) — un
  fetch par défaut peut ne suivre que main et cacher un problème réel.
- CHARTE.md est la seule autorité de démarrage pour Phase 2 — pas de
  réimport de vocabulaire externe sans le documenter comme kb008bis
  l'aurait dû faire.

## Prochaine étape non commencée
(à remplir selon ce qu'Andrei veut faire en premier sur phase2-systemc)
