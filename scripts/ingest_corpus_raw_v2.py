#!/usr/bin/env python3
"""ingest_corpus_raw_v2.py — Couche Atomique : ingestion corpus_raw_v2 → data/atomic/

Stricte stdlib — aucune dépendance externe.
Mapping slug → code CNP : Option B (provisoire, slug = code, code_provisoire: true).
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# --- Constantes ---

ORIGINE_SOURCE = "metiers_quebec"
ORIGINE_METHODE = "scraping"
ORIGINE_CONFIANCE = "moyenne"

# Sections à ignorer (liens, références, pas des faits métier)
SECTIONS_A_IGNORER = {"LIENS RECOMMANDÉS", "VOIR AUSSI"}

# Mapping nom de section normalisé → nom du champ FAIT
SECTION_VERS_FAIT = {
    "DESCRIPTION": "description",
    "MILIEU DE TRAVAIL": "milieux_travail",
    "MILIEUX DE TRAVAIL": "milieux_travail",
    "TÂCHES ET RESPONSABILITÉS": "taches",
    "FORMATION REQUISE": "formation_requise",
    "QUALITÉS ET APTITUDES NÉCESSAIRES": "qualites",
    "QUALITES ET APTITUDES NECESSAIRES": "qualites",
    "EXIGENCES D'ADMISSION": "exigences_admission",
}

# Sections dont la présence compte pour completude
CLE_COMPLETUDE = {
    "description": True,
    "milieux_travail": True,
    "taches": True,
    "formation_requise": True,
    "qualites": True,
    "exigences_admission": False,  # optionnel
    "salaire_median": False,  # absent de corpus_raw_v2
}


def nettoyer_texte(texte_brut: str) -> str:
    """Nettoie le texte scrapé : joint les mots séparés par des \\n, compacter."""
    if not texte_brut:
        return ""
    # Le texte vient du JSON : les \n sont de vrais sauts de ligne après json.load()
    # Compacter les \n simples (mots séparés) en espaces
    texte = re.sub(r"(?<!\n)\n(?!\n)", " ", texte_brut)
    # Les \n\n (double sauts) deviennent des sauts de paragraphe
    texte = re.sub(r"\n{2,}", "\n", texte)
    # Compacter espaces multiples
    texte = re.sub(r"[ \t]+", " ", texte)
    # Nettoyer début/fin
    texte = texte.strip()
    return texte


def normaliser_section(nom_section: str) -> str | None:
    """Normalise un nom de section et retourne le champ FAIT correspondant, ou None."""
    cle = nom_section.strip().upper()
    # Variantes courantes
    if "MILIEU" in cle and "TRAVAIL" in cle:
        return "milieux_travail"
    if "TÂCH" in cle or "TACH" in cle:
        return "taches"
    if "FORMATION" in cle:
        return "formation_requise"
    if "QUALIT" in cle or "APTITU" in cle:
        return "qualites"
    if "DESCRIPTION" in cle:
        return "description"
    if "EXIGENCE" in cle or "ADMISSION" in cle:
        return "exigences_admission"
    return None


def extraire_faits_sections_raw(sections_raw: dict, scraped_at: str) -> tuple[list[dict], dict]:
    """Extrait les FAITS et la completude depuis sections_raw.

    Fusionne les sections qui mappent au même champ (ex: MILIEU DE TRAVAIL
    + MILIEUX DE TRAVAIL → un seul FAIT milieux_travail).
    """
    date_captee = scraped_at[:10] if scraped_at else datetime.now().strftime("%Y-%m-%d")
    champs_valeurs: dict[str, list[str]] = {}
    champs_presents = set()

    for nom_section, texte_brut in sections_raw.items():
        # Ignorer les sections de liens
        if nom_section.upper() in SECTIONS_A_IGNORER:
            continue
        if not texte_brut or not texte_brut.strip():
            continue

        champ = normaliser_section(nom_section)
        if champ is None:
            continue

        valeur = nettoyer_texte(texte_brut)
        if not valeur:
            continue

        champs_valeurs.setdefault(champ, []).append(valeur)
        champs_presents.add(champ)

    # Un seul FAIT par champ — concaténer les sections multiples
    faits = []
    for champ, valeurs in champs_valeurs.items():
        valeur_finale = "\n\n".join(valeurs) if len(valeurs) > 1 else valeurs[0]
        faits.append({
            "champ": champ,
            "valeur": valeur_finale,
            "origine": {
                "source": ORIGINE_SOURCE,
                "date_captee": date_captee,
                "methode": ORIGINE_METHODE,
                "confiance": ORIGINE_CONFIANCE,
            },
        })

    # Construire la completude
    completude = {}
    for champ, obligatoire in CLE_COMPLETUDE.items():
        completude[champ] = champ in champs_presents

    return faits, completude


def construire_fiche(donnees: dict) -> dict:
    """Construit une fiche atomique depuis un fichier corpus_raw_v2."""
    slug = donnees["slug"]
    nom = donnees.get("nom", slug)
    secteur = donnees.get("secteur", "inconnu")
    scraped_at = donnees.get("scraped_at", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    sections_raw = donnees.get("sections_raw", {})

    faits, completude = extraire_faits_sections_raw(sections_raw, scraped_at)

    fiche = {
        "code": slug,
        "code_provisoire": True,
        "noms": [nom],
        "secteur": secteur,
        "faits": faits,
        "completude": completude,
    }
    return fiche


def main():
    parser = argparse.ArgumentParser(description="Ingest corpus_raw_v2 → data/atomic/")
    parser.add_argument("--src", default="data/corpus_raw_v2", help="Dossier source")
    parser.add_argument("--out", default="data/atomic", help="Dossier de sortie")
    parser.add_argument("--limit", type=int, default=0, help="Nombre max de fiches (0=toutes)")
    parser.add_argument("--dry-run", action="store_true", help="Affiche sans écrire")
    args = parser.parse_args()

    src = Path(args.src)
    out = Path(args.out)

    if not src.exists():
        print(f"Erreur: {src} introuvable", file=sys.stderr)
        sys.exit(1)

    fichiers = sorted(src.glob("*.json"))
    if args.limit > 0:
        fichiers = fichiers[:args.limit]

    stats = {"total": 0, "ecrit": 0, "vides": 0}

    for f in fichiers:
        stats["total"] += 1
        try:
            with open(f, "r", encoding="utf-8") as fh:
                donnees = json.load(fh)
        except (json.JSONDecodeError, OSError) as e:
            print(f"ERREUR lecture {f.name}: {e}", file=sys.stderr)
            continue

        fiche = construire_fiche(donnees)

        if not fiche["faits"]:
            stats["vides"] += 1
            if args.dry_run:
                print(f"  IGNORÉ (vide): {f.name}")
            continue

        if args.dry_run:
            nb_faits = len(fiche["faits"])
            print(f"  OK: {fiche['code']} — {nb_faits} faits, {sum(fiche['completude'].values())}/{len(fiche['completude'])} champs")
        else:
            out.mkdir(parents=True, exist_ok=True)
            dest = out / f.name
            with open(dest, "w", encoding="utf-8") as fh:
                json.dump(fiche, fh, ensure_ascii=False, indent=2)
            stats["ecrit"] += 1

    print(f"\nTerminé: {stats['total']} lus, {stats['ecrit']} écrits, {stats['vides']} vides")


if __name__ == "__main__":
    main()
