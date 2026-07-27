#!/usr/bin/env python3
"""
Audit adversarial de cnp_sha_check.py contre la checklist des 7 cas de
docs/method/durcissement-outils-classification_v0_1.md §3.

Script d'audit UNIQUEMENT — ne modifie ni cnp_sha_check.py ni la table SHA.
Sortie brute reproduite telle quelle dans docs/kb022-durcissement-sha-check.md.
"""
import sys
import re
import json
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cnp_sha_check import cnp_sha_check, sha_lookup, load_table, _normalize, _sha1  # noqa: E402

table = load_table()


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ── CAS 1 (obligatoire, premier) : collision infirmier/infirmière auxiliaire (31301 vs 32101) ──
section("CAS 1 — collision connue 31301 (infirmier autorisé) vs 32101 (infirmier auxiliaire)")
tests = [
    ("31301", "infirmiere auxiliaire"),
    ("31301", "infirmieres auxiliaires"),
    ("31301", "infirmier auxiliaire"),
    ("31301", "infirmiers auxiliaires"),
    ("32101", "infirmiere auxiliaire"),
    ("32101", "infirmieres auxiliaires"),
]
for cnp, terme in tests:
    r = cnp_sha_check(cnp, terme, table)
    print(cnp, repr(terme), "->", r)
print()
print('sha_lookup("infirmieres auxiliaires") =', sha_lookup("infirmieres auxiliaires", table))
print('sha_lookup("infirmiere auxiliaire")  =', sha_lookup("infirmiere auxiliaire", table))
print('sha_lookup("Infirmières auxiliaires") =', sha_lookup("Infirmières auxiliaires", table))

# ── CAS 2 : chaîne vide ──
section("CAS 2 — chaîne vide")
print(cnp_sha_check("32101", "", table))
print("sha_lookup('') =", sha_lookup("", table))

# ── CAS 3 : None / valeur absente ──
section("CAS 3 — None / valeur absente")
print(cnp_sha_check("32101", None, table))
print("sha_lookup(None) =", sha_lookup(None, table))
print(cnp_sha_check(None, "infirmieres auxiliaires", table))

# ── CAS 4 : type invalide ──
section("CAS 4 — type invalide (terme_recherche non-string)")
for bad in [12345, 3.14, ["infirmiere auxiliaire"], {"x": 1}, True, b"infirmiere auxiliaire"]:
    try:
        r = cnp_sha_check("32101", bad, table)
        print(repr(bad), "->", r)
    except Exception as e:
        print(repr(bad), "-> EXCEPTION", type(e).__name__, e)
for bad in [12345, 3.14, ["infirmiere auxiliaire"], {"x": 1}, True, b"infirmiere auxiliaire"]:
    try:
        r = sha_lookup(bad, table)
        print("sha_lookup", repr(bad), "->", r)
    except Exception as e:
        print("sha_lookup", repr(bad), "-> EXCEPTION", type(e).__name__, e)

section("CAS 4 — type invalide (cnp non-string)")
for bad_cnp in [31301, None, ["32101"], 32101.0]:
    try:
        r = cnp_sha_check(bad_cnp, "infirmieres auxiliaires", table)
        print(repr(bad_cnp), "->", r)
    except Exception as e:
        print(repr(bad_cnp), "-> EXCEPTION", type(e).__name__, e)

# ── CAS 5 : casse différente ──
section("CAS 5 — casse différente")
for t in ["INFIRMIÈRES AUXILIAIRES", "Infirmières Auxiliaires", "infirmières auxiliaires", "InFiRmIèReS aUxIlIaIrEs"]:
    r = cnp_sha_check("32101", t, table)
    print(repr(t), "-> valide=", r["valide"], "type=", r["type_correspondance"])

# ── CAS 6 : singulier vs pluriel (+ sweep exhaustif genre grammatical) ──
section("CAS 6 — singulier vs pluriel")
for t in ["infirmière auxiliaire", "infirmier auxiliaire", "infirmières auxiliaires", "infirmiers auxiliaires"]:
    r = cnp_sha_check("32101", t, table)
    print(repr(t), "-> valide=", r["valide"], "type=", r["type_correspondance"])

section("CAS 6 (suite) — sweep exhaustif : bug de construction dans l'expansion '/' (build_sha_table.py)")


def _expand_slash_variants(norm_app):
    results = [norm_app]
    if "/" not in norm_app:
        return results
    slash_match = re.match(r"(.+?)(/\S+)(.*)", norm_app)
    if slash_match:
        prefix = slash_match.group(1)
        slash_part = slash_match.group(2)
        suffix = slash_match.group(3)
        v1 = f"{prefix}{suffix}".strip()
        v2 = f"{slash_part.lstrip('/')}{suffix}".strip()
        for v in (v1, v2):
            if v and v not in results:
                results.append(v)
    else:
        parts = [v.strip() for v in norm_app.split("/")]
        for part in parts:
            if part and part not in results:
                results.append(part)
    return results


matrix = json.load(open(Path(__file__).parent.parent / "data" / "reference" / "cnp-appellations-officielles.json", encoding="utf-8"))
professions = matrix["professions"]
bug_count = 0
examples = []
for cnp, prof in professions.items():
    toutes = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
    for raw in toutes:
        norm = _normalize(raw)
        if "/" not in norm:
            continue
        for v in _expand_slash_variants(norm)[1:]:
            words = v.split()
            if any(words[i] == words[i + 1] for i in range(len(words) - 1)):
                bug_count += 1
                examples.append((cnp, raw, v))
print(f"Appellations avec '/' balayées : sweep complet des {len(professions)} CNP de la matrice")
print("Variantes générées avec mot dupliqué consécutif (motif de bug) :", bug_count)
for ex in examples:
    print(" ", ex)
print()
print("Vérification : la forme masculine correcte (mot dupliqué retiré) est-elle indexée quand même (sous une autre variante) ?")
for cnp, raw, garbage in examples:
    # Retire une occurrence du mot dupliqué consécutif pour reconstruire la forme correcte attendue.
    candidate = re.sub(r"\b(\w+)( \1)\b", r"\1", garbage, count=1)
    h = _sha1(candidate)
    print(f"  {cnp}: forme masculine correcte attendue = {candidate!r} -> indexée: {h in table['index_inverse']}")

# ── CAS 7 : entités HTML non décodées ──
section("CAS 7 — entités HTML non décodées")
for t in ["infirmières auxiliaires", "infirmi&egrave;res auxiliaires", "plombiers/plombi&egrave;res", "Plombiers/plombières"]:
    r72 = cnp_sha_check("72300", t, table)
    r32 = cnp_sha_check("32101", t, table)
    print(repr(t), "| 32101:", r32["valide"], r32["type_correspondance"], "| 72300:", r72["valide"], r72["type_correspondance"])

section("Vérification source : entités HTML restantes dans cnp-appellations-officielles.json")
count = 0
for cnp, prof in professions.items():
    toutes = [prof["appellation_principale"]] + prof.get("autres_appellations", [])
    for raw in toutes:
        if re.search(r"&[a-zA-Z]+;|&#\d+;", raw):
            count += 1
print("Entités HTML restantes dans la matrice source :", count)

section("Suite de tests existante (test_cnp_sha_check.py) — noms des tests déclarés")
import subprocess  # noqa: E402
out = subprocess.run([sys.executable, str(Path(__file__).parent / "test_cnp_sha_check.py"), "-v"],
                      capture_output=True, text=True)
print(out.stderr.strip())
