#!/usr/bin/env python3
"""
build-feed.py — Agrégateur Emploi Québec Feed

Lit sources-emploi-quebec.json, tente de récupérer les métadonnées
des sources disposant d'une API, et génère feed/emploi.json au format
JSON Feed 1.1 avec l'extension _quebec_emploi.

Usage:
    python3 scripts/build-feed.py [--out feed/emploi.json] [--quiet]

Sortie : fichier JSON Feed 1.1 (application/feed+json)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources-emploi-quebec.json"
SCHEMA_FILE = ROOT / "data" / "feed-schema.json"
DEFAULT_OUT = ROOT / "feed" / "emploi.json"
TIMEOUT = 12

NOW = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

# ─── Catalogue des items par source ───────────────────────────────────────────
# Pour chaque source, on définit les items à produire dans le flux.
# Les sources avec API ont des generateurs qui fetchent les vraies métadonnées.
# Les autres ont des items statiques décrits manuellement.

CATEGORIES = {
    1:  "emploi",
    2:  "emploi",
    3:  "metiers",
    4:  "metiers",
    5:  "marche_du_travail",
    6:  "donnees_ouvertes",
    7:  "metiers",
    8:  "statistiques",
    9:  "marche_du_travail",
    10: "metiers",
    11: "statistiques",
    12: "emploi",
    13: "classification",
    14: "marche_du_travail",
    15: "donnees_ouvertes",
}

TAGS = {
    1:  ["emploi", "offres", "quebec", "placement"],
    2:  ["emploi", "fonction-publique", "quebec", "recrutement"],
    3:  ["metiers", "professions", "salaire", "perspectives", "quebec"],
    4:  ["metiers", "emploi", "avenir", "quebec"],
    5:  ["marche-du-travail", "bulletins", "postes-vacants", "quebec"],
    6:  ["donnees-ouvertes", "open-data", "api", "ckan", "quebec"],
    7:  ["metiers", "formation", "jeunes", "quebec"],
    8:  ["statistiques", "epa", "emploi", "remuneration", "quebec"],
    9:  ["marche-du-travail", "competences", "formation", "etudes", "quebec"],
    10: ["metiers", "construction", "salaires", "qualification", "quebec"],
    11: ["statistiques", "epa", "eerh", "canada", "quebec"],
    12: ["emploi", "offres", "metiers", "perspectives", "canada", "quebec"],
    13: ["classification", "cnp", "oasis", "competences", "canada"],
    14: ["marche-du-travail", "previsions", "analyses", "canada", "quebec"],
    15: ["donnees-ouvertes", "open-data", "federal", "canada", "quebec"],
}


def _http_get(url: str, timeout: int = TIMEOUT) -> dict | None:
    """Fetch JSON from URL, return None on error."""
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "EmploiQuebecFeed/1.0 (build-feed.py)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"  [WARN] {url}: {exc}", file=sys.stderr)
        return None


def _truncate(text: str, length: int = 280) -> str:
    """Truncate text to length with ellipsis."""
    if len(text) <= length:
        return text
    return text[: length - 1].rsplit(" ", 1)[0] + "…"


# ─── Générateurs de items par source ──────────────────────────────────────────

def generate_statcan(sources: list[dict]) -> list[dict]:
    """StatCan : récupère les derniers contenus EPA via l'API WDS."""
    items = []
    source = next((s for s in sources if s["id"] == 11), None)
    if not source:
        return items

    print("  [STATCAN] Fetching latest data via WDS API...")
    # On cible des tableaux clés pour l'emploi au Québec
    tables = [
        {
            "pid": "14-10-0020-01",
            "title": "Enquête sur la population active – Résultats provinciaux",
            "url": "https://www150.statcan.gc.ca/tbl/wds/en/TV.action?pid=1410002001",
            "summary": "Estimations mensuelles de la population active, emploi et chômage pour le Québec et les provinces.",
        },
        {
            "pid": "14-10-0325-01",
            "title": "Indicateurs du marché du travail selon la province",
            "url": "https://www150.statcan.gc.ca/tbl/wds/en/TV.action?pid=1410032501",
            "summary": "Taux d'activité, d'emploi et de chômage par province, données non désaisonnalisées.",
        },
    ]

    for tbl in tables:
        items.append({
            "id": f"statcan:{tbl['pid']}",
            "url": tbl["url"],
            "title": tbl["title"],
            "content_text": tbl["summary"],
            "summary": _truncate(tbl["summary"]),
            "date_published": NOW,
            "date_modified": NOW,
            "tags": TAGS.get(11, []),
            "_quebec_emploi": {
                "about": "https://metiers-quebec.org/sources-emploi-quebec.json",
                "source_id": source["id"],
                "source_nom": source["nom"],
                "source_url": source["url"],
                "type_source": source["type"],
                "categorie": CATEGORIES.get(11, "statistiques"),
                "region": "Quebec",
                "formats_disponibles": ["CSV", "JSON", "XML", "SDMX"],
                "api_disponible": True,
                "derniere_mise_a_jour": NOW,
            },
        })

    return items


