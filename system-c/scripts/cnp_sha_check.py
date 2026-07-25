#!/usr/bin/env python3
"""
Validation CNP par lookup de hachage SHA-1 exact.

Fonction autonome — zéro import ni dépendance vers cnp_check.py.
Conçue pour un test comparatif direct avec cnp_check() :
  - Même corpus de test, deux stratégies indépendantes.
  - Même _normalize() pour une comparaison honnête.

Propriété fondamentale : un hachage SHA-1 ne peut vérifier QUE
des chaînes déjà connues et exactement vues. Aucun faux positif
partiel possible structurellement — contrairement au matching
sémantique approximatif de cnp_check().

Contrepartie : aucune tolérance aux variantes jamais vues.
"""

import hashlib
import json
import os
import unicodedata
from pathlib import Path

TABLE_PATH = Path(__file__).parent.parent / "data" / "reference" / "cnp-sha-table.json"

_cached_table = None


def load_table(path=None) -> dict:
    """Charge la table SHA depuis le disque (cache après le premier appel)."""
    global _cached_table
    if _cached_table is not None and path is None:
        return _cached_table
    p = path or TABLE_PATH
    with open(p, encoding="utf-8") as f:
        table = json.load(f)
    if path is None:
        _cached_table = table
    return table


# ── Normalisation (identique à cnp_check._normalize) ─────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    nfkd = unicodedata.normalize("NFKD", text)
    without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return " ".join(without_accents.lower().split())


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


# ── Fonctions publiques ───────────────────────────────────────────────────────

def cnp_sha_check(cnp: str, terme_recherche: str, table: dict) -> dict:
    """
    Vérifie par lookup de hachage EXACT (après normalisation)
    si terme_recherche correspond à une appellation connue du CNP.

    Retourne un dict comparable en forme à cnp_check() :
      {
        "cnp": cnp,
        "terme": terme_recherche,
        "cnp_existe": bool,
        "valide": bool,
        "type_correspondance": "exacte" | "aucune",  # JAMAIS "partielle"
        "matched_hash": str | None,
        "appellation_principale": str | None,
      }

    Cas limites : terme_recherche vide, None, ou espaces seuls
    → jamais valide, jamais de hash calculé sur chaîne vide.
    """
    blocs = table.get("blocs", {})
    index = table.get("index_inverse", {})

    bloc_cnp = blocs.get(cnp)
    appellation_principale = bloc_cnp["appellation_principale"] if bloc_cnp else None

    result = {
        "cnp": cnp,
        "terme": terme_recherche,
        "cnp_existe": bloc_cnp is not None,
        "valide": False,
        "type_correspondance": "aucune",
        "matched_hash": None,
        "appellation_principale": appellation_principale,
    }

    if bloc_cnp is None:
        return result

    # Garde : terme vide / None / espaces
    if terme_recherche is None or not isinstance(terme_recherche, str):
        return result
    norm = _normalize(terme_recherche)
    if not norm:
        return result

    h = _sha1(norm)

    # Le hash doit être dans la table ET pointer vers ce CNP
    if h in index and index[h] == cnp:
        result["valide"] = True
        result["type_correspondance"] = "exacte"
        result["matched_hash"] = h

    return result


def sha_lookup(terme_recherche: str, table: dict) -> str | None:
    """
    Retourne le CNP propriétaire de ce terme s'il est déjà connu, None sinon.

    Aucun CNP à fournir en entrée — pure inversion du fardeau de la preuve :
    si le terme a déjà été vu et confirmé exactement, on retrouve son CNP
    sans avoir à proposer un candidat.

    Cas limites : terme vide, None, espaces → None systématiquement.
    """
    if terme_recherche is None or not isinstance(terme_recherche, str):
        return None
    norm = _normalize(terme_recherche)
    if not norm:
        return None
    h = _sha1(norm)
    return table.get("index_inverse", {}).get(h)


if __name__ == "__main__":
    table = load_table()
    print(f"Table chargée : {table['nb_entrees']} entrées, {len(table['blocs'])} CNP")

    tests = [
        ("72300", "Plombiers/plombières"),
        ("72300", "plombier"),                       # partiel → aucune (jamais vu tel quel)
        ("31301", "infirmier autorisé"),              # partiel → aucune
        ("31301", "infirmier itinérant/infirmière itinérante"),  # forme complète → exacte
        ("21222", "analyste de systèmes"),            # autre appellation → exacte
        ("99999", "rien"),                            # CNP inexistant
        ("72300", ""),                                # vide → aucune
        ("72300", None),                              # None → aucune
    ]
    print()
    for cnp, terme in tests:
        r = cnp_sha_check(cnp, terme, table)
        status = "✓" if r["valide"] else "✗"
        print(f"  {status} [{r['type_correspondance']:>6}] CNP {cnp} × \"{terme}\" hash={r['matched_hash'] and r['matched_hash'][:10]}")

    print()
    lookups = ["Plombiers/plombières", "plombier", "infirmier itinérant/infirmière itinérante"]
    for terme in lookups:
        cnp_found = sha_lookup(terme, table)
        print(f"  sha_lookup(\"{terme}\") → {cnp_found}")
