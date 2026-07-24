#!/usr/bin/env bash
set -e

# Détecte si la racine git EST system-c/ (repo dédié) ou si system-c/
# est un sous-dossier d'un monorepo plus large. L'ancienne version
# supposait toujours le second cas — faux dans un repo dédié, ce qui
# faisait échouer la vérification sur 100% des fichiers systématiquement.

REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_BASENAME=$(basename "$REPO_ROOT")

if [ "$REPO_BASENAME" = "system-c" ]; then
  # La racine du repo EST system-c/ : tous les fichiers trackés sont dans le scope par définition.
  HORS_SCOPE=$(git ls-files | grep -E "(corpus_raw_v2|dist/|graphify)" || true)
else
  # system-c/ est un sous-dossier : tout fichier tracké hors de ce préfixe est une violation.
  HORS_SCOPE=$(git ls-files | grep -v "^system-c/" || true)
fi

if [ -n "$HORS_SCOPE" ]; then
  echo "❌ Isolation violée — fichiers détectés :"
  echo "$HORS_SCOPE"
  exit 1
fi

# Vérification de CONTENU, pas seulement de noms — CHARTE.md interdit
# corpus_raw_v2, dist/, Graphify et tout slug provisoire même à l'intérieur
# d'un fichier par ailleurs bien placé.
CONTENU_SUSPECT=$(git grep -lE "corpus_raw_v2|graphify|code_provisoire" -- '*.py' '*.md' '*.json' 2>/dev/null || true)
if [ -n "$CONTENU_SUSPECT" ]; then
  echo "❌ Isolation violée — références interdites trouvées dans le CONTENU de :"
  echo "$CONTENU_SUSPECT"
  exit 1
fi

echo "✅ Isolation intacte. (racine repo: $REPO_BASENAME)"
