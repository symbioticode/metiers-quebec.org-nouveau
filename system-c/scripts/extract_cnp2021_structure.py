#!/usr/bin/env python3
"""Extrait la hiérarchie CNP 2021 (data/reference/cnp2021-structure.json)
depuis cnp_2021_version_1.0_-_structure_de_la_classification.csv.

Source : ~/Projects/50_JOBSAID/jobpulse/CNP/
Niveaux CSV : 1=Grande catégorie, 2=Grand groupe, 3=Sous-grand groupe,
4=Sous-groupe, 5=Groupe de base.
"""
import csv
import json
import sys
from pathlib import Path

SRC = Path.home() / "Projects/50_JOBSAID/jobpulse/CNP/cnp_2021_version_1.0_-_structure_de_la_classification.csv"
OUT = Path(__file__).resolve().parent.parent / "data/reference/cnp2021-structure.json"

NIVEAUX = {
    1: "grande_categorie",
    2: "grand_groupe",
    3: "sous_grand_groupe",
    4: "sous_groupe",
    5: "groupe_de_base",
}


def main():
    if not SRC.exists():
        print(f"ERREUR: source introuvable: {SRC}", file=sys.stderr)
        sys.exit(1)

    entries = []
    anomalies = []
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                niveau = int(row["Niveau"])
            except (KeyError, ValueError):
                anomalies.append(f"ligne {i}: niveau illisible: {row}")
                continue
            code = row["Code dela CNP 2021 v1.0"].strip()
            titre = row["Titres de classes"].strip()
            definition = (row.get("Définitions de la classe") or "").strip()
            if niveau not in NIVEAUX:
                anomalies.append(f"ligne {i}: niveau inconnu {niveau}")
                continue
            entries.append({
                "code": code,
                "niveau": NIVEAUX[niveau],
                "titre": titre,
                "definition": definition or None,
            })

    out = {
        "source": "cnp_2021_version_1.0_-_structure_de_la_classification.csv (Statistique Canada)",
        "description": "Hiérarchie complète de la CNP 2021 v1.0 : grande catégorie / grand groupe / sous-grand groupe / sous-groupe / groupe de base.",
        "total_entrees": len(entries),
        "entrees": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Entrées extraites: {len(entries)}")
    for niv, label in NIVEAUX.items():
        n = sum(1 for e in entries if e["niveau"] == label)
        print(f"  {label}: {n}")
    if anomalies:
        print(f"ANOMALIES ({len(anomalies)}):")
        for a in anomalies:
            print(f"  - {a}")
    print(f"Écrit: {OUT}")


if __name__ == "__main__":
    main()
