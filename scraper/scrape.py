#!/usr/bin/env python3
"""
Scraper pour metiers-quebec.org
Récupère les données du site actuel et les stocke en JSON.
"""

import json
import re
import time
import sys
import os
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

BASE_URL = "https://www.metiers-quebec.org"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DELAY = 0.5  # secondes entre les requêtes (respectueux)

# Encodage du site original
ENCODING = "windows-1252"


class SimpleFetcher:
    """Classe pour récupérer les pages web avec urllib."""

    def __init__(self, base_url=BASE_URL, delay=DELAY):
        self.base_url = base_url
        self.delay = delay
        self.request_count = 0
        # Désactiver la vérification SSL (certificat auto-signé sur ce site)
        import ssl
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def fetch(self, path):
        """Récupère une page et retourne le HTML décodé."""
        import urllib.request
        import urllib.error

        url = urljoin(self.base_url, path)
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "MetiersQuebecScraper/1.0 (Projet educatif)",
                "Accept": "text/html",
                "Accept-Encoding": "identity",
            })
            with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as response:
                raw = response.read()
                html = raw.decode(ENCODING, errors="replace")
                self.request_count += 1
                if self.request_count % 20 == 0:
                    print(f"  [INFO] {self.request_count} requêtes effectuées...")
                time.sleep(self.delay)
                return html
        except urllib.error.HTTPError as e:
            print(f"  [ERREUR] {e.code} pour {url}")
            return None
        except Exception as e:
            print(f"  [ERREUR] {e} pour {url}")
            return None


class SectorListParser(HTMLParser):
    """Parse les pages d'index alphabétique pour extraire les URLs de métiers."""

    def __init__(self):
        super().__init__()
        self.professions = []  # [(url, nom)]
        self.current_href = None
        self.current_text = ""
        self.in_link = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href and not href.startswith("#") and not href.startswith("javascript"):
                self.current_href = href
                self.current_text = ""
                self.in_link = True

    def handle_endtag(self, tag):
        if tag == "a" and self.in_link:
            self.in_link = False
            text = self.current_text.strip()
            if self.current_href and text and text.lower() != "retour" and len(text) > 2:
                # Filtrer les liens de navigation
                if not any(x in self.current_href.lower() for x in [
                    "accueil", "cadre", "programmes", "secteur",
                    "alphabetique", "index", "portrait", ".pdf"
                ]):
                    self.professions.append((self.current_href, text))

    def handle_data(self, data):
        if self.in_link:
            self.current_text += data


class ProfessionParser(HTMLParser):
    """Parse une page de métier pour extraire les données structurées."""

    def __init__(self):
        super().__init__()
        self.sections = {}
        self.current_section = None
        self.current_text = ""
        self.in_section = False
        self.depth = 0
        self.title = ""
        self.in_title = False
        self.list_items = []
        self.in_list = False
        self.tables = []
        self.current_table = []
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.section_keywords = [
            "tâches", "responsabilités", "milieux", "qualités",
            "aptitudes", "exigences", "programmes", "admission",
            "données", "salar", "statistiques", "placement",
            "liens", "recommandés", "voir aussi", "description",
            "perspectives", "formation"
        ]

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.current_table = []
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag in ("td", "th") and self.in_tr:
            self.in_td = True
        elif tag == "li":
            self.in_list = True
        elif tag == "h1":
            self.in_title = True
            self.current_text = ""
        elif tag == "u" or (tag == "span" and "MsoSubhead" in str(attrs)):
            pass

    def handle_endtag(self, tag):
        if tag == "table" and self.in_table:
            self.in_table = False
            if self.current_table:
                self.tables.append(self.current_table)
        elif tag == "tr" and self.in_tr:
            self.in_tr = False
            if self.current_row:
                self.current_table.append(self.current_row)
        elif tag in ("td", "th") and self.in_td:
            self.in_td = False
        elif tag == "li" and self.in_list:
            self.in_list = False
            text = self.current_text.strip()
            if text and len(text) > 3:
                self.list_items.append(text)
            self.current_text = ""
        elif tag == "h1" and self.in_title:
            self.in_title = False
            text = self.current_text.strip()
            if text and len(text) > 2:
                self.title = text

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        if self.in_title:
            self.current_text += data
            return

        if self.in_td:
            self.current_row.append(text)
            return

        if self.in_list:
            self.current_text += data
            return

        # Détecter les en-têtes de section (souvent en gras + souligné)
        lower = text.lower().strip()
        for kw in self.section_keywords:
            if kw in lower and len(text) < 80:
                self.current_section = text.strip(": .")
                self.sections[self.current_section] = []
                self.list_items = []
                break

        # Si on est dans une section, collecter le texte
        if self.current_section and not self.in_list:
            if text and len(text) > 5 and text != self.current_section:
                if text not in self.sections.get(self.current_section, []):
                    self.sections.setdefault(self.current_section, []).append(text)

    def get_result(self):
        """Retourne les données structurées du métier."""
        # Extraire les salaires des tableaux
        salaries = []
        for table in self.tables:
            for row in table:
                if any("sal" in cell.lower() or "$" in cell for cell in row):
                    salaries.append(row)

        return {
            "titre": self.title,
            "sections": self.sections,
            "tableaux": self.tables[:3],  # max 3 tableaux
            "salaires": salaries,
        }