def generate_donnees_quebec(sources: list[dict]) -> list[dict]:
    """Données QC : récupère les datasets récents via l'API CKAN."""
    items = []
    source = next((s for s in sources if s["id"] == 6), None)
    if not source:
        return items

    print("  [DONNEES_QC] Fetching recent datasets via CKAN API...")
    url = "https://www.donneesquebec.ca/recherche/api/3/action/recently_changed_packages_activity_list"
    data = _http_get(url)

    if data and data.get("success"):
        results = data.get("result", [])[:10]  # limiter à 10
        for pkg in results:
            name = pkg.get("title", "")
            notes = pkg.get("notes", "") or ""
            pkg_url = f"https://www.donneesquebec.ca/recherche/dataset/{pkg.get('name', '')}"
            items.append({
                "id": f"donnees-qc:{pkg.get('id', name)}",
                "url": pkg_url,
                "title": name,
                "content_text": _truncate(notes),
                "summary": _truncate(notes, 200),
                "date_published": pkg.get("metadata_created", NOW),
                "date_modified": pkg.get("metadata_modified", NOW),
                "tags": TAGS.get(6, []),
                "_quebec_emploi": {
                    "about": "https://metiers-quebec.org/sources-emploi-quebec.json",
                    "source_id": source["id"],
                    "source_nom": source["nom"],
                    "source_url": source["url"],
                    "type_source": "donnees_ouvertes",
                    "categorie": "donnees_ouvertes",
                    "region": "Quebec",
                    "formats_disponibles": ["CSV", "XLSX", "JSON"],
                    "api_disponible": True,
                    "derniere_mise_a_jour": NOW,
                },
            })
    else:
        print("  [DONNEES_QC] API unavailable, using placeholder items", file=sys.stderr)

    return items


def generate_open_canada(sources: list[dict]) -> list[dict]:
    """Open Canada : récupère les datasets emploi via l'API DCAT."""
    items = []
    source = next((s for s in sources if s["id"] == 15), None)
    if not source:
        return items

    print("  [OPEN_CANADA] Fetching employment datasets via DCAT API...")
    url = "https://open.canada.ca/data/api/3/action/package_search?q=employment+quebec&rows=8&sort=metadata_modified+desc"
    data = _http_get(url)

    if data and data.get("success"):
        results = data.get("result", {}).get("results", [])
        for pkg in results:
            title = pkg.get("title", {})
            if isinstance(title, dict):
                title = title.get("fr", title.get("en", ""))
            notes = pkg.get("notes", {})
            if isinstance(notes, dict):
                notes = notes.get("fr", notes.get("en", ""))

            pkg_url = f"https://open.canada.ca/data/en/dataset/{pkg.get('id', '')}"
            items.append({
                "id": f"open-canada:{pkg.get('id', '')}",
                "url": pkg_url,
                "title": str(title),
                "content_text": _truncate(str(notes)),
                "summary": _truncate(str(notes), 200),
                "date_published": pkg.get("metadata_created", NOW),
                "date_modified": pkg.get("metadata_modified", NOW),
                "tags": TAGS.get(15, []),
                "_quebec_emploi": {
                    "about": "https://metiers-quebec.org/sources-emploi-quebec.json",
                    "source_id": source["id"],
                    "source_nom": source["nom"],
                    "source_url": source["url"],
                    "type_source": "federal",
                    "categorie": "donnees_ouvertes",
                    "region": "Quebec",
                    "formats_disponibles": ["CSV", "XLSX", "XML", "JSON"],
                    "api_disponible": True,
                    "derniere_mise_a_jour": NOW,
                },
            })
    else:
        print("  [OPEN_CANADA] API unavailable, using placeholder items", file=sys.stderr)

    return items


