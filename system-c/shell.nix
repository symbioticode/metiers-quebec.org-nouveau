{ pkgs ? import <nixpkgs> {} }:

let
  # Version Python unique — garantit que venv et shell parlent le même Python
  python = pkgs.python311;  # aligner sur le venv existant (3.11)

  pythonEnv = python.withPackages (ps: with ps; [
    numpy
    pandas
    scipy
    matplotlib
    requests
    pyyaml
    python-dateutil
    pytz
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

    # dukascopy-node — Node.js requis (npm global local, nix store read-only)
    pkgs.nodejs_20
    pkgs.nodePackages.npm
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.openssl.out}/lib:$LD_LIBRARY_PATH"
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:${pkgs.zlib}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"

    # ── dukascopy-node : PATH persistant ──────────────────────────────────────
    # Le nix store est read-only → npm install -g doit écrire dans $HOME.
    # Ce bloc est exécuté à chaque entrée dans nix-shell pour que le binaire
    # dukascopy-node soit toujours accessible dans PATH.
    export NPM_GLOBAL="$HOME/.npm-global"
    mkdir -p "$NPM_GLOBAL"
    npm config set prefix "$NPM_GLOBAL" 2>/dev/null || true
    export PATH="$NPM_GLOBAL/bin:$PATH"

    VENV_DIR=".venv"

    # Recréer le venv si la version Python a changé
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

    # yfinance : version sans curl_cffi (requests natif) - aligné avec pyproject.toml
    pip install --quiet "yfinance>=1.3.0,<2.0.0"
    pip install --quiet pytest

    # mif-dqf : installé explicitement — ne pas commenter cette ligne
    pip install --quiet mif-dqf

    export PYTHONPATH="$(pwd):$PYTHONPATH"

    PY="$VENV_DIR/bin/python"
    echo ""
    echo "📊 Dépendances :"
    $PY -c "import numpy;   print('   ✓ numpy:',   numpy.__version__)"   2>/dev/null || echo "   ✗ numpy"
    $PY -c "import pandas;  print('   ✓ pandas:',  pandas.__version__)"  2>/dev/null || echo "   ✗ pandas"
    $PY -c "import yfinance; print('   ✓ yfinance:', yfinance.__version__)" 2>/dev/null || echo "   ✗ yfinance"
    $PY -c "import dqf;     print('   ✓ mif-dqf:', dqf.__version__)"     2>/dev/null || echo "   ✗ mif-dqf"

    # dukascopy-node — IMPORTANT : --help (exit 0), pas --version (exit 1, bug upstream)
    if npx dukascopy-node --help &>/dev/null; then
      DUKA_VER=$(npm list -g dukascopy-node --depth=0 2>/dev/null \
        | grep dukascopy-node | tr -d ' ' | cut -d@ -f2)
      echo "   ✓ node:           $(node --version)"
      echo "   ✓ dukascopy-node: ''${DUKA_VER:-installé}"
    else
      echo "   ✗ node:           $(node --version 2>/dev/null || echo 'absent')"
      echo "   ✗ dukascopy-node  (absent — exécuter : bash setup_dukascopy_nixos_fixed.sh)"
    fi

    echo ""
    echo "✅ Environnement prêt — Python: $($PY --version)"
  '';

  PYTHON_KEYRING_BACKEND = "keyring.backends.null.Keyring";
}
