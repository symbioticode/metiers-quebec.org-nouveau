#!/usr/bin/env python3
"""Scrape missing building sector professions."""

import json
import os
import re
import time
import sys
from urllib.parse import urljoin
from html.parser import HTMLParser

BASE_URL = "https://www.metiers-quebec.org"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DELAY = 0.3

# Missing professions from building sector
MISSING = [
    {"slug": "architecte", "url": "/batiment/architecte.htm", "nom": "Architecte", "secteur": "batiment"},
    {"slug": "arpenteurl", "url": "/environnement/arpenteur.html", "nom": "Arpenteur(e)-géomètre", "secteur": "batiment"},
    {"slug": "briqueteur", "url": "/batiment/briqueteur.htm", "nom": "Briqueteur(euse)-maçon(ne)", "secteur": "batiment"},
    {"slug": "cimentier", "url": "/batiment/cimentier.htm", "nom": "Cimentier(ère)-applicateur(trice)", "secteur": "batiment"},
    {"slug": "dynamiteur", "url": "/mines/dynamiteur.html", "nom": "Boutefeu-foreur(euse)", "secteur": "batiment"},
    {"slug": "geologuel", "url": "/mines/geologue.html", "nom": "Géologue", "secteur": "batiment"},
    {"slug": "peintre", "url": "/batiment/peintre.htm", "nom": "Peintre en bâtiment", "secteur": "batiment"},
]


def detect_encoding(raw_bytes):
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    try:
        text = raw_bytes.decode('utf-8')
        if any(c in text for c in 'àâäéèêëïîôùûüÿçœæ'):
            return 'utf-8'
    except (UnicodeDecodeError, ValueError):
        pass
    text_1252 = raw_bytes.decode('windows-1252', errors='replace')
    utf8_indicators = ['â€™', 'â€"', 'â€œ', 'Ã©', 'Ã¨', 'Ã ', 'Ã§', 'Ã®']
    for indicator in utf8_indicators:
        if indicator in text_1252:
            try:
                fixed = text_1252.encode('windows-1252', errors='replace').decode('utf-8', errors='replace')
                if fixed != text_1252:
                    return 'utf-8-as-1252'
            except:
                pass
            break
    return 'windows-1252'


class SectionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = {}
        self.current_section = None
        self.current_text = []
        self.in_table = False
        self.in_td = False
        self.td_text = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        if tag == 'td':
            self.in_td = True
            self.td_text = []

    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        if tag == 'td':
            self.in_td = False
            text = ' '.join(self.td_text).strip()
            if text:
                self.current_text.append(text)

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.in_td:
            self.td_text.append(text)
            return
        # Check for section headers
        upper = text.upper().strip()
        section_keywords = {
            'DESCRIPTION': 'description',
            'TÂCHES': 'taches', 'TACHES': 'taches',
            'MILIEU': 'milieu',
            'QUALITÉS': 'qualites', 'QUALITES': 'qualites',
            'MARCHÉ': 'marche', 'MARCHE': 'marche',
            'FORMATION': 'formation',
            'ADMISSION': 'admission', 'EXIGENCES': 'admission',
            'SALAIRES': 'salaires', 'SALARIALE': 'salaires',
            'PLACEMENT': 'placement', 'STATISTIQUES': 'placement',
            'PERSPECTIVES': 'perspectives', 'EMPLOI': 'perspectives',
        }
        for keyword, section_key in section_keywords.items():
            if keyword in upper and len(text) < 80:
                if self.current_section and self.current_text:
                    self.sections.setdefault(self.current_section, []).append(' '.join(self.current_text))
                self.current_section = section_key
                self.current_text = []
                return
        if self.current_section:
            self.current_text.append(text)

    def finish(self):
        if self.current_section and self.current_text:
            self.sections.setdefault(self.current_section, []).append(' '.join(self.current_text))
        return self.sections


def scrape_profession(url, encoding=None):
    import urllib.request
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    full_url = urljoin(BASE_URL, url)
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15, context=ssl_context)
        raw = resp.read()
        if not encoding:
            encoding = detect_encoding(raw)
        html = raw.decode(encoding, errors='replace')
        parser = SectionParser()
        parser.feed(html)
        return parser.finish()
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        return {}


def main():
    # Load existing data
    details_path = os.path.join(DATA_DIR, "professions_details.json")
    with open(details_path, "r") as f:
        details = json.load(f)

    existing_slugs = {p['slug'] for p in details}
    added = 0

    for prof in MISSING:
        if prof['slug'] in existing_slugs:
            print(f"  Skip (exists): {prof['slug']}")
            continue

        print(f"  Scraping: {prof['slug']} ({prof['url']})")
        sections = scrape_profession(prof['url'])
        time.sleep(DELAY)

        entry = {
            "nom": prof['nom'],
            "slug": prof['slug'],
            "url_source": prof['url'],
            "secteur": prof['secteur'],
            "sections": {k: v for k, v in sections.items() if v},
        }
        details.append(entry)
        added += 1
        print(f"    Found {len(entry['sections'])} sections")

    # Save
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {added} professions. Total: {len(details)}")


if __name__ == "__main__":
    main()
