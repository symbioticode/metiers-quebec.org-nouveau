#!/usr/bin/env python3
"""
Génère data/raw-comparaison/table-comparaison.md.

Lit les données brutes de taches/ et offres/ et les dispose côte à côte,
verbatim, sans résumer ni interpréter. Une section par métier.

Sources attendues :
  taches/{cnp}.json         → NOC (noc_oasis), Guichet-Emplois, IMT en ligne
  offres/{cnp}.json         → Jobillico, Jobboom, Emploisdecadres

Certains métiers ont deux CNP différents selon la session d'extraction
(ex. plombier : 72300 dans taches/, 73200 dans offres/ jobboom). Les deux
sont affichés sans trancher.
"""

import json
import os
from pathlib import Path

BASE = Path(__file__).parent
TACHES_DIR = BASE / "taches"
OFFRES_DIR = BASE / "offres"
OUT = BASE / "table-comparaison.md"

# ── Définition des métiers ────────────────────────────────────────────────────
# cnp_taches : code dans taches/
# cnp_offres_a : code dans offres/ pour le fichier format-A (jobillico+jobboom+emploisdecadres)
# cnp_offres_b : code dans offres/ pour le fichier format-B (jobboom+emploisdecadres seulement)
METIERS = [
    {
        "nom_recherche": "Infirmière / infirmier autorisé",
        "cnp_taches": "31301",
        "cnp_offres_a": None,   # perdu (rm -f du 2026-07-24)
        "cnp_offres_b": "31301",
    },
    {
        "nom_recherche": "Plombier / plombière",
        "cnp_taches": "72300",
        "cnp_offres_a": "72300",
        "cnp_offres_b": "73200",
    },
    {
        "nom_recherche": "Analyste / spécialiste en informatique",
        "cnp_taches": "21222",
        "cnp_offres_a": "21222",
        "cnp_offres_b": "21211",
    },
    {
        "nom_recherche": "Vendeur / vendeuse en commerce de détail",
        "cnp_taches": "64100",
        "cnp_offres_a": None,   # perdu (rm -f du 2026-07-24)
        "cnp_offres_b": "64100",
    },
    {
        "nom_recherche": "Technicien(ne) en comptabilité",
        "cnp_taches": "12200",
        "cnp_offres_a": "12200",
        "cnp_offres_b": "14200",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def bloc(titre: str, texte: str, niveau: int = 3) -> str:
    h = "#" * niveau
    if not texte or not texte.strip():
        return f"{h} {titre}\n\n_(aucun texte disponible)_\n\n"
    return f"{h} {titre}\n\n{texte.strip()}\n\n"


def offres_bloc(source_nom: str, offres: list, echec: bool, cause: str = "") -> str:
    lines = [f"### {source_nom}\n"]
    if echec or not offres:
        raison = cause or "0 offre extrait"
        lines.append(f"_{raison}_\n")
        return "\n".join(lines) + "\n"
    for i, o in enumerate(offres, 1):
        titre = o.get("titre", "sans titre")
        url = o.get("url", "")
        texte = (o.get("taches_verbatim") or o.get("texte_brut") or "").strip()
        lines.append(f"#### Offre {i} — {titre}")
        if url:
            lines.append(f"URL : {url}")
        lines.append("")
        lines.append(texte if texte else "_(texte vide)_")
        lines.append("")
    return "\n".join(lines) + "\n"


# ── Génération ────────────────────────────────────────────────────────────────

def generer():
    sections = []

    sections.append("# Table de comparaison brute — tâches par métier et par source\n")
    sections.append(
        "_Généré par `generate_table.py`. Textes verbatim, sans résumé ni interprétation._"
        " Colonne **Notes** à remplir manuellement.\n\n"
    )
    sections.append(
        "**Sources :** NOC (StatCan/OASIS), Guichet-Emplois (EDSC), IMT en ligne (Québec),"
        " Jobillico, Jobboom, Emploisdecadres.\n\n"
    )
    sections.append("---\n\n")

    for m in METIERS:
        nom = m["nom_recherche"]
        cnp_t = m["cnp_taches"]
        cnp_a = m["cnp_offres_a"]
        cnp_b = m["cnp_offres_b"]

        # Construire l'en-tête avec les CNP disponibles
        cnps_connus = sorted({c for c in [cnp_t, cnp_a, cnp_b] if c})
        cnp_label = " / ".join(cnps_connus)

        sections.append(f"## {nom} (CNP : {cnp_label})\n\n")

        # ── Sources institutionnelles (taches/) ──────────────────────────────
        t = load(TACHES_DIR / f"{cnp_t}.json")
        sources_inst = t.get("sources", {})

        noc = sources_inst.get("noc_oasis", {})
        sections.append(bloc(
            f"NOC — {noc.get('url', 'StatCan OASIS')}",
            noc.get("texte_brut", ""),
        ))

        ge = sources_inst.get("guichet_emplois", {})
        sections.append(bloc(
            f"Guichet-Emplois — {ge.get('url', '')}",
            ge.get("texte_brut", ""),
        ))

        imt = sources_inst.get("imt_en_ligne", {})
        sections.append(bloc(
            f"IMT en ligne — {imt.get('url', '')}",
            imt.get("texte_brut", ""),
        ))

        # ── Jobillico (offres/ format-A) ─────────────────────────────────────
        if cnp_a:
            oa = load(OFFRES_DIR / f"{cnp_a}.json")
            jbco = oa.get("sources", {}).get("jobillico", {})
            offres_jbco = jbco.get("offres", [])
            echec_jbco = len(offres_jbco) == 0
            cause_jbco = jbco.get("notes", "")
        else:
            offres_jbco = []
            echec_jbco = True
            cause_jbco = (
                "Données perdues — fichier offres/ écrasé lors du rm -f du 2026-07-24."
                " IDs connus dans rapport.md."
            )
        sections.append(offres_bloc("Jobillico", offres_jbco, echec_jbco, cause_jbco))

        # ── Jobboom (offres/ format-B = résultat session Playwright) ─────────
        if cnp_b:
            ob = load(OFFRES_DIR / f"{cnp_b}.json")
            jboom_data = ob.get("jobboom", {})
            offres_jboom = jboom_data.get("offres", [])
            echec_jboom = jboom_data.get("echec", len(offres_jboom) == 0)
            cause_jboom = jboom_data.get("cause", "")
        else:
            offres_jboom, echec_jboom, cause_jboom = [], True, ""
        sections.append(offres_bloc("Jobboom", offres_jboom, echec_jboom, cause_jboom))

        # ── Emploisdecadres (offres/ format-B) ───────────────────────────────
        if cnp_b:
            edec_data = ob.get("emploisdecadres", {})
            offres_edec = edec_data.get("offres", [])
            echec_edec = edec_data.get("echec", len(offres_edec) == 0)
            cause_edec = edec_data.get("cause", "")
        else:
            offres_edec, echec_edec, cause_edec = [], True, ""
        sections.append(offres_bloc("Emploisdecadres", offres_edec, echec_edec, cause_edec))

        # ── Notes (vide) ──────────────────────────────────────────────────────
        sections.append("### Notes\n\n_à compléter_\n\n")
        sections.append("---\n\n")

    OUT.write_text("".join(sections), encoding="utf-8")
    print(f"Table générée : {OUT}")
    print(f"Taille : {OUT.stat().st_size} octets")


if __name__ == "__main__":
    generer()
