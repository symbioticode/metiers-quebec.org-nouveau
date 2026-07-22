#!/usr/bin/env python3
"""
Scraper amélioré pour metiers-quebec.org
Version 2 : Meilleur parsing du HTML FrontPage.
"""

import json
import re
import time
import sys
import os
from urllib.parse import urljoin
from html.parser import HTMLParser

BASE_URL = "https://www.metiers-quebec.org"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DELAY = 0.3


def detect_encoding(raw_bytes):
    """Detect encoding: try UTF-8 first, fall back to windows-1252."""
    # Check for BOM
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return 'utf-16'
    
    # Try UTF-8 first
    try:
        text = raw_bytes.decode('utf-8')
        # Verify it's valid UTF-8 with expected French characters
        if any(c in text for c in 'àâäéèêëïîôùûüÿçœæ'):
            return 'utf-8'
    except (UnicodeDecodeError, ValueError):
        pass
    
    # Check for common UTF-8 double-byte sequences in windows-1252 decode
    text_1252 = raw_bytes.decode('windows-1252', errors='replace')
    # If we see patterns like â€™ (curly quotes), â€" (em dash), it's likely UTF-8
    utf8_indicators = ['â€™', 'â€"', 'â€œ', 'Ã©', 'Ã¨', 'Ã ', 'Ã§', 'Ã®', 'dâ€™']
    for indicator in utf8_indicators:
        if indicator in text_1252:
            # Try re-interpreting as UTF-8
            try:
                fixed = text_1252.encode('windows-1252', errors='replace').decode('utf-8', errors='replace')
                if fixed != text_1252:
                    return 'utf-8-as-1252'
            except:
                pass
            break
    
    return 'windows-1252'


class SimpleFetcher:
    def __init__(self, base_url=BASE_URL, delay=DELAY):
        self.base_url = base_url
        self.delay = delay
        self.request_count = 0
        import ssl
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def fetch(self, path):
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
                enc = detect_encoding(raw)
                if enc == 'utf-8-as-1252':
                    # Re-interpret UTF-8 bytes that were in the stream
                    html = raw.decode('windows-1252', errors='replace')
                    try:
                        html = html.encode('windows-1252', errors='replace').decode('utf-8', errors='replace')
                    except:
                        pass
                else:
                    html = raw.decode(enc, errors="replace")
                self.request_count += 1
                if self.request_count % 50 == 0:
                    print(f"  [INFO] {self.request_count} requêtes...")
                time.sleep(self.delay)
                return html
        except urllib.error.HTTPError as e:
            return None
        except Exception as e:
            return None


