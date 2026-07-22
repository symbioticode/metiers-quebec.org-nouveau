#!/usr/bin/env python3
"""
Pré-calcul des statistiques pour la page Vue Statistiques.
Extrait les données depuis professions_details.json et sectors.json
et génère stats.json pour le rendu client-side avec Chart.js.
"""

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "dist" / "data"

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


def extract_education_level(prof):
    """Extrait le niveau d'études depuis le titre ou l'intro."""
    text = (prof.get("titre", "") + " " + " ".join(
        prof.get("sections", {}).get("intro", [])
    )).lower()

    if any(kw in text for kw in ["universitaire", "baccalauréat", "maîtrise", "doctorat", "ph.d"]):
        return "Universitaire"
    if any(kw in text for kw in ["collégial", "technicien", "dec", "d.e.p", "attep"]):
        return "Collégial"
    if any(kw in text for kw in ["secondaire", "d.e.s", "secondaire terminé", "high school"]):
        return "Secondaire"
    if any(kw in text for kw in ["formation professionnelle", "d.e.p.", "compétence"]):
        return "Formation professionnelle"
    return "Non spécifié"


def count_indicators(prof):
    """Compte les indicateurs de marché dans le texte."""
    full_text = " ".join(
        item for items in prof.get("sections", {}).values() for item in items
    ).lower()

    return {
        "penurie": bool(re.search(r"pénurie|pénuries|pénurique", full_text)),
        "manque": bool(re.search(r"manque|manques|insuffisan", full_text)),
        "debouche": bool(re.search(r"débouché|débouchés|débouché", full_text)),
        "excellente": bool(re.search(r"excellente|excellent|très favorable|très favorables", full_text)),
        "favorable": bool(re.search(r"favorable|favorables|bonne|bon|prometteur", full_text)),
    }


def compute_section_coverage(professions):
    """Calcule la couverture de chaque section."""
    section_counts = Counter()
    for prof in professions:
        sections = prof.get("sections", {})
        for sname, content in sections.items():
            if content and any(item.strip() for item in content):
                section_counts[sname] += 1

    # Normaliser les noms
    normalized = defaultdict(int)
    mapping = {
        "intro": "Introduction",
        "description": "Description",
        "taches": "Tâches et responsabilités",
        "milieu": "Milieu de travail",
        "milieux": "Milieu de travail",
        "qualites": "Qualités et aptitudes",
        "marche": "Marché du travail",
        "formation": "Formation requise",
        "admission": "Admission",
        "salaires": "Données salariales",
        "placement": "Placement",
        "perspectives": "Perspectives d'emploi",
        "liens": "Liens recommandés",
        "voir_aussi": "Voir aussi",
        "niveau": "Niveau d'études",
    }

    for sname, count in section_counts.items():
        clean = " ".join(sname.split()).strip().lower()
        for key, label in mapping.items():
            if key in clean:
                normalized[label] += count
                break
        else:
            normalized[clean[:30]] += count

    return dict(normalized)


def main():
    print("Chargement des données...")

    with open(DATA_DIR / "professions_details.json", "r", encoding="utf-8") as f:
        professions = json.load(f)

    with open(DATA_DIR / "sectors.json", "r", encoding="utf-8") as f:
        sectors = json.load(f)

    total = len(professions)
    print(f"  {total} métiers, {len(sectors)} secteurs")

    # 1. Répartition par secteur (depuis sectors.json)
    sector_dist = []
    for slug, data in sorted(sectors.items(), key=lambda x: -len(x[1].get("metiers", []))):
        count = len(data.get("metiers", []))
        name = SECTOR_NAMES.get(slug, data.get("nom", slug))
        sector_dist.append({"label": name, "value": count})

    # 2. Niveaux d'études
    edu_counter = Counter()
    for prof in professions:
        level = extract_education_level(prof)
        edu_counter[level] += 1

    edu_levels = [
        {"label": k, "value": v}
        for k, v in edu_counter.most_common()
    ]

    # 3. Indicateurs marché emploi
    market_counts = {"penurie": 0, "manque": 0, "debouche": 0, "excellente": 0, "favorable": 0}
    for prof in professions:
        indicators = count_indicators(prof)
        for key in market_counts:
            if indicators[key]:
                market_counts[key] += 1

    market_data = [
        {"label": "Pénurie de main-d'œuvre", "value": market_counts["penurie"]},
        {"label": "Manque de candidats", "value": market_counts["manque"]},
        {"label": "Débouchés disponibles", "value": market_counts["debouche"]},
        {"label": "Perspectives excellentes", "value": market_counts["excellente"]},
        {"label": "Perspectives favorables", "value": market_counts["favorable"]},
    ]

    # 4. Couverture des sections
    section_coverage = compute_section_coverage(professions)
    coverage_data = [
        {"label": k, "value": v}
        for k, v in sorted(section_coverage.items(), key=lambda x: -x[1])
    ]

    # 5. Top 10 secteurs (détaillé, depuis professions_details.json)
    prof_sectors = Counter()
    for prof in professions:
        sec = prof.get("secteur", "inconnu")
        name = SECTOR_NAMES.get(sec, sec)
        prof_sectors[name] += 1

    top_sectors = [
        {"label": name, "value": count}
        for name, count in prof_sectors.most_common(15)
    ]

    # KPI globaux
    kpis = {
        "total_professions": total,
        "total_sectors": len(sectors),
        "total_with_details": sum(1 for p in professions if len(p.get("sections", {})) > 3),
        "total_with_perspectives": sum(1 for p in professions if any(
            "perspective" in " ".join(sname.split()).lower()
            for sname in p.get("sections", {}).keys()
        )),
    }

    stats = {
        "kpis": kpis,
        "sector_distribution": sector_dist,
        "education_levels": edu_levels,
        "market_indicators": market_data,
        "section_coverage": coverage_data,
        "top_sectors": top_sectors,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "stats.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\nStatistiques sauvegardées : {output_path}")
    print(f"  KPIs : {kpis}")
    print(f"  Secteurs : {len(sector_dist)}")
    print(f"  Niveaux d'études : {len(edu_levels)}")
    print(f"  Indicateurs marché : {len(market_data)}")
    print(f"  Sections couvertes : {len(coverage_data)}")


if __name__ == "__main__":
    main()