def scrape_alphabetical_index(fetcher):
    """Récupère toutes les URLs de métiers depuis les index alphabétiques."""
    letters = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "jk",
        "l", "m", "n", "o", "p", "qr", "s", "t", "uv", "wxyz"
    ]

    all_professions = {}  # url -> nom

    print("=== Étape 1 : Récupération de l'index alphabétique ===")
    for letter in letters:
        path = f"/alphabetique/{letter}.htm"
        print(f"  Lettre {letter.upper()}...", end=" ", flush=True)
        html = fetcher.fetch(path)
        if not html:
            print("SKIP")
            continue

        parser = SectorListParser()
        parser.feed(html)

        count = 0
        for url, nom in parser.professions:
            if url not in all_professions:
                all_professions[url] = nom
                count += 1

        print(f"{count} métiers trouvés")

    print(f"\n  Total : {len(all_professions)} métiers uniques\n")
    return all_professions


def scrape_sectors(fetcher):
    """Récupère la liste des secteurs et leurs métiers."""
    sectors = {
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
        "comptabilite": "Comptabilité et gestion financière",
    }

    print("=== Étape 2 : Récupération des secteurs ===")
    sector_data = {}

    for slug, name in sectors.items():
        path = f"/{slug}/{slug}.htm"
        print(f"  {name}...", end=" ", flush=True)
        html = fetcher.fetch(path)
        if not html:
            print("SKIP")
            continue

        parser = SectorListParser()
        parser.feed(html)

        professions = []
        for url, nom in parser.professions:
            # Normaliser l'URL
            if not url.startswith("/"):
                url = f"/{slug}/{url}"
            professions.append({"url": url, "nom": nom})

        sector_data[slug] = {
            "nom": name,
            "slug": slug,
            "metiers": professions,
            "count": len(professions),
        }
        print(f"{len(professions)} métiers")

    print(f"\n  Total : {len(sector_data)} secteurs\n")
    return sector_data


def scrape_professions(fetcher, professions_dict, max_count=None):
    """Scrape les pages de métiers pour les données structurées."""
    print("=== Étape 3 : Récupération des métiers ===")
    print(f"  {len(professions_dict)} métiers à scraper")

    results = []
    count = 0
    errors = 0

    for url, nom in professions_dict.items():
        if max_count and count >= max_count:
            print(f"\n  Limite atteinte : {max_count} métiers")
            break

        count += 1
        if count % 50 == 0:
            print(f"  Progression : {count}/{len(professions_dict)} ({errors} erreurs)")

        html = fetcher.fetch(url)
        if not html:
            errors += 1
            continue

        parser = ProfessionParser()
        try:
            parser.feed(html)
        except Exception as e:
            errors += 1
            continue

        data = parser.get_result()
        data["url_source"] = url
        data["nom_original"] = nom
        data["slug"] = url.split("/")[-1].replace(".htm", "").replace(".html", "")

        # Extraire le secteur depuis l'URL
        parts = url.strip("/").split("/")
        if len(parts) >= 2:
            data["secteur_slug"] = parts[0]
        else:
            data["secteur_slug"] = "inconnu"

        results.append(data)

    print(f"\n  Terminé : {len(results)} métiers récupérés ({errors} erreurs)\n")
    return results


def save_json(data, filename):
    """Sauvegarde les données en JSON."""
    filepath = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size = os.path.getsize(filepath)
    print(f"  Sauvegardé : {filepath} ({size:,} octets)")
    return filepath


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("SCRAPER METIERS-QUEBEC.ORG")
    print("=" * 60)
    print()

    # Vérifier les arguments
    max_professions = None
    if len(sys.argv) > 1:
        try:
            max_professions = int(sys.argv[1])
            print(f"  Mode test : max {max_professions} métiers\n")
        except ValueError:
            pass

    fetcher = SimpleFetcher()

    # Étape 1 : Index alphabétique
    professions = scrape_alphabetical_index(fetcher)
    save_json(professions, "professions_urls.json")

    # Étape 2 : Secteurs
    sectors = scrape_sectors(fetcher)
    save_json(sectors, "sectors.json")

    # Étape 3 : Détails des métiers (limité en mode test)
    if max_professions:
        # En mode test, on ne scrape que les premiers métiers
        test_professions = dict(list(professions.items())[:max_professions])
        details = scrape_professions(fetcher, test_professions, max_count=max_professions)
    else:
        details = scrape_professions(fetcher, professions)

    save_json(details, "professions_details.json")

    # Statistiques finales
    print("=" * 60)
    print("STATISTIQUES FINALES")
    print("=" * 60)
    print(f"  Métiers uniques : {len(professions)}")
    print(f"  Secteurs : {len(sectors)}")
    print(f"  Détails récupérés : {len(details)}")
    print(f"  Total requêtes : {fetcher.request_count}")
    print()

    # Créer un index simplifié pour la recherche
    search_index = []
    for item in details:
        search_index.append({
            "nom": item.get("nom_original", ""),
            "slug": item.get("slug", ""),
            "secteur": item.get("secteur_slug", ""),
            "titre": item.get("titre", ""),
            "url": item.get("url_source", ""),
        })

    save_json(search_index, "search_index.json")

    print("Terminé !")


if __name__ == "__main__":
    main()
