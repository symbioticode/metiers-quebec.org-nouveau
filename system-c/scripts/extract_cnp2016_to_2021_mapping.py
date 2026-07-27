#!/usr/bin/env python3
"""Extrait la table de correspondance CNP 2016 -> CNP 2021
(data/reference/cnp2016-to-cnp2021-mapping.json) depuis
noc2016v1_3-noc2021v1_0-eng.csv.

Note: le CSV source de Statistique Canada n'existe qu'en anglais pour
cette table de correspondance (pas de version fra disponible dans le
dossier source). Les titres restent donc en anglais ici; l'usage prévu
est la traçabilité de codes, pas l'affichage.
"""
import csv
import json
import sys
from pathlib import Path

SRC = Path.home() / "Projects/50_JOBSAID/jobpulse/CNP/noc2016v1_3-noc2021v1_0-eng.csv"
OUT = Path(__file__).resolve().parent.parent / "data/reference/cnp2016-to-cnp2021-mapping.json"


def main():
    if not SRC.exists():
        print(f"ERREUR: source introuvable: {SRC}", file=sys.stderr)
        sys.exit(1)

    entries = []
    anomalies = []
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            code_2016 = (row.get("NOC 2016 V1.3 Code") or "").strip()
            titre_2016 = (row.get("NOC 2016 V1.3 Title") or "").strip()
            type_changement = (row.get(" GSIM Type of Change") or row.get("GSIM Type of Change") or "").strip()
            code_2021 = (row.get("NOC 2021 V1.0 Code") or "").strip()
            titre_2021 = (row.get("NOC 2021 V1.0 Title") or "").strip()
            notes = (row.get("Notes") or "").strip()

            if not code_2016 or not code_2021:
                anomalies.append(f"ligne {i}: code manquant: {row}")
                continue

            entries.append({
                "cnp_2016": code_2016,
                "titre_2016_en": titre_2016,
                "cnp_2021": code_2021,
                "titre_2021_en": titre_2021,
                "type_changement": type_changement or None,
                "notes": notes or None,
            })

    out = {
        "source": "noc2016v1_3-noc2021v1_0-eng.csv (Statistique Canada)",
        "langue_source": "anglais (aucune version française disponible pour cette table de correspondance)",
        "description": "Table de correspondance CNP 2016 v1.3 -> CNP 2021 v1.0, pour traçabilité historique des sources externes référençant encore la CNP 2016.",
        "total_entrees": len(entries),
        "entrees": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Entrées extraites: {len(entries)}")
    if anomalies:
        print(f"ANOMALIES ({len(anomalies)}):")
        for a in anomalies:
            print(f"  - {a}")
    print(f"Écrit: {OUT}")


if __name__ == "__main__":
    main()
