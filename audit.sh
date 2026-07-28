#!/bin/bash
# audit.sh — Audit automatisé du prototype Métiers Québec
# Lance tous les outils d'audit et génère un rapport dans docs/AUDIT.md

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT=8080
BASE_URL="http://localhost:$PORT"
PAGES=("index.html" "secteur.html" "profession.html" "alpha.html")
REPORT="docs/AUDIT.md"
TMP_DIR=".audit-tmp"

mkdir -p "$TMP_DIR"

echo "============================================"
echo "  AUDIT — Métiers Québec Prototype"
echo "============================================"
echo ""

# ── 1. Vérifier/Installer les outils ──────────────────────────────
echo "[1/6] Vérification des outils..."

install_if_missing() {
  local cmd=$1
  local pkg=$2
  if ! command -v "$cmd" &>/dev/null; then
    echo "  Installation de $pkg..."
    npm install -g "$pkg" --silent 2>/dev/null || true
  fi
  if command -v "$cmd" &>/dev/null; then
    echo "  ✓ $pkg"
  else
    echo "  ✗ $pkg (non disponible)"
  fi
}

install_if_missing "axe" "@axe-core/cli"
install_if_missing "pa11y" "pa11y"
install_if_missing "linkinator" "linkinator"
install_if_missing "lighthouse" "lighthouse"
install_if_missing "vnu" "vnu-jar"
install_if_missing "stylelint" "stylelint"
install_if_missing "htmlhint" "htmlhint"

echo ""

# ── 2. Démarrer le serveur local ──────────────────────────────────
echo "[2/6] Démarrage du serveur local (port $PORT)..."

# Tuer un ancien serveur s'il existe
lsof -ti:$PORT 2>/dev/null | xargs kill -9 2>/dev/null || true

python3 -m http.server $PORT &>/dev/null &
SERVER_PID=$!
sleep 1

if curl -s "$BASE_URL" > /dev/null 2>&1; then
  echo "  ✓ Serveur démarré (PID: $SERVER_PID)"
else
  echo "  ✗ Impossible de démarrer le serveur"
  exit 1
fi

echo ""

# ── 3. Validation HTML (W3C) ──────────────────────────────────────
echo "[3/6] Validation HTML (vnu-jar W3C)..."
VNU_OUTPUT="$TMP_DIR/vnu.txt"
if command -v vnu &>/dev/null; then
  vnu --errors-only "${PAGES[@]}" > "$VNU_OUTPUT" 2>&1 || true
  VNU_ERRORS=$(wc -l < "$VNU_OUTPUT" 2>/dev/null || echo "0")
  echo "  Erreurs HTML: $VNU_ERRORS lignes"
  cat "$VNU_OUTPUT" | head -30
else
  echo "  ⚠ vnu non disponible — ignoré"
  echo "Non disponible" > "$VNU_OUTPUT"
fi
echo ""

# ── 4. Accessibilité (axe-core) ───────────────────────────────────
echo "[4/6] Audit accessibilité (axe-core)..."
AXE_OUTPUT="$TMP_DIR/axe.json"
AXE_TXT="$TMP_DIR/axe.txt"
if command -v axe &>/dev/null; then
  > "$AXE_TXT"
  for page in "${PAGES[@]}"; do
    echo "--- $page ---" >> "$AXE_TXT"
    axe "$BASE_URL/$page" --tags wcag2aa 2>/dev/null >> "$AXE_TXT" || true
    echo "" >> "$AXE_TXT"
  done
  AXE_LINES=$(wc -l < "$AXE_TXT" 2>/dev/null || echo "0")
  echo "  Résultats axe: $AXE_LINES lignes"
  head -40 "$AXE_TXT"
else
  echo "  ⚠ axe non disponible — tentative pa11y..."
  if command -v pa11y &>/dev/null; then
    > "$AXE_TXT"
    for page in "${PAGES[@]}"; do
      echo "--- $page ---" >> "$AXE_TXT"
      pa11y --standard WCAG2AA --reporter json "$BASE_URL/$page" >> "$AXE_TXT" 2>/dev/null || true
      echo "" >> "$AXE_TXT"
    done
    echo "  Résultats pa11y: $(wc -l < "$AXE_TXT") lignes"
  else
    echo "  Aucun outil d'accessibilité disponible"
    echo "Non disponible" > "$AXE_TXT"
  fi