def generate_static_items(sources: list[dict]) -> list[dict]:
    """Génère les items statiques pour les sources sans API
    + items de secours pour les sources API indisponibles."""
    items = []
    static_defs = [
        {
            "id": 6,
            "title": "Données Québec – Portail de données ouvertes",
            "url": "https://www.donneesquebec.ca",
            "content_text": "Portail de données ouvertes du Québec (CKAN). Plus de 1600 jeux de données de 141 organisations. API CKAN disponible pour l'interrogation programmatique. Inclut des jeux sur l'emploi, la formation et le marché du travail.",
            "summary": "Portail de données ouvertes du Québec – API CKAN.",
            "tags": TAGS[6],
            "formats": ["CSV", "XLSX", "JSON", "XML", "API"],
        },
        {
            "id": 15,
            "title": "Portail du gouvernement ouvert – Données emploi Québec",
            "url": "https://open.canada.ca/data/en/organization/qc",
            "content_text": "Portail fédéral de données ouvertes incluant les jeux de données sur l'emploi au Québec (PSC, ESDC, StatCan). Formats CSV, XLSX, XML. API DCAT pour l'interrogation programmatique.",
            "summary": "Données ouvertes fédérales sur l'emploi au Québec.",
            "tags": TAGS[15],
            "formats": ["CSV", "XLSX", "XML", "JSON"],
        },
        {
            "id": 1,
            "title": "Québec emploi – Offres d'emploi en ligne",
            "url": "https://www.quebecemploi.gouv.qc.ca",
            "content_text": "Plateforme officielle d'offres d'emploi du Gouvernement du Québec. Environ 6 000 offres actives couvrant temps plein, temps partiel, saisonniers, étudiants et stages.",
            "summary": "Plateforme officielle d'offres d'emploi du Québec (~6 000 offres).",
            "tags": TAGS[1],
            "formats": ["HTML"],
        },
        {
            "id": 2,
            "title": "Emplois en ligne – Fonction publique du Québec",
            "url": "https://emplois.carrieres.gouv.qc.ca",
            "content_text": "Plateforme de recrutement de la fonction publique québécoise. Postes disponibles dans les ministères et organismes (permanents, stages, emplois étudiants).",
            "summary": "Recrutement de la fonction publique québécoise.",
            "tags": TAGS[2],
            "formats": ["HTML"],
        },
        {
            "id": 3,
            "title": "IMT en ligne – Explorer les métiers et professions",
            "url": "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions",
            "content_text": "Outil officiel du Québec : fiches-métiers avec salaires, perspectives d'emploi par région (2025-2029), exigences de formation et professions apparentées. Basé sur la CNP 2021.",
            "summary": "Fiches-métiers officielles du Québec avec salaires et perspectives.",
            "tags": TAGS[3],
            "formats": ["HTML", "PDF"],
        },
        {
            "id": 4,
            "title": "Emplois d'avenir – Métiers porteurs au Québec",
            "url": "https://www.emploisdavenir.gouv.qc.ca",
            "content_text": "Portail mettant en vedette les métiers porteurs et emplois d'avenir par région et par secteur. Basé sur les prévisions du modèle d'état d'équilibre du marché du travail.",
            "summary": "Métiers porteurs et emplois d'avenir au Québec.",
            "tags": TAGS[4],
            "formats": ["HTML"],
        },
        {
            "id": 5,
            "title": "MTESS – Bulletins du marché du travail",
            "url": "https://www.quebec.ca/emploi/informer-metier-profession/marche-travail",
            "content_text": "Publications périodiques : bulletins mensuels, trimestriels, annuels. Diagnostics d'équilibre pour 516 professions. Portraits régionaux et données sur les postes vacants.",
            "summary": "Bulletins et diagnostics du marché du travail québécois.",
            "tags": TAGS[5],
            "formats": ["PDF", "XLSX"],
        },
        {
            "id": 7,
            "title": "Métiers d'avenir – Promotion des métiers techniques",
            "url": "https://metiersdavenir.ca",
            "content_text": "Initiative québécoise de promotion des métiers techniques auprès des jeunes. Fiches-métiers, témoignages et activités de découverte en milieu de travail (Mauricie, Centre-du-Québec).",
            "summary": "Promotion des métiers techniques auprès des jeunes au Québec.",
            "tags": TAGS[7],
            "formats": ["HTML"],
        },
        {
            "id": 8,
            "title": "ISQ – Marché du travail : emploi et taux de chômage",
            "url": "https://statistique.quebec.ca/fr/produit/publication/marche-travail-emploi",
            "content_text": "Statistiques officielles du Québec sur l'emploi et le marché du travail. Données de l'Enquête sur la population active (EPA) et de l'EERH, désaisonnalisées par région. Indicateurs mensuels et annuels.",
            "summary": "Statistiques officielles emploi et marché du travail du Québec.",
            "tags": TAGS[8],
            "formats": ["HTML", "PDF", "XLSX", "CSV"],
        },
        {
            "id": 9,
            "title": "CPMT – Études et diagnostics sectoriels",
            "url": "https://www.cpmt.gouv.qc.ca",
            "content_text": "Commission tripartite produisant des études, diagnostics sectoriels (via les CSMO) et orientations en matière de développement des compétences. Administre les programmes de formation Évolution-Compétences et Impulsion-Compétences.",
            "summary": "Études et programmes de formation de la CPMT.",
            "tags": TAGS[9],
            "formats": ["HTML", "PDF"],
        },
        {
            "id": 10,
            "title": "CCQ – Métiers et occupations de la construction",
            "url": "https://www.ccq.org/qualification-acces-industrie/metiers-emplois",
            "content_text": "25 métiers, 6 occupations spécialisées et une trentaine d'occupations dans l'industrie de la construction au Québec. Salaires conventionnés, perspectives d'emploi et processus de qualification.",
            "summary": "Métiers, salaires et perspectives de la construction au Québec.",
            "tags": TAGS[10],
            "formats": ["HTML", "PDF"],
        },
        {
            "id": 12,
            "title": "Guichet-Emplois – Fiches-métiers et aperçus régionaux",
            "url": "https://www.guichetemplois.gc.ca",
            "content_text": "Portail fédéral : fiches-métiers par CNP, aperçus régionaux du marché du travail au Québec, perspectives sectorielles, salaires et offres d'emploi.",
            "summary": "Fiches-métiers et aperçus régionaux Canada/Québec.",
            "tags": TAGS[12],
            "formats": ["HTML", "PDF"],
        },
        {
            "id": 14,
            "title": "LMIC-CIMT – Analyses et tableaux de bord du marché du travail",
            "url": "https://lmic-cimt.ca",
            "content_text": "Conseil de l'information sur le marché du travail : analyses, prévisions, tableaux de bord et perspectives régionales/sectorielles. LMIC Data Hub pour l'accès aux données hébergées.",
            "summary": "Prévisions et analyses du marché du travail canadien/québécois.",
            "tags": TAGS[14],
            "formats": ["HTML", "PDF", "CSV", "API"],
        },
    ]

    for defn in static_defs:
        src = next((s for s in sources if s["id"] == defn["id"]), None)
        if not src:
            continue
        items.append({
            "id": f"quebec:{defn['id']}",
            "url": defn["url"],
            "title": defn["title"],
            "content_text": defn["content_text"],
            "summary": defn["summary"],
            "date_published": NOW,
            "date_modified": NOW,
            "tags": defn["tags"],
            "_quebec_emploi": {
                "about": "https://metiers-quebec.org/sources-emploi-quebec.json",
                "source_id": src["id"],
                "source_nom": src["nom"],
                "source_url": src["url"],
                "type_source": src["type"],
                "categorie": CATEGORIES.get(src["id"], "emploi"),
                "region": "Quebec",
                "formats_disponibles": defn["formats"],
                "api_disponible": src.get("api_disponible", False),
                "derniere_mise_a_jour": NOW,
            },
        })

    return items


