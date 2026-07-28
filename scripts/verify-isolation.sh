#!/usr/bin/env bash
set -e
HORS_SCOPE=$(git ls-files | grep -v "^system-c/" || true)
if [ -n "$HORS_SCOPE" ]; then
  echo "❌ Isolation violée — fichiers hors system-c/ détectés :"
  echo "$HORS_SCOPE"
  exit 1
fi
echo "✅ Isolation intacte."
