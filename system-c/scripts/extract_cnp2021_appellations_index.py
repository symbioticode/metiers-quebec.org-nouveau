#!/usr/bin/env python3
"""Extrait l'index des appellations d'emploi
(data/reference/cnp2021-appellations-index.json) depuis
cnp_2021_version_1.0_-_elements.csv (Statistique Canada), lignes de type
"Tous les exemples".

Source : ~/Projects/50_JOBSAID/jobpulse/CNP/cnp_2021_version_1.0_-_elements.csv

Remplace une première version qui minait cette table depuis l'index
alphabétique du PDF français converti en markdown (voir historique git).
Le CSV est la source officielle, structurée, et couvre les 516 groupes de
base sans les artefacts de mise en page du PDF — à privilégier conformément
au principe déjà appliqué à cnp2021-structure.json.
"""
import csv
import json
import sys
from pathlib import Path

SRC = Path.home() / "Projects/50_JOBSAID/jobpulse/CNP/cnp_2021_version_1.0_-_elements.csv"
OUT = Path(__file__).resolve().parent.parent / "data/reference/cnp2021-appellations-index.json"

TYPE_APPELLATIONS = "Tous les exemples"


def main():
    if not SRC.exists():
        print(f"ERREUR: source introuvable: {SRC}", file=sys.stderr)
        sys.exit(1)

    entries = []
    anomalies = []
    seen = set()
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            type_element = (row.get("Nom du type d’élément Français") or "").strip()
            if type_element != TYPE_APPELLATIONS:
                continue

            code = (row.get("Code de la CNP v1.0") or "").strip()
            texte = (row.get("Description d’élément Français") or "").strip()

            if not code or not texte:
                anomalies.append(f"ligne {i}: code ou texte manquant: {row}")
                continue

            if " - " in texte:
                appellation, contexte = texte.split(" - ", 1)
                appellation = appellation.strip()
                contexte = contexte.strip() or None
            else:
                appellation, contexte = texte, None

            key = (appellation, code, contexte)
            if key in seen:
                anomalies.append(f"ligne {i}: doublon exact ignoré: {key}")
                continue
            seen.add(key)
            entries.append({
                "appellation": appellation,
                "cnp": code,
                "contexte": contexte,
            })

    out = {
        "source": "cnp_2021_version_1.0_-_elements.csv (Statistique Canada), lignes 'Tous les exemples'",
        "description": "Table appellation d'emploi -> code CNP 2021 (5 chiffres), extraite du CSV officiel des éléments de classe. Le contexte est la précision entre tirets quand elle existe.",
        "total_entrees": len(entries),
        "entrees": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Entrées extraites: {len(entries)}")
    if anomalies:
        print(f"ANOMALIES ({len(anomalies)}):")
        for a in anomalies[:30]:
            print(f"  - {a}")
        if len(anomalies) > 30:
            print(f"  ... et {len(anomalies) - 30} autres")
    print(f"Écrit: {OUT}")


if __name__ == "__main__":
    main()
