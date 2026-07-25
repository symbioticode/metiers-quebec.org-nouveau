#!/usr/bin/env python3
"""
Comparaison directe cnp_check() vs cnp_sha_check() sur corpus partagé.

4 catégories :
  A. Round-trip sur les 516 appellation_principale officielles
  B. Variantes connues (autres_appellations des 5 CNP cibles)
  C. Offres d'emploi réelles jamais vues (corpus infirmier/infirmière, kb015)
  D. 29 paires de collision identifiées par le sweep exhaustif de cnp_check()

Mesure : temps d'exécution (perf_counter), couverture (résultat attendu obtenu),
précision (pas de faux positif).
"""

import json
import os
import sys
import time
import unicodedata
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from cnp_check import cnp_check, load_matrix, _normalize as nc_normalize
from cnp_sha_check import cnp_sha_check, sha_lookup, load_table

MATRIX_PATH = Path(__file__).parent.parent / "data" / "reference" / "cnp-appellations-officielles.json"
TABLE_PATH = Path(__file__).parent.parent / "data" / "reference" / "cnp-sha-table.json"

# ── Chargement ────────────────────────────────────────────────────────────────

matrice = load_matrix(str(MATRIX_PATH))
table = load_table(str(TABLE_PATH))
professions = matrice["professions"]

# ── Corpus C — offres d'emploi réelles jamais vues (infirmier/infirmière) ────
# Corpus tiré verbatim de la tâche (kb015.md — audit adversarial exhaustif).
# CNP attendu : 31301 pour les infirmiers autorisés, 32101 pour les auxiliaires.
CORPUS_C = [
    # (terme_recherche, cnp_attendu, valide_attendu)
    ("Infirmier/infirmière autorisé(e)",         "31301", True),
    ("Infirmier(ère) technicien(ne)",             "31301", True),
    ("Infirmière de recherche",                   "31301", True),
    ("Infirmier auxiliaire (temps partiel)",      "32101", True),
    ("Infirmière auxiliaire",                     "32101", True),
    ("Infirmier Auxiliaire Autorisé (H/F)",       "32101", True),
    ("Infirmier Infirmière",                      "31301", True),
]

