#!/usr/bin/env python3
"""
coverage_split.py — Compare section coverage: raw source vs pipeline HTML.

For each target concept (salaire, formation, admission, placement, marché, qualités),
detect presence in corpus_raw_v2 via lexical search, and in pipeline HTML.

Output: data/coverage_report.json
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "corpus_raw_v2"
DIST_DIR = BASE_DIR / "dist"

# Target concepts: keys = regex patterns to match against section key names
# keywords = regex patterns to match against section text content
CONCEPTS = {
    "salaire": {
        "keys": [r"salaire", r"salarial", r"donn[ée]e\s*salarial"],
        "keywords": [
            r"salair", r"r[ée]mun[ée]ration", r"\$/heure", r"\$/semaine",
            r"\$/ann[ée]e", r"pourboire",
        ],
        "pipeline_label": "Données salariales",
    },
    "formation": {
        "keys": [r"formation\s*requis", r"programme", r"programmes?\s*d['\u2019]études"],
        "keywords": [
            r"formation\s*requis", r"programme\s*d['\u2019]études",
            r"D\.E\.C\.", r"DEC\b", r"baccalaur[ée]at", r"dipl[ôo]me",
        ],
        "pipeline_label": "Formation requise",
    },
    "admission": {
        "keys": [r"exigence\s*d['\u2019]admission", r"admission"],
        "keywords": [
            r"exigence\s*d['\u2019]admission", r"condition\s*d['\u2019]admission",
            r"pr[ée]requis", r"dossier\s*de\s*candidature",
        ],
        "pipeline_label": "Admission",
    },
    "placement": {
        "keys": [r"placement", r"statistique\s*de\s*placement"],
        "keywords": [
            r"taux\s*de\s*placement", r"placement\s*(?:excellent|tr[èe]s\s*bon|bon|moyen|faible)",
            r"nombre\s*r[ée]pondants?", r"nombre\s*en\s*emploi",
            r"statistique\s*de\s*placement",
        ],
        "pipeline_label": "Placement",
    },
    "marché": {
        "keys": [r"march[ée]\s*du\s*travail", r"exigence\s*du\s*march"],
        "keywords": [
            r"march[ée]\s*du\s*travail", r"perspective\s*d['\u2019]emploi",
            r"demande\s*de\s*main-d['\u2019]œuvre", r"p[ée]nurie",
            r"besoin\s*de\s*main-d['\u2019]œuvre",
        ],
        "pipeline_label": "Marché du travail",
    },
    "qualités": {
        "keys": [r"qualit[ée]", r"aptitude", r"comp[ée]tence"],
        "keywords": [
            r"qualit[ée]s?\s*et\s*aptitude", r"savoir-[êe]tre",
            r"comp[ée]tences?\s*personnelles?", r"atouts?\s*personnel",
        ],
        "pipeline_label": "Qualités et aptitudes requises",
    },
}


def detect_in_source(concept, section_keys, sections_text):
    """Detect concept in raw source via key match + content keywords."""
    all_keys_lower = " ".join(k.lower() for k in section_keys)
    all_text_lower = " ".join(v.lower() for v in sections_text.values())

    for pat in CONCEPTS[concept]["keys"]:
        if re.search(pat, all_keys_lower):
            return True
    for pat in CONCEPTS[concept]["keywords"]:
        if re.search(pat, all_text_lower):
            return True
    return False


def detect_in_pipeline(concept, slug):
    """Check if pipeline HTML has REAL content for this section (not 'Information non disponible.')."""
    html_path = DIST_DIR / "metier" / slug / "index.html"
    if not html_path.exists():
        return False
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    label = CONCEPTS[concept]["pipeline_label"]
    # Find the section heading and check if the next <p> has real content
    idx = content.find(label)
    if idx == -1:
        return False
    # Extract text after heading until next </div> or <h2>
    after = content[idx + len(label):]
    # Get the <p> content
    m = re.search(r'<p>(.*?)</p>', after, re.DOTALL)
    if not m:
        return False
    text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    # Check if it's the placeholder
    if text in ("Information non disponible.", ""):
        return False
    return len(text) > 10


def run():
    if not RAW_DIR.exists():
        print(f"Error: {RAW_DIR} not found. Run corpus_raw_v2.py first.")
        return

    slug_files = sorted(RAW_DIR.glob("*.json"))
    if not slug_files:
        print(f"Error: No .json files in {RAW_DIR}")
        return

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_professions": len(slug_files),
        "concepts": {},
    }

    for concept in CONCEPTS:
        report["concepts"][concept] = {
            "label": CONCEPTS[concept]["pipeline_label"],
            "present_in_source_count": 0,
            "present_in_pipeline_count": 0,
            "both_count": 0,
            "source_only_count": 0,
            "pipeline_only_count": 0,
            "neither_count": 0,
            "details": [],
        }

    for slug_file in slug_files:
        with open(slug_file, "r", encoding="utf-8") as f:
            record = json.load(f)

        slug = record["slug"]
        nom = record["nom"]
        secteur = record["secteur"]
        sections_raw = record.get("sections_raw", {})

        for concept in CONCEPTS:
            in_source = detect_in_source(concept, sections_raw.keys(), sections_raw)
            in_pipeline = detect_in_pipeline(concept, slug)

            report["concepts"][concept]["details"].append({
                "slug": slug,
                "nom": nom,
                "secteur": secteur,
                "present_in_source": in_source,
                "present_in_pipeline": in_pipeline,
            })

            if in_source:
                report["concepts"][concept]["present_in_source_count"] += 1
            if in_pipeline:
                report["concepts"][concept]["present_in_pipeline_count"] += 1
            if in_source and in_pipeline:
                report["concepts"][concept]["both_count"] += 1
            elif in_source and not in_pipeline:
                report["concepts"][concept]["source_only_count"] += 1
            elif not in_source and in_pipeline:
                report["concepts"][concept]["pipeline_only_count"] += 1
            else:
                report["concepts"][concept]["neither_count"] += 1

    # Print summary
    total = report["total_professions"]
    print(f"Coverage report: {total} professions, {len(CONCEPTS)} concepts\n")
    print(f"{'Concept':<15} {'Source':>10} {'Pipeline':>10} {'Both':>8} {'SrcOnly':>10} {'PlOnly':>10} {'None':>8}")
    print("-" * 80)
    for concept in CONCEPTS:
        c = report["concepts"][concept]
        print(
            f"{concept:<15} "
            f"{c['present_in_source_count']:>5}/{total:<4} "
            f"{c['present_in_pipeline_count']:>5}/{total:<4} "
            f"{c['both_count']:>4}/{total:<4} "
            f"{c['source_only_count']:>5}/{total:<4} "
            f"{c['pipeline_only_count']:>5}/{total:<4} "
            f"{c['neither_count']:>4}/{total:<4}"
        )

    out_path = DATA_DIR / "coverage_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    run()
