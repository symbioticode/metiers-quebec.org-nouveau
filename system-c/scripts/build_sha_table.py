#!/usr/bin/env python3
"""
Construit system-c/data/reference/cnp-sha-table.json à partir de
data/reference/cnp-appellations-officielles.json.

Pour chaque appellation connue (appellation_principale + autres_appellations),
chaque variante "/" est expansée en entrées séparées, puis normalisée et hachée
en SHA-1. La même fonction _normalize() que cnp_check.py est utilisée —
comparaison honnête, pas d'avantage artificiellement donné à l'un ou l'autre.

GARDE DE CONSTRUCTION : si un même SHA-1 apparaît pour deux CNP différents,
la construction s'arrête et signale la collision — c'est un test d'intégrité
de la matrice source.
"""

import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

MATRIX_PATH = Path(__file__).parent.parent / "data" / "reference" / "cnp-appellations-officielles.json"
OUT_PATH = Path(__file__).parent.parent / "data" / "reference" / "cnp-sha-table.json"


# ── Normalisation (identique à cnp_check._normalize) ─────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    nfkd = unicodedata.normalize("NFKD", text)
    without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return " ".join(without_accents.lower().split())


# ── Expansion des variantes "/" ───────────────────────────────────────────────

def _expand_slash_variants(norm_app: str) -> list[str]:
    """
    Expanse une appellation normalisée contenant '/' en entrées séparées.
    Ex: "infirmier itinerant/infirmiere itinerante" ->
        ["infirmier itinerant/infirmiere itinerante",   # forme complète
         "infirmier itinerant",
         "infirmiere itinerante"]

    Utilise la même logique de regex que cnp_check.py pour cohérence.
    Inclut toujours la forme complète (non-expansée) en premier.
    """
    results = [norm_app]  # la forme complète est toujours incluse

    if "/" not in norm_app:
        return results

    # Tenter le motif préfixe/variante+suffixe (même regex que cnp_check)
    slash_match = re.match(r"(.+?)(/\S+)(.*)", norm_app)
    if slash_match:
        prefix = slash_match.group(1)
        slash_part = slash_match.group(2)
        suffix = slash_match.group(3)
        # Cas où le premier mot après "/" ne couvre pas tout le préfixe
        # partagé (ex. "infirmier spécialiste/infirmière spécialiste en
        # soins respiratoires") : le mot final du préfixe se retrouve
        # répété au début du suffixe. Retirer cette seule répétition
        # immédiate avant de reconstruire v1 — ne touche que ce motif
        # précis, sans réinterpréter le reste du suffixe.
        prefix_mots = prefix.split()
        suffix_mots = suffix.strip().split()
        if prefix_mots and suffix_mots and prefix_mots[-1] == suffix_mots[0]:
            suffix_mots = suffix_mots[1:]
        v1 = " ".join(prefix_mots + suffix_mots).strip()
        v2 = f"{slash_part.lstrip('/')}{suffix}".strip()
        for v in (v1, v2):
            if v and v not in results:
                results.append(v)
    else:
        # Pas de motif préfixe/suffixe — splitter directement sur "/"
        parts = [v.strip() for v in norm_app.split("/")]
        for part in parts:
            if part and part not in results:
                results.append(part)

    return results


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


# ── Construction de la table ──────────────────────────────────────────────────

def build_table(matrix_path: Path = MATRIX_PATH) -> dict:
    with open(matrix_path, encoding="utf-8") as f:
        matrice = json.load(f)

    professions = matrice.get("professions", {})

    # index_inverse : sha1_hex -> cnp  (pour détection collision)
    index_inverse: dict[str, str] = {}
    blocs: dict[str, dict] = {}
    collisions: list[dict] = []

    for cnp, prof in professions.items():
        appellation_principale = prof["appellation_principale"]
        autres = prof.get("autres_appellations", [])
        toutes = [appellation_principale] + autres

        hashes_du_cnp: list[str] = []

        for appellation_raw in toutes:
            norm = _normalize(appellation_raw)
            if not norm:
                continue
            variantes = _expand_slash_variants(norm)
            for variant in variantes:
                if not variant:
                    continue
                h = _sha1(variant)
                if h in index_inverse and index_inverse[h] != cnp:
                    # GARDE DE CONSTRUCTION — collision SHA-1 entre deux CNP distincts
                    collisions.append({
                        "sha1": h,
                        "chaine_normalisee": variant,
                        "cnp_existant": index_inverse[h],
                        "cnp_nouveau": cnp,
                    })
                    # On continue pour recenser TOUTES les collisions avant d'arrêter
                elif h not in index_inverse:
                    index_inverse[h] = cnp
                    if h not in hashes_du_cnp:
                        hashes_du_cnp.append(h)

        blocs[cnp] = {
            "appellation_principale": appellation_principale,
            "hashes": hashes_du_cnp,
        }

    if collisions:
        print("ERREUR — GARDE DE CONSTRUCTION : collisions SHA-1 détectées !", file=sys.stderr)
        for c in collisions:
            print(
                f"  SHA-1 {c['sha1'][:12]}... — chaîne \"{c['chaine_normalisee']}\""
                f" → CNP {c['cnp_existant']} ↔ CNP {c['cnp_nouveau']}",
                file=sys.stderr,
            )
        sys.exit(1)

    table = {
        "version": "1.0",
        "genere_depuis": "cnp-appellations-officielles.json",
        "nb_entrees": len(index_inverse),
        "blocs": blocs,
        "index_inverse": index_inverse,
    }
    return table


def main():
    print(f"Chargement matrice : {MATRIX_PATH}")
    table = build_table()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"Table générée : {OUT_PATH}")
    print(f"  {len(table['blocs'])} CNP")
    print(f"  {table['nb_entrees']} entrées SHA-1 dans l'index inverse")
    print("  0 collision détectée — intégrité de la matrice source confirmée")


if __name__ == "__main__":
    main()