# ── Corpus D — 29 paires de collision identifiées par le sweep cnp_check() ───
# Tirées verbatim de kb015.md section CATÉGORIE A et B.
# Pour chaque paire (cnpA, cnpB), le terme déclencheur est l'appellation_principale
# de cnpA testée contre cnpB — attendu : valide=True pour les deux (collision).
COLLISION_PAIRS = [
    ("21300", "21399"),
    ("21311", "21399"),
    ("21321", "21399"),
    ("21322", "21399"),
    ("21331", "21399"),
    ("21332", "21399"),
    ("21390", "21399"),
    ("21231", "21399"),
    ("21231", "21311"),
    ("14101", "64314"),
    ("21101", "21320"),
    ("21200", "21201"),
    ("31103", "32104"),
    ("72200", "72201"),
    ("13110", "13111"),
    ("13110", "13112"),
    ("11109", "12200"),
    ("40041", "62200"),
    ("41302", "62200"),
    ("51110", "62200"),
    ("51121", "62200"),
    ("62200", "73311"),
    ("41210", "43109"),
    ("42203", "43109"),
    ("43109", "72600"),
    ("52121", "73112"),
    ("72421", "73209"),
    ("21200", "21222"),  # Catégorie B
    ("62200", "21222"),  # Catégorie B
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def pct(n, total):
    if total == 0:
        return "N/A"
    return f"{100 * n // total}% ({n}/{total})"


def run_categorie_a():
    """Round-trip sur les 516 appellation_principale officielles."""
    total = len(professions)
    ok_check = ok_sha = 0
    fp_check = fp_sha = 0  # faux positifs (valide=True pour mauvais CNP)

    t0 = time.perf_counter()
    for cnp, prof in professions.items():
        terme = prof["appellation_principale"]
        r = cnp_check(cnp, terme, matrice)
        if r["valide"]:
            ok_check += 1
        # Pas de FP possible ici (on teste le bon CNP)
    t_check = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for cnp, prof in professions.items():
        terme = prof["appellation_principale"]
        r = cnp_sha_check(cnp, terme, table)
        if r["valide"]:
            ok_sha += 1
    t_sha = (time.perf_counter() - t0) * 1000

    return {
        "label": "A — Round-trip appellation_principale (516)",
        "total": total,
        "check_ok": ok_check, "check_ms": t_check,
        "sha_ok": ok_sha, "sha_ms": t_sha,
    }


def run_categorie_b():
    """Variantes connues (autres_appellations) des 5 CNP cibles."""
    CNP_CIBLES = ["31301", "72300", "21222", "64100", "12200"]
    corpus = []
    for cnp in CNP_CIBLES:
        prof = professions.get(cnp)
        if not prof:
            continue
        for app in prof.get("autres_appellations", []):
            corpus.append((cnp, app))

    total = len(corpus)
    ok_check = ok_sha = 0

    t0 = time.perf_counter()
    for cnp, terme in corpus:
        r = cnp_check(cnp, terme, matrice)
        if r["valide"]:
            ok_check += 1
    t_check = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for cnp, terme in corpus:
        r = cnp_sha_check(cnp, terme, table)
        if r["valide"]:
            ok_sha += 1
    t_sha = (time.perf_counter() - t0) * 1000

    return {
        "label": f"B — Autres appellations 5 CNP cibles ({total})",
        "total": total,
        "check_ok": ok_check, "check_ms": t_check,
        "sha_ok": ok_sha, "sha_ms": t_sha,
    }


def run_categorie_c():
    """Offres d'emploi réelles jamais vues."""
    total = len(CORPUS_C)
    ok_check = ok_sha = 0

    detail_check = []
    detail_sha = []

    t0 = time.perf_counter()
    for terme, cnp, attendu in CORPUS_C:
        r = cnp_check(cnp, terme, matrice)
        got = r["valide"] == attendu
        ok_check += got
        detail_check.append((terme, cnp, r["valide"], r["type_correspondance"], got))
    t_check = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for terme, cnp, attendu in CORPUS_C:
        r = cnp_sha_check(cnp, terme, table)
        got = r["valide"] == attendu
        ok_sha += got
        detail_sha.append((terme, cnp, r["valide"], r["type_correspondance"], got))
    t_sha = (time.perf_counter() - t0) * 1000

    return {
        "label": f"C — Offres réelles jamais vues ({total})",
        "total": total,
        "check_ok": ok_check, "check_ms": t_check,
        "sha_ok": ok_sha, "sha_ms": t_sha,
        "detail_check": detail_check,
        "detail_sha": detail_sha,
    }


def run_categorie_d():
    """
    29 paires de collision identifiées par le sweep cnp_check().
    Pour chaque paire (cnpA, cnpB) :
      - on teste l'appellation_principale de cnpA contre cnpB
      - si les deux algos retournent valide=True → collision reproduite
    Question : cnp_sha_check() reproduit-il ces faux positifs ?
    Hypothèse : non (le hachage ne peut structurellement pas produire
    de faux positif partiel). On confirme empiriquement.
    """
    total = len(COLLISION_PAIRS)
    collision_check = collision_sha = 0
    details = []

    t0 = time.perf_counter()
    for cnpA, cnpB in COLLISION_PAIRS:
        profA = professions.get(cnpA)
        if not profA:
            continue
        terme = profA["appellation_principale"]
        rA = cnp_check(cnpA, terme, matrice)
        rB = cnp_check(cnpB, terme, matrice)
        both_valid_check = rA["valide"] and rB["valide"]
        if both_valid_check:
            collision_check += 1
        details.append({
            "cnpA": cnpA, "cnpB": cnpB, "terme": terme[:60],
            "check_A": rA["valide"], "check_B": rB["valide"],
        })
    t_check = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for i, (cnpA, cnpB) in enumerate(COLLISION_PAIRS):
        profA = professions.get(cnpA)
        if not profA:
            continue
        terme = profA["appellation_principale"]
        rA = cnp_sha_check(cnpA, terme, table)
        rB = cnp_sha_check(cnpB, terme, table)
        both_valid_sha = rA["valide"] and rB["valide"]
        if both_valid_sha:
            collision_sha += 1
        details[i]["sha_A"] = rA["valide"]
        details[i]["sha_B"] = rB["valide"]
    t_sha = (time.perf_counter() - t0) * 1000

    return {
        "label": f"D — Paires de collision connues ({total})",
        "total": total,
        "collision_check": collision_check,
        "collision_sha": collision_sha,
        "check_ms": t_check, "sha_ms": t_sha,
        "details": details,
    }


def run_sweep_exhaustif():
    """
    Sweep 516×515 : toutes les appellations_principales × tous les CNP.
    Mesure le temps brut des deux algos sur le même corpus.
    """
    cnp_list = list(professions.keys())
    n = len(cnp_list)

    print(f"\nSweep exhaustif : {n}×{n-1} = {n*(n-1)} paires...", flush=True)

    fp_check = fp_sha = 0

    t0 = time.perf_counter()
    for cnpA in cnp_list:
        terme = professions[cnpA]["appellation_principale"]
        for cnpB in cnp_list:
            if cnpA == cnpB:
                continue
            r = cnp_check(cnpB, terme, matrice)
            if r["valide"]:
                fp_check += 1
    t_check = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for cnpA in cnp_list:
        terme = professions[cnpA]["appellation_principale"]
        for cnpB in cnp_list:
            if cnpA == cnpB:
                continue
            r = cnp_sha_check(cnpB, terme, table)
            if r["valide"]:
                fp_sha += 1
    t_sha = (time.perf_counter() - t0) * 1000

    return {
        "n_paires": n * (n - 1),
        "fp_check": fp_check,
        "fp_sha": fp_sha,
        "check_ms": t_check,
        "sha_ms": t_sha,
    }


# ── Rapport ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("COMPARAISON cnp_check() vs cnp_sha_check()")
    print(f"Matrice : {matrice['total_professions']} professions")
    print(f"Table SHA : {table['nb_entrees']} entrées")
    print("=" * 72)

    res_a = run_categorie_a()
    res_b = run_categorie_b()
    res_c = run_categorie_c()
    res_d = run_categorie_d()
    res_sweep = run_sweep_exhaustif()

    # ── Tableau résumé ────────────────────────────────────────────────────────
    print("\n## Tableau comparatif\n")
    print(f"| Catégorie | cnp_check() couverture | cnp_check() ms | cnp_sha_check() couverture | cnp_sha_check() ms |")
    print(f"|---|---|---|---|---|")

    for res in [res_a, res_b]:
        print(
            f"| {res['label']} "
            f"| {pct(res['check_ok'], res['total'])} "
            f"| {res['check_ms']:.1f} ms "
            f"| {pct(res['sha_ok'], res['total'])} "
            f"| {res['sha_ms']:.1f} ms |"
        )

    # Catégorie C (valide_attendu = True pour tous)
    print(
        f"| {res_c['label']} "
        f"| {pct(res_c['check_ok'], res_c['total'])} "
        f"| {res_c['check_ms']:.1f} ms "
        f"| {pct(res_c['sha_ok'], res_c['total'])} "
        f"| {res_c['sha_ms']:.1f} ms |"
    )

    # Catégorie D (collisions reproduites)
    print(
        f"| {res_d['label']} — collisions reproduites "
        f"| {pct(res_d['collision_check'], res_d['total'])} "
        f"| {res_d['check_ms']:.1f} ms "
        f"| {pct(res_d['collision_sha'], res_d['total'])} "
        f"| {res_d['sha_ms']:.1f} ms |"
    )

    # Sweep
    print(
        f"| Sweep exhaustif {res_sweep['n_paires']} paires — faux positifs inter-CNP "
        f"| FP={res_sweep['fp_check']} "
        f"| {res_sweep['check_ms']:.1f} ms "
        f"| FP={res_sweep['fp_sha']} "
        f"| {res_sweep['sha_ms']:.1f} ms |"
    )

    # ── Détail Catégorie C ────────────────────────────────────────────────────
    print("\n## Détail Catégorie C — offres réelles\n")
    print(f"| Terme | CNP attendu | cnp_check() | sha_check() |")
    print(f"|---|---|---|---|")
    for i, (terme, cnp, attendu) in enumerate(CORPUS_C):
        dc = res_c["detail_check"][i]
        ds = res_c["detail_sha"][i]
        check_sym = "✓" if dc[4] else "✗"
        sha_sym = "✓" if ds[4] else "✗"
        print(f"| {terme} | {cnp} | {check_sym} {dc[3]} | {sha_sym} {ds[3]} |")

    # ── Détail Catégorie D ────────────────────────────────────────────────────
    print("\n## Détail Catégorie D — paires de collision\n")
    print(f"| CNP A | CNP B | Terme (tronqué) | cnp_check() collision | cnp_sha_check() collision |")
    print(f"|---|---|---|---|---|")
    for d in res_d["details"]:
        check_col = "OUI" if (d.get("check_A") and d.get("check_B")) else "non"
        sha_col = "OUI" if (d.get("sha_A") and d.get("sha_B")) else "non"
        print(f"| {d['cnpA']} | {d['cnpB']} | {d['terme']} | {check_col} | {sha_col} |")

    # ── Résumé sweep ─────────────────────────────────────────────────────────
    print(f"\n## Sweep exhaustif {res_sweep['n_paires']} paires\n")
    print(f"- cnp_check()     : {res_sweep['fp_check']} faux positifs inter-CNP, {res_sweep['check_ms']:.1f} ms")
    print(f"- cnp_sha_check() : {res_sweep['fp_sha']} faux positifs inter-CNP, {res_sweep['sha_ms']:.1f} ms")
    print(f"- Ratio de vitesse : {res_sweep['check_ms'] / max(res_sweep['sha_ms'], 0.001):.1f}× plus lent pour cnp_check()")

    print("\n## Conclusion brute\n")
    sha_catA = pct(res_a["sha_ok"], res_a["total"])
    check_catA = pct(res_a["check_ok"], res_a["total"])
    print(f"- Cat. A round-trip : cnp_check()={check_catA}, cnp_sha_check()={sha_catA}")
    print(f"- Cat. C offres réelles : cnp_check()={pct(res_c['check_ok'], res_c['total'])}, cnp_sha_check()={pct(res_c['sha_ok'], res_c['total'])}")
    print(f"- Cat. D collisions reproduites : cnp_check()={res_d['collision_check']}/{res_d['total']}, cnp_sha_check()={res_d['collision_sha']}/{res_d['total']}")
    print(f"- Sweep FP : cnp_check()={res_sweep['fp_check']}, cnp_sha_check()={res_sweep['fp_sha']}")


if __name__ == "__main__":
    main()
