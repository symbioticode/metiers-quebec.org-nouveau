#!/usr/bin/env python3
"""CNP code validation against the official qualificationsquebec.com matrix."""

import json
import os
import re
import unicodedata

MATRIX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "reference", "cnp-appellations-officielles.json"
)

_cached_matrix = None


def load_matrix(path=None):
    """Load the CNP×appellations matrix from disk (cached after first call)."""
    global _cached_matrix
    if _cached_matrix is not None and path is None:
        return _cached_matrix
    p = path or MATRIX_PATH
    with open(p, "r", encoding="utf-8") as f:
        matrice = json.load(f)
    if path is None:
        _cached_matrix = matrice
    return matrice


def _normalize(text):
    """Lowercase, strip accents, collapse whitespace."""
    nfkd = unicodedata.normalize("NFKD", text)
    without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return " ".join(without_accents.lower().split())


def _singularize_naive(text):
    """Naive French singularization: strip trailing 'x' or 's' from each word."""
    words = text.split()
    result = []
    for w in words:
        if w.endswith("eaux"):
            result.append(w[:-1])
        elif w.endswith("x"):
            result.append(w[:-1])
        elif w.endswith("s"):
            result.append(w[:-1])
        else:
            result.append(w)
    return " ".join(result)


def _contains_as_phrase(needle, haystack):
    """Word-boundary match: needle is found as a complete phrase in haystack."""
    pattern = r"(?<!\w)" + re.escape(needle) + r"(?!\w)"
    return re.search(pattern, haystack) is not None


def _build_all_appellations(prof):
    """Return normalized list: [appellation_principale] + autres_appellations."""
    terms = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
    return [_normalize(t) for t in terms]


def cnp_check(cnp, terme_recherche, matrice=None):
    """
    Check if a search term matches a CNP code's appellations.

    Args:
        cnp: 5-digit CNP code string (e.g. "72300")
        terme_recherche: job title / search term to validate
        matrice: optional pre-loaded matrix dict; loaded from disk if None

    Returns:
        dict with keys:
            cnp: the CNP code checked
            terme: the search term checked
            valide: bool — True if CNP exists and term matches
            type_correspondance: "exacte" | "partielle" | "aucune"
            cnp_existe: bool — True if CNP code is in the matrix
            appellation_principale: str or None
            matched_term: str or None — the appellation that matched (if any)
    """
    if matrice is None:
        matrice = load_matrix()

    professions = matrice.get("professions", {})
    prof = professions.get(cnp)

    result = {
        "cnp": cnp,
        "terme": terme_recherche,
        "valide": False,
        "type_correspondance": "aucune",
        "cnp_existe": prof is not None,
        "appellation_principale": prof["appellation_principale"] if prof else None,
        "matched_term": None,
    }

    if prof is None:
        return result

    if terme_recherche is None or not isinstance(terme_recherche, str):
        result["type_correspondance"] = "aucune"
        return result

    norm_search = _normalize(terme_recherche)
    if not norm_search:
        result["type_correspondance"] = "aucune"
        return result
    norm_singular = _singularize_naive(norm_search)
    all_norm = _build_all_appellations(prof)

    # Exact match
    if norm_search in all_norm:
        idx = all_norm.index(norm_search)
        terms_raw = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
        result["valide"] = True
        result["type_correspondance"] = "exacte"
        result["matched_term"] = terms_raw[idx]
        return result

    # Partial match: word-boundary or slash-separated variant matching
    for i, norm_app in enumerate(all_norm):
        norm_app_sing = _singularize_naive(norm_app)

        # Direct word-boundary check (both directions, both singular/normal)
        matched = False
        for needle in (norm_search, norm_singular):
            for haystack in (norm_app, norm_app_sing):
                if _contains_as_phrase(needle, haystack) or _contains_as_phrase(haystack, needle):
                    matched = True
                    break
            if matched:
                break

        if matched:
            terms_raw = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
            result["valide"] = True
            result["type_correspondance"] = "partielle"
            result["matched_term"] = terms_raw[i]
            return result

        # Slash-separated variants: expand "X/Y context" → ["X context", "Y context"]
        slash_match = re.match(r"(.+?)(/\S+)(.*)", norm_app)
        if slash_match:
            prefix = slash_match.group(1)
            slash_part = slash_match.group(2)
            suffix = slash_match.group(3)
            variants_raw = [prefix, slash_part.lstrip("/")]
            expanded = [f"{v}{suffix}".strip() for v in variants_raw]
            for exp in expanded:
                exp_sing = _singularize_naive(exp)
                for needle in (norm_search, norm_singular):
                    for haystack in (exp, exp_sing):
                        if _contains_as_phrase(needle, haystack) or _contains_as_phrase(haystack, needle):
                            terms_raw = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
                            result["valide"] = True
                            result["type_correspondance"] = "partielle"
                            result["matched_term"] = terms_raw[i]
                            return result
        else:
            # No slash pattern — check each variant independently
            variants = [v.strip() for v in norm_app.split("/")]
            for v in variants:
                v_sing = _singularize_naive(v)
                for needle in (norm_search, norm_singular):
                    for haystack in (v, v_sing):
                        if _contains_as_phrase(needle, haystack) or _contains_as_phrase(haystack, needle):
                            terms_raw = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
                            result["valide"] = True
                            result["type_correspondance"] = "partielle"
                            result["matched_term"] = terms_raw[i]
                            return result

    return result


if __name__ == "__main__":
    matrice = load_matrix()
    print(f"Matrix loaded: {matrice['total_professions']} professions")

    tests = [
        ("72300", "plombier"),
        ("72300", "Plombier/plombière"),
        ("72300", "mécanicien en plomberie"),
        ("72300", "infirmière"),
        ("31301", "infirmier"),
        ("31301", "infirmier autorisé"),
        ("99999", "rien"),
        ("21222", "analyste de systèmes"),
    ]
    for cnp, terme in tests:
        r = cnp_check(cnp, terme, matrice)
        status = "✓" if r["valide"] else "✗"
        print(f"  {status} [{r['type_correspondance']:>8}] CNP {cnp} × \"{terme}\" → matched: {r['matched_term']}")