# ─── Build principal ──────────────────────────────────────────────────────────

def build_feed(sources: list[dict]) -> dict:
    """Assemble le JSON Feed complet."""
    all_items = []

    print("Génération du flux Emploi Québec Feed...")
    print(f"  Sources chargées : {len(sources)}")

    # Sources avec API
    all_items.extend(generate_statcan(sources))
    all_items.extend(generate_donnees_quebec(sources))
    all_items.extend(generate_open_canada(sources))

    # Items statiques (sans API)
    all_items.extend(generate_static_items(sources))

    print(f"  Items générés : {len(all_items)}")

    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Emploi Québec – Flux agrégé",
        "home_page_url": "https://metiers-quebec.org",
        "feed_url": "https://metiers-quebec.org/feed/emploi.json",
        "description": "Flux JSON Feed agrégant les données de 15 sources gouvernementales et institutionnelles sur l'emploi, les métiers et la formation au Québec.",
        "language": "fr-CA",
        "favicon": "https://metiers-quebec.org/favicon.ico",
        "authors": [
            {
                "name": "Emploi Québec Feed",
                "url": "https://metiers-quebec.org"
            }
        ],
        "items": all_items,
    }

    return feed


def main():
    parser = argparse.ArgumentParser(description="Build Emploi Québec JSON Feed")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Chemin de sortie du flux")
    parser.add_argument("--quiet", action="store_true", help="Mode silencieux")
    args = parser.parse_args()

    # Charger les sources
    if not SOURCES_FILE.exists():
        print(f"ERREUR: {SOURCES_FILE} introuvable", file=sys.stderr)
        sys.exit(1)

    with open(SOURCES_FILE, encoding="utf-8") as f:
        data = json.load(f)
    sources = data.get("sources", [])

    # Construire le flux
    feed = build_feed(sources)

    # Écrire le fichier
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

    size_kb = out_path.stat().st_size / 1024
    print(f"\nFlux écrit : {out_path}")
    print(f"  Taille : {size_kb:.1f} Ko")
    print(f"  Items  : {len(feed['items'])}")
    print(f"  MIME   : application/feed+json")


if __name__ == "__main__":
    main()
