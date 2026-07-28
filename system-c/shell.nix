{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python311;

  pythonEnv = python.withPackages (ps: with ps; [
    requests
    beautifulsoup4
    pyyaml
    python-dateutil
    pytz
    pytest
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.gcc
    pkgs.pkg-config
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    pkgs.openssl
    pkgs.cacert

    # Scraping headless — Chromium système, pas le binaire Playwright bundlé
    # (incompatible NixOS : liens dynamiques attendus dans /usr, absents ici)
    pkgs.chromium
    pkgs.nodejs_20  # requis par playwright CLI même en usage Python
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.openssl.out}/lib:$LD_LIBRARY_PATH"
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:${pkgs.zlib}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"

    # Playwright : utiliser le Chromium système plutôt que télécharger un binaire
    # (le nix store est read-only, le téléchargement standard de playwright échoue)
    export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
    export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="${pkgs.chromium}/bin/chromium"

    VENV_DIR=".venv"

    if [ -d "$VENV_DIR" ]; then
      VENV_PY=$("$VENV_DIR/bin/python" --version 2>&1 | cut -d' ' -f2)
      NIX_PY=$(python --version 2>&1 | cut -d' ' -f2)
      if [ "$VENV_PY" != "$NIX_PY" ]; then
        echo "⚠  Version Python diverge (venv=$VENV_PY, nix=$NIX_PY) — recréation..."
        rm -rf "$VENV_DIR"
      fi
    fi

    if [ ! -d "$VENV_DIR" ]; then
      echo "📦 Création du venv Python $(python --version)..."
      python -m venv "$VENV_DIR" --system-site-packages
    fi

    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel --quiet
    pip install --quiet playwright pytest

    export PYTHONPATH="$(pwd):$PYTHONPATH"

    PY="$VENV_DIR/bin/python"
    echo ""
    echo "📊 Dépendances système-c :"
    $PY -c "import requests; print('   ✓ requests:', requests.__version__)" 2>/dev/null || echo "   ✗ requests"
    $PY -c "import playwright; print('   ✓ playwright: ok')" 2>/dev/null || echo "   ✗ playwright"
    echo "   ✓ chromium:  ${pkgs.chromium}/bin/chromium"

    echo ""
    echo "✅ Environnement system-c prêt — Python: $($PY --version)"
  '';

  PYTHON_KEYRING_BACKEND = "keyring.backends.null.Keyring";
}