fi
echo ""

# ── 5. Liens cassés (linkinator) ──────────────────────────────────
echo "[5/6] Vérification des liens (linkinator)..."
LINK_OUTPUT="$TMP_DIR/links.txt"
if command -v linkinator &>/dev/null; then
  linkinator "$BASE_URL" --recurse --check-fragments --format CSV > "$LINK_OUTPUT" 2>/dev/null || true
  BROKEN=$(grep -c "BROKEN" "$LINK_OUTPUT" 2>/dev/null || echo "0")
  TOTAL=$(tail -n +2 "$LINK_OUTPUT" | wc -l 2>/dev/null || echo "0")
  echo "  Liens vérifiés: $TOTAL"
  echo "  Liens cassés: $BROKEN"
  grep "BROKEN" "$LINK_OUTPUT" | head -20 || echo "  Aucun lien cassé"
else
  echo "  ⚠ linkinator non disponible — ignoré"
  echo "Non disponible" > "$LINK_OUTPUT"
fi
echo ""

# ── 6. HTMLHint (structure) ───────────────────────────────────────
echo "[6/6] Linting HTML (htmlhint)..."
HTMLHINT_OUTPUT="$TMP_DIR/htmlhint.txt"
if command -v htmlhint &>/dev/null; then
  htmlhint "${PAGES[@]}" > "$HTMLHINT_OUTPUT" 2>&1 || true
  HINT_ERRORS=$(grep -c "Linting" "$HTMLHINT_OUTPUT" 2>/dev/null || echo "0")
  echo "  Résultats htmlhint:"
  cat "$HTMLHINT_OUTPUT" | head -30
else
  echo "  ⚠ htmlhint non disponible — ignoré"
  echo "Non disponible" > "$HTMLHINT_OUTPUT"
fi
echo ""

# ── Génération du rapport ─────────────────────────────────────────
echo "Génération du rapport docs/AUDIT.md..."

cat > "$REPORT" << HEADER
# Rapport d'audit — Prototype Métiers Québec

Généré le $(date '+%Y-%m-%d %H:%M:%S')

---

## 1. Validation HTML (W3C)

\`\`\`
$(cat "$VNU_OUTPUT")
\`\`\`

## 2. Accessibilité (axe-core / WCAG 2.1 AA)

\`\`\`
$(cat "$AXE_TXT" | head -80)
\`\`\`

## 3. Liens cassés (linkinator)

\`\`\`
$(cat "$LINK_OUTPUT" | head -40)
\`\`\`

## 4. Structure HTML (htmlhint)

\`\`\`
$(cat "$HTMLHINT_OUTPUT")
\`\`\`

---

## Résumé

| Catégorie | Outil | Statut |
|-----------|-------|--------|
| Validation HTML | vnu-jar | $(if [ -s "$VNU_OUTPUT" ] && ! grep -q "Non disponible" "$VNU_OUTPUT"; then echo "✅ Fait"; else echo "⚠️ Ignoré"; fi) |
| Accessibilité | axe-core | $(if [ -s "$AXE_TXT" ] && ! grep -q "Non disponible" "$AXE_TXT"; then echo "✅ Fait"; else echo "⚠️ Ignoré"; fi) |
| Liens cassés | linkinator | $(if [ -s "$LINK_OUTPUT" ] && ! grep -q "Non disponible" "$LINK_OUTPUT"; then echo "✅ Fait"; else echo "⚠️ Ignoré"; fi) |
| Linting HTML | htmlhint | $(if [ -s "$HTMLHINT_OUTPUT" ] && ! grep -q "Non disponible" "$HTMLHINT_OUTPUT"; then echo "✅ Fait"; else echo "⚠️ Ignoré"; fi) |

## Recommandations

- Corriger les erreurs HTML signalées par vnu
- Résoudre les problèmes d'accessibilité WCAG 2.1 AA
- Réparer les liens cassés
- Valider la structure HTML avec htmlhint
HEADER

echo ""
echo "============================================"
echo "  AUDIT TERMINÉ"
echo "  Rapport: $REPORT"
echo "============================================"

# Nettoyage
kill $SERVER_PID 2>/dev/null || true
