#!/usr/bin/env python3
"""Extrait l'index alphabétique des appellations d'emploi
(data/reference/cnp2021-appellations-index.json) depuis l'index alphabétique
du PDF français de la CNP 2021, converti en Markdown.

Source : ~/Projects/50_JOBSAID/jobpulse/CNP/12-583-x2021001-fra.md

Format des entrées dans le markdown : "**CODE** appellation - contexte",
parfois précédé d'une puce "- ", parfois sans puce et concaténé sur la même
ligne que l'entrée suivante (mise en page à colonnes du PDF d'origine, perdue
à la conversion). On extrait donc chaque paire (code, texte) par une regex
qui borne le texte au prochain code en gras, plutôt que par découpage ligne à
ligne.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path.home() / "Projects/50_JOBSAID/jobpulse/CNP/12-583-x2021001-fra.md"
OUT = Path(__file__).resolve().parent.parent / "data/reference/cnp2021-appellations-index.json"

INDEX_HEADER = "# **Index alphabétique**"
ENTRY_RE = re.compile(r'\*\*(\d{5})\*\*\s*([^\*]*?)(?=\*\*\d{5}\*\*|\Z)', re.DOTALL)


def clean_text(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r'^-\s*', '', s)
    s = s.split('\n')[0].strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def main():
    if not SRC.exists():
        print(f"ERREUR: source introuvable: {SRC}", file=sys.stderr)
        sys.exit(1)

    full = SRC.read_text(encoding="utf-8")
    idx = full.find(INDEX_HEADER)
    if idx == -1:
        print("ERREUR: section 'Index alphabétique' introuvable dans le markdown", file=sys.stderr)
        sys.exit(1)
    section = full[idx:]

    entries = []
    anomalies = []
    seen = set()
    for m in ENTRY_RE.finditer(section):
        code = m.group(1)
        text = clean_text(m.group(2))
        if not text:
            anomalies.append(f"code {code}: texte vide après nettoyage")
            continue
        if "Statistique Canada" in text or text.startswith("#"):
            anomalies.append(f"code {code}: bruit résiduel détecté: {text[:60]!r}")
            continue
        if " - " in text:
            appellation, contexte = text.split(" - ", 1)
            appellation = appellation.strip()
            contexte = contexte.strip() or None
        else:
            appellation, contexte = text, None

        key = (appellation, code, contexte)
        if key in seen:
            continue
        seen.add(key)
        entries.append({
            "appellation": appellation,
            "cnp": code,
            "contexte": contexte,
        })

    out = {
        "source": "12-583-x2021001-fra.pdf (Statistique Canada) — index alphabétique, converti en markdown",
        "description": "Table appellation d'emploi -> code CNP 2021 (5 chiffres), extraite de l'index alphabétique du PDF français. Le contexte est la précision entre tirets quand elle existe.",
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
