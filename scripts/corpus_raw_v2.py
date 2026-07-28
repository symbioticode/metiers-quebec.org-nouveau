#!/usr/bin/env python3
"""
corpus_raw_v2.py — Extract raw corpus from professions_details.json
No SECTION_MAP, no lossy mapping. Preserves EXACT original keys.

Output: data/corpus_raw_v2/{slug}.json per profession
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "corpus_raw_v2"

SECTOR_NAMES = {
    "administration": "Administration, secrétariat et informatique",
    "aerospatial": "Aérospatial",
    "agriculture": "Agriculture, agroalimentaire et pêcheries",
    "armee": "Armée",
    "arts": "Arts appliquées et d'expression",
    "batiment": "Bâtiment et construction",
    "bois": "Bois (meubles) et matériaux connexes",
    "chimie": "Chimie et biologie",
    "communication": "Communication, documentation et médias",
    "graphique": "Communications graphiques, multimédia et imprimerie",
    "fabric_mec": "Dessin et fabrication mécanique",
    "enseignement": "Éducation, enseignement et services de garde",
    "electrotechnique": "Électrotechnique",
    "motorises": "Entretien d'équipements motorisés",
    "environnement": "Environnement et aménagement du territoire",
    "foresterie": "Foresterie et papier",
    "lettres": "Lettres et langues",
    "mecanique_entr": "Mécanique d'entretien",
    "metallurgie": "Métallurgie",
    "mines": "Mines, pétrole et travaux de génie",
    "mode": "Mode et production textile",
    "protection": "Protection publique",
    "restau_tourisme": "Restauration, hôtellerie et tourisme",
    "sante": "Santé",
    "humaines": "Sciences et techniques humaines",
    "nature": "Sciences naturelles",
    "physique": "Sciences physiques et mathématiques",
    "sociaux": "Services sociaux et juridiques",
    "beaute": "Soins esthétiques et beauté",
    "transport": "Transport",
}


def extract():
    with open(DATA_DIR / "professions_details.json", "r", encoding="utf-8") as f:
        professions = json.load(f)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    written = 0
    total_keys = 0

    for p in professions:
        slug = p.get("slug", "")
        if not slug:
            continue

        sections_raw = {}
        for key, values in p.get("sections", {}).items():
            # Normalize key: replace literal \n with space, collapse whitespace
            clean_key = " ".join(key.split())
            # Join list values into a single text block
            text = "\n".join(values)
            sections_raw[clean_key] = text

        total_keys += len(sections_raw)

        record = {
            "slug": slug,
            "nom": p.get("nom", ""),
            "secteur": p.get("secteur", ""),
            "secteur_nom": SECTOR_NAMES.get(p.get("secteur", ""), p.get("secteur", "")),
            "source_url": p.get("url_source", ""),
            "scraped_at": now,
            "sections_raw": sections_raw,
        }

        out_path = OUTPUT_DIR / f"{slug}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        written += 1

    print(f"Done: {written} files written to {OUTPUT_DIR}")
    print(f"Total section keys across all professions: {total_keys}")


if __name__ == "__main__":
    extract()