class ProfessionParserV2(HTMLParser):
    """Parseur amélioré pour les pages de métiers FrontPage."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.current_tag = None
        self.tag_stack = []
        self.skip_tags = {"script", "style", "head"}
        self.in_skip = 0
        self.links = []
        self.in_link = False
        self.link_href = ""
        self.link_text = ""
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.bold_text = []
        self.in_bold = False

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        if tag in self.skip_tags:
            self.in_skip += 1
            return

        attrs_dict = dict(attrs)
        if tag == "table":
            self.in_table = True
            self.current_table = []
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag in ("td", "th") and self.in_tr:
            self.in_td = True
        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith("#") and not href.startswith("javascript"):
                self.in_link = True
                self.link_href = href
                self.link_text = ""
        elif tag in ("b", "strong"):
            self.in_bold = True
        elif tag == "br":
            self.text_parts.append("\n")
        elif tag == "p":
            self.text_parts.append("\n")
        elif tag == "li":
            self.text_parts.append("\n• ")

    def handle_endtag(self, tag):
        if tag in self.skip_tags and self.in_skip > 0:
            self.in_skip -= 1
            if self.tag_stack and self.tag_stack[-1] == tag:
                self.tag_stack.pop()
            return

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
        elif tag == "a" and self.in_link:
            self.in_link = False
            href = self.link_href
            text = self.link_text.strip()
            if text and href and not any(x in href.lower() for x in [
                "accueil", "cadre", ".pdf", "javascript"
            ]):
                self.links.append({"href": href, "text": text})
        elif tag in ("b", "strong"):
            self.in_bold = False

        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_skip > 0:
            return

        if self.in_link:
            self.link_text += data
            return

        text = data.strip()
        if text:
            self.text_parts.append(data)

    def get_full_text(self):
        return "\n".join("".join(self.text_parts).split())

    def parse_sections(self):
        """Parse le texte en sections structurées."""
        full_text = self.get_full_text()

        # Patterns d'en-têtes de sections
        section_patterns = [
            r"(TÂCHES\s+ET\s+RESPONSABILITÉS)",
            r"(MILIEUX?\s+DE\s+TRAVAIL)",
            r"(QUALITÉS?\s+ET\s+APTITUDES?\s+(?:RE)?QUISES?)",
            r"(EXIGENCES?\s+DU\s+MARCHÉ\s+DU\s+TRAVAIL)",
            r"(PROGRAMMES?\s+D['']ÉTUDES?\s+REQUIS?)",
            r"(EXIGENCES?\s+D['']ADMISSION)",
            r"(DONNÉES?\s+SALARIALES?)",
            r"(STATISTIQUES?\S*\s+DE\s+PLACEMENT)",
            r"(LIENS?\s+RECOMMANDÉS?)",
            r"(VOIR\s+AUSSI)",
            r"(DESCRIPTION)",
            r"(PERSPECTIVES?\s+D['']EMPLOI)",
            r"(FORMATION\s+REQUISE?)",
            r"(NIVEAU\s+D['']ÉTUDES?)",
            r"(EMPLOIS?\s+ET\s+DEMANDES?\s+DE\s+MAIN-D['']ŒUVRE)",
        ]

        sections = {}
        current_section = "intro"

        # Chercher les sections dans le texte
        parts = re.split(r"(" + "|".join(section_patterns) + r")", full_text, flags=re.IGNORECASE)

        for part in parts:
            if part is None:
                continue
            part = part.strip()
            if not part:
                continue

            # Vérifier si c'est un en-tête de section
            matched = False
            for pattern in section_patterns:
                if re.match(pattern, part, re.IGNORECASE):
                    current_section = part.upper().strip()
                    sections[current_section] = []
                    matched = True
                    break

            if not matched and current_section:
                if part and len(part) > 3:
                    sections.setdefault(current_section, []).append(part)

        return sections

    def extract_salary_data(self):
        """Extrait les données salariales des tableaux."""
        salaries = []
        for table in self.tables:
            for row in table:
                row_text = " ".join(row).lower()
                if any(kw in row_text for kw in ["salaire", "heure", "$", "minimum", "maximum", "moyen"]):
                    salaries.append(row)
        return salaries

    def extract_links(self):
        """Extrait les liens pertinents."""
        relevant = []
        for link in self.links:
            text = link["text"].strip()
            href = link["href"]
            if text and len(text) > 3 and not text.lower().startswith("retour"):
                relevant.append({"text": text, "href": href})
        return relevant


def scrape_alphabetical_index(fetcher):
    """Récupère toutes les URLs de métiers depuis les index alphabétiques."""
    letters = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "jk",
        "l", "m", "n", "o", "p", "qr", "s", "t", "uv", "wxyz"
    ]

    all_professions = {}

    print("=== Étape 1 : Index alphabétique ===")
    for letter in letters:
        path = f"/alphabetique/{letter}.htm"
        html = fetcher.fetch(path)
        if not html:
            continue

        # Parser les liens directement
        import re
        links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)

        count = 0
        for href, text in links:
            text = text.strip()
            if (text and len(text) > 3
                and not text.lower().startswith("retour")
                and not any(x in href.lower() for x in [
                    "accueil", "cadre", "alphabetique", "programmes",
                    "javascript", "#", ".pdf", "portrait"
                ])):
                # Normaliser l'URL
                if not href.startswith("/"):
                    href = f"/{href}"
                if href not in all_professions:
                    all_professions[href] = text
                    count += 1

        print(f"  {letter.upper()}: {count} métiers")

    print(f"\n  Total : {len(all_professions)} métiers uniques\n")
    return all_professions


def scrape_sectors(fetcher):
    """Récupère les secteurs et leurs métiers."""
    # D'abord, récupérer la liste des secteurs depuis la page d'accueil
    print("=== Étape 2 : Secteurs ===")

    html = fetcher.fetch("/")
    if not html:
        print("  [ERREUR] Impossible de récupérer la page d'accueil")
        return {}

    # Extraire les secteurs du JavaScript
    sector_match = re.search(r'LibelleOption\s*=\s*new\s+Array\((.*?)\);', html, re.DOTALL)
    url_match = re.search(r'CibleURL\s*=\s*new\s+Array\((.*?)\);', html, re.DOTALL)

    if not sector_match or not url_match:
        print("  [ERREUR] Impossible de trouver les secteurs dans le JavaScript")
        # Fallback avec les secteurs connus
        sectors = {
            "administration": "Administration, secrétariat et informatique",
            "aerospatial": "Aérospatial",
            "agriculture": "Agriculture, agroalimentaire et pêcheries",
            "armee": "Armée",
            "arts": "Arts appliquées et d'expression",
            "batiment": "Bâtiment et construction",
            "bois": "Bois (meubles) et matériaux connexes",
            "chimie": "Chimie et biologie",
            "graphique": "Communications graphiques, multimédia et imprimerie",
            "enseignement": "Éducation, enseignement et services de garde",
            "electrotechnique": "Électrotechnique",
            "motorises": "Entretien d'équipements motorisés",
            "foresterie": "Foresterie et papier",
            "metallurgie": "Métallurgie",
            "mode": "Mode et production textile",
            "protection": "Protection publique",
            "restau_tourisme": "Restauration, hôtellerie et tourisme",
            "sante": "Santé",
            "nature": "Sciences naturelles",
            "physique": "Sciences physiques et mathématiques",
            "sociaux": "Services sociaux et juridiques",
            "transport": "Transport",
        }
    else:
        # Parser les arrays JavaScript
        labels_raw = sector_match.group(1)
        urls_raw = url_match.group(1)

        labels = re.findall(r'"([^"]+)"', labels_raw)
        urls = re.findall(r'"([^"]+)"', urls_raw)

        sectors = {}
        for label, url in zip(labels, urls):
            slug = url.strip("/").split("/")[0]
            sectors[slug] = label
            print(f"  Secteur trouvé : {label} ({slug})")

    print(f"\n  {len(sectors)} secteurs trouvés\n")

    # Récupérer les métiers de chaque secteur
    sector_data = {}
    for slug, name in sectors.items():
        # Essayer différents patterns d'URL
        possible_urls = [
            f"/{slug}/{slug}.htm",
            f"/{slug}/{slug}.html",
        ]

        html = None
        for url in possible_urls:
            html = fetcher.fetch(url)
            if html:
                break

        if not html:
            print(f"  {name}: SKIP (pas de page)")
            continue

        # Extraire les liens vers les métiers
        links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
        professions = []
        for href, text in links:
            text = text.strip()
            if (text and len(text) > 3
                and not text.lower().startswith("retour")
                and not any(x in href.lower() for x in [
                    "accueil", "cadre", "sante.htm", "javascript", "#"
                ])):
                if not href.startswith("/"):
                    href = f"/{slug}/{href}"
                professions.append({"url": href, "nom": text})

        sector_data[slug] = {
            "nom": name,
            "slug": slug,
            "metiers": professions,
            "count": len(professions),
        }
        print(f"  {name}: {len(professions)} métiers")

    print(f"\n  {len(sector_data)} secteurs avec métiers\n")
    return sector_data


def scrape_professions(fetcher, professions_dict, max_count=None):
    """Scrape les pages de métiers."""
    print("=== Étape 3 : Détails des métiers ===")

    results = []
    count = 0
    errors = 0

    for url, nom in professions_dict.items():
        if max_count and count >= max_count:
            break

        count += 1
        if count % 100 == 0:
            print(f"  Progression : {count}/{len(professions_dict)}")

        html = fetcher.fetch(url)
        if not html:
            errors += 1
            continue

        parser = ProfessionParserV2()
        try:
            parser.feed(html)
        except Exception:
            errors += 1
            continue

        sections = parser.parse_sections()
        salaries = parser.extract_salary_data()
        links = parser.extract_links()

        # Extraire le titre principal
        title = ""
        for part in parser.text_parts[:20]:
            part = part.strip()
            if part and len(part) > 5 and "NIVEAU" in part.upper():
                title = part
                break

        # Extraire le secteur depuis l'URL
        parts = url.strip("/").split("/")
        sector = parts[0] if len(parts) >= 2 else "inconnu"

        data = {
            "nom": nom,
            "slug": url.split("/")[-1].replace(".htm", "").replace(".html", ""),
            "url_source": url,
            "secteur": sector,
            "titre": title,
            "sections": sections,
            "salaires": salaries,
            "liens": links[:5],  # Max 5 liens
        }

        results.append(data)

    print(f"\n  Terminé : {len(results)} métiers ({errors} erreurs)\n")
    return results


def save_json(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size = os.path.getsize(filepath)
    print(f"  Sauvegardé : {filename} ({size:,} octets)")
    return filepath


def main():
    print("=" * 60)
    print("SCRAPER METIERS-QUEBEC.ORG v2")
    print("=" * 60)
    print()

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

    # Étape 3 : Détails des métiers
    if max_professions:
        test_professions = dict(list(professions.items())[:max_professions])
        details = scrape_professions(fetcher, test_professions, max_count=max_professions)
    else:
        details = scrape_professions(fetcher, professions)

    save_json(details, "professions_details.json")

    # Index de recherche
    search_index = []
    for item in details:
        search_index.append({
            "nom": item.get("nom", ""),
            "slug": item.get("slug", ""),
            "secteur": item.get("secteur", ""),
            "url": item.get("url_source", ""),
        })
    save_json(search_index, "search_index.json")

    # Statistiques
    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"  Métiers uniques : {len(professions)}")
    print(f"  Secteurs : {len(sectors)}")
    print(f"  Détails récupérés : {len(details)}")
    print(f"  Requêtes totales : {fetcher.request_count}")
    print()

    # Vérifier la qualité des données
    with_sections = sum(1 for d in details if d.get("sections"))
    with_salaries = sum(1 for d in details if d.get("salaires"))
    print(f"  Avec sections : {with_sections}/{len(details)}")
    print(f"  Avec salaires : {with_salaries}/{len(details)}")
    print()


if __name__ == "__main__":
    main()
