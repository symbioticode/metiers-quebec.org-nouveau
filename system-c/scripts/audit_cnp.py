#!/usr/bin/env python3
"""Audit taches/*.json and offres/*.json against the CNP×appellations matrix."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from cnp_check import cnp_check, load_matrix

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "raw-comparaison")
TACHES_DIR = os.path.join(BASE, "taches")
OFFRES_DIR = os.path.join(BASE, "offres")
OUTPUT = os.path.join(BASE, "audit-cnp.md")

TARGET_CNPS = ["31301", "72300", "21222", "64100", "12200"]


def audit_nom_metier(cnp, nom_metier, matrice):
    """Check if nom_metier matches the CNP's known appellations."""
    return cnp_check(cnp, nom_metier, matrice)


def audit_offre_titre(cnp, titre, matrice):
    """Check if an offer title matches the CNP's known appellations."""
    return cnp_check(cnp, titre, matrice)


def audit_file(filepath, matrice, file_type):
    """Audit a single JSON file. Returns list of findings."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    cnp = data.get("cnp", "?????")
    nom_metier = data.get("nom_metier", "")
    findings = []

    # Check nom_metier
    r = audit_nom_metier(cnp, nom_metier, matrice)
    findings.append({
        "field": "nom_metier",
        "value": nom_metier,
        "valide": r["valide"],
        "type_correspondance": r["type_correspondance"],
        "matched_term": r["matched_term"],
    })

    # For offres: check each offer's titre
    if file_type == "offres":
        sources = data.get("sources", {})
        for source_name, source_data in sources.items():
            offres = source_data.get("offres", [])
            for offre in offres:
                titre = offre.get("titre", "")
                if titre:
                    r = audit_offre_titre(cnp, titre, matrice)
                    findings.append({
                        "field": f"offre.{source_name}.titre",
                        "value": titre,
                        "valide": r["valide"],
                        "type_correspondance": r["type_correspondance"],
                        "matched_term": r["matched_term"],
                    })

    return cnp, nom_metier, findings


def main():
    matrice = load_matrix()
    lines = []
    lines.append("# Audit CNP × appellations")
    lines.append("")
    lines.append(f"Matrice source: qualificationsquebec.com ({matrice['total_professions']} professions)")
    lines.append(f"Date de l'audit: 2026-07-24")
    lines.append("")

    total_checks = 0
    total_ok = 0
    total_partial = 0
    total_fail = 0

    for file_type, directory in [("taches", TACHES_DIR), ("offres", OFFRES_DIR)]:
        lines.append(f"## {file_type.capitalize()}")
        lines.append("")

        for cnp_code in TARGET_CNPS:
            filepath = os.path.join(directory, f"{cnp_code}.json")
            if not os.path.exists(filepath):
                lines.append(f"### CNP {cnp_code} — fichier manquant")
                lines.append("")
                continue

            cnp, nom_metier, findings = audit_file(filepath, matrice, file_type)

            # Get official appellation
            prof = matrice["professions"].get(cnp, {})
            official = prof.get("appellation_principale", "N/A")

            lines.append(f"### CNP {cnp} — {nom_metier}")
            lines.append(f"- **Appellation officielle Q2**: {official}")
            lines.append(f"- **nom_metier dans le fichier**: {nom_metier}")
            lines.append("")

            for finding in findings:
                total_checks += 1
                status = "✅" if finding["valide"] else "❌"
                if finding["valide"]:
                    if finding["type_correspondance"] == "exacte":
                        total_ok += 1
                    else:
                        total_partial += 1
                else:
                    total_fail += 1

                match_info = f" → `{finding['matched_term']}`" if finding["matched_term"] else ""
                lines.append(
                    f"- {status} **{finding['field']}**: \"{finding['value']}\" "
                    f"[{finding['type_correspondance']}]{match_info}"
                )
            lines.append("")

    # Summary
    lines.insert(2, f"- **{total_checks} vérifications** au total")
    lines.insert(3, f"- **{total_ok} correspondances exactes** + **{total_partial} partielles** + **{total_fail} échecs**")
    lines.insert(4, "")

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Audit written to {OUTPUT}")
    print(f"Total: {total_checks} checks — {total_ok} exact, {total_partial} partial, {total_fail} failed")


if __name__ == "__main__":
    main()
