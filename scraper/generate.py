#!/usr/bin/env python3
"""
Générateur de site statique pour metiers-quebec.org
"""

import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "dist"

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

SECTOR_ICONS = {
    "administration": "💻", "aerospatial": "✈️", "agriculture": "🌾",
    "armee": "🎖️", "arts": "🎨", "batiment": "🏗️", "bois": "🪵",
    "chimie": "🔬", "communication": "📢", "graphique": "🖨️",
    "fabric_mec": "🔧", "enseignement": "🎓", "electrotechnique": "⚡",
    "motorises": "🔩", "environnement": "🌿", "foresterie": "🌲",
    "lettres": "📚", "mecanique_entr": "⚙️", "metallurgie": "⚒️",
    "mines": "⛏️", "mode": "👗", "protection": "🛡️",
    "restau_tourisme": "🍽️", "sante": "🏥", "humaines": "🧠",
    "nature": "🌿", "physique": "📐", "sociaux": "⚖️",
    "beaute": "💄", "transport": "🚛",
}

SECTION_MAP = {
    "description": "description",
    "taches": "taches", "tâches": "taches",
    "milieu": "milieu", "milieux": "milieu",
    "qualites": "qualites", "qualités": "qualites",
    "marche": "marche", "marché": "marche",
    "formation": "formation", "programmes": "formation",
    "admission": "admission", "exigences": "admission",
    "salaires": "salaires", "salariale": "salaires", "salarial": "salaires",
    "placement": "placement", "statistiques": "placement",
    "liens": "liens", "recommandés": "liens",
    "perspectives": "perspectives", "emploi": "perspectives",
    "niveau": "niveau", "études": "niveau",
    "voir_aussi": "voir_aussi",
}


def normalize_section(name):
    clean = " ".join(name.split()).strip().lower()
    for key, val in SECTION_MAP.items():
        if key in clean:
            return val
    return "other"


def he(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fmt(content_list):
    if not content_list:
        return "<p>Information non disponible.</p>"
    parts = []
    for item in content_list:
        # Replace newlines with spaces and normalize whitespace
        item = " ".join(item.split()).strip()
        if not item:
            continue
        parts.append(f"<p>{he(item)}</p>")
    return "\n".join(parts)


def page_shell(title, desc, active_nav, sidebar_html, content_html, extra_css=""):
    return f'''<!DOCTYPE html>
<html lang="fr-CA">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{he(title)} — Métiers Québec</title>
  <meta name="description" content="{he(desc)}">
  <link rel="stylesheet" href="/css/style.css">
  {extra_css}
</head>
<body>
  <header class="header">
    <a href="/" class="header__logo">
      <svg viewBox="0 0 36 36" fill="none"><rect width="36" height="36" rx="8" fill="rgba(255,255,255,0.15)"/><path d="M18 6c-2 4-6 6-6 10a6 6 0 0 0 12 0c0-4-4-6-6-10z" stroke="white" stroke-width="2" fill="none"/><path d="M18 28v-6" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
      Métiers Québec
    </a>
    <div class="header__search">
      <svg class="header__search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="headerSearch" placeholder="Recherche un métier, un secteur..." autocomplete="off">
      <div class="search-results" id="headerSearchResults"></div>
    </div>
    <nav class="header__nav" aria-label="Navigation principale">
      <a href="/secteurs/" class="header__nav-link{" header__nav-link--active" if active_nav=="secteurs" else ""}">Secteurs</a>
      <a href="/alpha/" class="header__nav-link{" header__nav-link--active" if active_nav=="alpha" else ""}">Index A-Z</a>
      <a href="/stats/" class="header__nav-link{" header__nav-link--active" if active_nav=="stats" else ""}">Stats</a>
    </nav>
    <button class="header__menu-btn" id="menuBtn" aria-label="Menu">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
    </button>
  </header>
  <div class="layout">
    <aside class="sidebar"><nav class="sidebar__nav" aria-label="Navigation latérale">{sidebar_html}</nav></aside>
    <main class="main">{content_html}
      <footer class="footer">
        <p>Métiers Québec — Source: <a href="https://www.metiers-quebec.org" target="_blank" rel="noopener">metiers-quebec.org</a></p>
      </footer>
    </main>
  </div>
  <button class="back-to-top" id="backToTop" aria-label="Retour en haut">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="18 15 12 9 6 15"/></svg>
  </button>
  <script src="/js/search.js"></script>
</body>
</html>'''


SIDEBAR_DEFAULT = '''
<div class="sidebar__section">
  <div class="sidebar__title">Navigation</div>
  <a href="/" class="sidebar__link sidebar__link--active">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
    Accueil
  </a>
  <a href="/alpha/" class="sidebar__link">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    Index alphabétique
  </a>
  <a href="/stats/" class="sidebar__link">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
    Statistiques
  </a>
</div>
<div class="sidebar__section">
  <div class="sidebar__title">Secteurs d'emploi</div>
  <a href="/secteur/sante/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>Santé</a>
  <a href="/secteur/administration/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>Administration & Informatique</a>
  <a href="/secteur/batiment/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 20h20M5 20V8l7-5 7 5v12"/></svg>Bâtiment & Construction</a>
  <a href="/secteur/electrotechnique/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>Électrotechnique</a>
  <a href="/secteur/aerospatial/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></svg>Aérospatial</a>
  <a href="/secteur/mecanique_entr/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>Mécanique d'entretien</a>
  <a href="/secteur/enseignement/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>Éducation & Enseignement</a>
  <a href="/secteur/chimie/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>Chimie & Biologie</a>
  <a href="/secteur/metallurgie/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>Métallurgie</a>
  <a href="/secteur/protection/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>Protection publique</a>
  <a href="/secteur/transport/" class="sidebar__link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>Transport</a>
</div>
'''


class Generator:
    def __init__(self):
        self.professions = []
        self.sectors = {}
        self.load()

    def load(self):
        with open(DATA_DIR / "professions_details.json", "r") as f:
            self.professions = json.load(f)
        with open(DATA_DIR / "sectors.json", "r") as f:
            self.sectors = json.load(f)

        for p in self.professions:
            norm = {}
            for sname, content in p.get("sections", {}).items():
                key = normalize_section(sname)
                norm.setdefault(key, []).extend(content)
            p["sn"] = norm

            # Fix sector slug
            url = p.get("url_source", "")
            parts = url.strip("/").split("/")
            if len(parts) >= 2 and parts[0] != "..":
                p["secteur"] = parts[0]

        # Build slug->prof map
        self.slug_map = {p.get("slug", ""): p for p in self.professions}
        print(f"Loaded: {len(self.professions)} professions, {len(self.sectors)} sectors")

    def write(self, path, content):
        full = OUTPUT_DIR / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    def gen_profession(self, p):
        nom = p.get("nom", "")
        slug = p.get("slug", "")
        sec = p.get("secteur", "inconnu")
        sec_name = SECTOR_NAMES.get(sec, sec)
        raw_sections = p.get("sections", {})

        # Normalize section keys: lowercase, strip newlines, match to our keys
        section_key_map = {
            "description": ["description", "description"],
            "taches": ["tâches\net\nresponsabilités", "taches"],
            "milieu": ["milieu\nde\ntravail", "milieux\nde\ntravail", "milieu"],
            "qualites": ["qualités\net\naptitudes\nrequises", "qualites"],
            "marche": ["exigences\ndu\nmarché\ndu\ntravail", "marche", "marché"],
            "formation": ["formation\nrequise", "formation\nrequis", "formation"],
            "admission": ["exigences\nd'admission", "exigence\nd'admission", "admission"],
            "salaires": ["données\nsalariales", "donnée\nsalariale", "données\nsalariale", "salaires"],
            "placement": ["statistiques\nde\nplacement", "placement"],
            "perspectives": ["perspectives\nd'emploi", "perspectives"],
        }

        sn = {}
        for target_key, source_keys in section_key_map.items():
            for sk in source_keys:
                for actual_key, val in raw_sections.items():
                    if actual_key.lower().replace("\n", " ").strip() == sk.replace("\n", " ").strip():
                        sn[target_key] = val
                        break
                if target_key in sn:
                    break
            # Also try direct lowercase match
            if target_key not in sn and target_key in raw_sections:
                sn[target_key] = raw_sections[target_key]

        # Fallback: use intro as description if no DESCRIPTION key
        if "description" not in sn and "intro" in raw_sections:
            intro_val = raw_sections["intro"]
            if isinstance(intro_val, list):
                intro_text = " ".join(intro_val)
            else:
                intro_text = str(intro_val)
            # Replace newlines with spaces
            flat = intro_text.replace('\n', ' ')
            # Find where actual description starts (first sentence-like content)
            import re
            # Look for common French sentence starters
            sentence_starters = ['Quelle', 'Le ', 'La ', 'Un ', 'Une ', 'Les ', 'Des ', "L'"]
            best_pos = len(flat)
            for starter in sentence_starters:
                pos = flat.find(starter)
                if pos > 0 and pos < best_pos:
                    # Make sure it's not part of metadata (check previous char)
                    if pos == 0 or flat[pos-1] in ' .:-':
                        best_pos = pos
            if best_pos < len(flat):
                cleaned = flat[best_pos:best_pos+500]
                # End at sentence boundary
                for sep in ['. ', '? ', '! ']:
                    pos = cleaned.find(sep, 50)
                    if pos > 0:
                        cleaned = cleaned[:pos+1]
                        break
                if cleaned and len(cleaned) > 10:
                    sn["description"] = [cleaned]

        # Fallback: use intro as formation if no FORMATION key
        if "formation" not in sn and "intro" in raw_sections:
            intro_val = raw_sections["intro"]
            if isinstance(intro_val, list):
                intro_text = " ".join(intro_val)
            else:
                intro_text = str(intro_val)
            import re
            # Look for FORMATION REQUISE section in intro
            m = re.search(r'FORMATION\s+REQUISE?\s*:?\s*(.*?)(?=EXIGENCE|$)', intro_text, re.DOTALL | re.IGNORECASE)
            if m and len(m.group(1).strip()) > 10:
                sn["formation"] = [m.group(1).strip()]

        sidebar = SIDEBAR_DEFAULT + f'''
<div class="sidebar__section">
  <div class="sidebar__title">Secteur</div>
  <a href="/secteur/{he(sec)}/" class="sidebar__link">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
    {he(sec_name)}
  </a>
</div>'''

        sections_html = ""
        section_order = [
            ("description", "Description", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'),
            ("taches", "Tâches et responsabilités", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'),
            ("milieu", "Milieu de travail", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'),
            ("qualites", "Qualités et aptitudes requises", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'),
            ("marche", "Marché du travail", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'),
            ("formation", "Formation requise", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>'),
            ("admission", "Admission", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>'),
            ("salaires", "Données salariales", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'),
            ("placement", "Placement", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'),
            ("perspectives", "Perspectives d'emploi", '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'),
        ]

        # Extract education level from intro/title
        titre = p.get("titre", "")
        intro_text = " ".join(p.get("sections", {}).get("intro", [])).upper()
        niveau = ""
        if "UNIVERSITAIRE" in intro_text or "UNIVERSITAIRE" in titre.upper():
            niveau = "Universitaire"
        elif "COLLÉGIAL" in intro_text or "COLLEGIAL" in intro_text or "COLLÉGIAL" in titre.upper():
            niveau = "Collégial"
        elif "SECONDAIRE" in intro_text or "SECONDAIRE" in titre.upper():
            niveau = "Secondaire"
        elif "FORMATION PROFESSIONNELLE" in intro_text or "FORMATION PROFESSIONNELLE" in titre.upper():
            niveau = "Formation professionnelle"
        elif "D.E.C." in intro_text or "DEC" in intro_text:
            niveau = "Collégial"
        elif "B.Sc." in intro_text or "BACCALAUREAT" in intro_text:
            niveau = "Universitaire"
        else:
            niveau = "Non spécifié"

        for key, label, icon in section_order:
            content = fmt(sn.get(key, []))
            if content.strip():
                sections_html += f'\n      <div class="content-section"><h2 class="content-section__title">{icon} {label}</h2>{content}</div>'

        # Prof-meta cards
        meta_cards = f'''
      <div class="prof-meta">
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Secteur</div>
          <div class="prof-meta__card-value">{he(sec_name)}</div>
        </div>
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Niveau d'études</div>
          <div class="prof-meta__card-value">{he(niveau)}</div>
        </div>
      </div>'''

        # Extract salary info
        salaires = p.get("salaires", [])
        salary_text = ""
        if salaires:
            for row in salaires:
                row_text = " ".join(str(x) for x in row).strip()
                if "$" in row_text and any(c.isdigit() for c in row_text):
                    salary_text = row_text
                    break

        meta_cards = f'''
      <div class="prof-meta">
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Secteur</div>
          <div class="prof-meta__card-value">{he(sec_name)}</div>
        </div>
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Niveau d'études</div>
          <div class="prof-meta__card-value">{he(niveau)}</div>
        </div>
      </div>'''
        if salary_text:
            meta_cards = f'''
      <div class="prof-meta">
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Secteur</div>
          <div class="prof-meta__card-value">{he(sec_name)}</div>
        </div>
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Niveau d'études</div>
          <div class="prof-meta__card-value">{he(niveau)}</div>
        </div>
        <div class="prof-meta__card">
          <div class="prof-meta__card-label">Salaire moyen</div>
          <div class="prof-meta__card-value">{he(salary_text)}</div>
        </div>
      </div>'''

        # Page header meta line
        meta_line = ""
        if niveau and niveau != "Non spécifié":
            meta_line = f'<p class="page-header__meta">{he(niveau)}</p>'

        content = f'''
      <div class="breadcrumb">
        <a href="/">Accueil</a>
        <span class="breadcrumb__sep">/</span>
        <a href="/secteur/{he(sec)}/">{he(sec_name)}</a>
        <span class="breadcrumb__sep">/</span>
        <span>{he(nom.title())}</span>
      </div>

      <div class="page-header">
        <a href="/secteur/{he(sec)}/" class="page-header__back">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
          Retour au secteur {he(sec_name)}
        </a>
        <div class="page-header__tag">{he(sec_name)}</div>
        <h1 class="page-header__title">{he(nom.title())}</h1>
        {meta_line}
      </div>

      {meta_cards}
      {sections_html}'''

        self.write(f"metier/{slug}/index.html",
                   page_shell(f"{nom}", f"Métier {nom} au Québec", "", sidebar, content))

    def gen_sector(self, slug, name, profs):
        icon = SECTOR_ICONS.get(slug, "📋")
        sorted_p = sorted(profs, key=lambda x: x.get("nom", ""))

        items = "\n".join(
            f'<a href="/metier/{he(p.get("slug",""))}/" class="profession-item">{he(p.get("nom",""))}</a>'
            for p in sorted_p
        )

        sidebar = SIDEBAR_DEFAULT + f'''
<div class="sidebar__section">
  <div class="sidebar__title">Secteur actuel</div>
  <a href="/secteur/{he(slug)}/" class="sidebar__link sidebar__link--active">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
    {he(name)}
  </a>
</div>'''

        content = f'''
      <div class="breadcrumb">
        <a href="/">Accueil</a>
        <span class="breadcrumb__sep">/</span>
        <a href="/secteurs/">Secteurs</a>
        <span class="breadcrumb__sep">/</span>
        <span>{he(name)}</span>
      </div>

      <div class="page-header">
        <div class="page-header__tag">Secteur d'emploi</div>
        <h1 class="page-header__title">{icon} {he(name)}</h1>
        <p class="page-header__meta">{len(sorted_p)} métiers et professions dans le domaine de {he(name).lower()} au Québec</p>
      </div>

      <section class="section">
        <div class="section__header">
          <h2 class="section__title">Métiers du secteur {he(name)}</h2>
        </div>
        <div class="professions-list">{items}</div>
      </section>'''

        self.write(f"secteur/{slug}/index.html",
                   page_shell(name, f"Métiers dans le secteur {name}", "secteurs", sidebar, content))

    def gen_sectors_index(self):
        items = ""
        for slug, name in sorted(SECTOR_NAMES.items()):
            icon = SECTOR_ICONS.get(slug, "📋")
            count = len(self.sectors.get(slug, {}).get("metiers", []))
            items += f'\n      <a href="/secteur/{he(slug)}/" class="sector-card"><div class="sector-card__icon sector-card__icon--blue">{icon}</div><div><div class="sector-card__name">{he(name)}</div><div class="sector-card__count">{count} métiers</div></div></a>'

        sidebar = SIDEBAR_DEFAULT
        content = f'''
      <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="/">Accueil</a> <span>/</span> <span>Secteurs</span></nav>
      <h1 class="page-title">Secteurs d'emploi</h1>
      <p>{len(SECTOR_NAMES)} secteurs d'emploi au Québec</p>
      <div class="sectors-grid">{items}</div>'''

        self.write("secteurs/index.html",
                   page_shell("Secteurs", "Tous les secteurs d'emploi", "secteurs", sidebar, content))

    def gen_alpha(self):
        by_letter = {}
        for p in self.professions:
            nom = p.get("nom", "")
            if nom:
                L = nom[0].upper()
                if not L.isalpha():
                    L = "#"
                by_letter.setdefault(L, []).append(p)

        all_L = sorted(by_letter.keys())
        nav = " ".join(f'<a href="#L-{l}" class="letter-nav__link">{l}</a>' for l in all_L)

        sections = ""
        for L in all_L:
            items = "\n".join(
                f'<a href="/metier/{he(p.get("slug",""))}/" class="profession-item">{he(p.get("nom",""))}</a>'
                for p in sorted(by_letter[L], key=lambda x: x.get("nom", ""))
            )
            sections += f'\n    <section class="section" id="L-{L}"><h2 class="section__title">{L}</h2><div class="professions-list">{items}</div></section>'

        sidebar = SIDEBAR_DEFAULT
        content = f'''
      <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="/">Accueil</a> <span>/</span> <span>Index A-Z</span></nav>
      <h1 class="page-title">Index alphabétique</h1>
      <nav class="letter-nav">{nav}</nav>
      {sections}'''

        self.write("alpha/index.html",
                   page_shell("Index A-Z", "Index alphabétique de tous les métiers", "alpha", sidebar, content))

    def gen_search_data(self):
        data = []
        for p in self.professions:
            data.append({
                "nom": p.get("nom", ""),
                "slug": p.get("slug", ""),
                "secteur": p.get("secteur", ""),
                "secteur_nom": SECTOR_NAMES.get(p.get("secteur", ""), ""),
            })
        self.write("data/search.json", json.dumps(data, ensure_ascii=False))

    def gen_homepage(self):
        sector_cards = ""
        sorted_sectors = sorted(SECTOR_NAMES.items())
        for slug, name in sorted_sectors[:12]:
            icon = SECTOR_ICONS.get(slug, "📋")
            count = len(self.sectors.get(slug, {}).get("metiers", []))
            sector_cards += f'\n          <a href="/secteur/{he(slug)}/" class="sector-card"><div class="sector-card__icon sector-card__icon--blue">{icon}</div><div><div class="sector-card__name">{he(name)}</div><div class="sector-card__count">{count} métiers</div></div></a>'

        sidebar = SIDEBAR_DEFAULT
        content = f'''
      <section class="hero">
        <div class="hero__badge">Guide des carrières au Québec</div>
        <h1 class="hero__title">Découvre ta <span>futur<span>e</span> carrière</span></h1>
        <p class="hero__subtitle">Plus de 1 500 métiers et professions répartis dans 32 secteurs d'emploi. Salaires, formations, perspectives d'emploi et bien plus.</p>
        <div class="hero__search">
          <svg class="hero__search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input type="text" id="heroSearch" placeholder="Recherche un métier, ex: infirmier, informaticien..." autocomplete="off">
          <div class="search-results" id="heroSearchResults"></div>
        </div>
      </section>
      <section class="stats">
        <div class="stat-card">
          <div class="stat-card__number">{len(self.professions)}</div>
          <div class="stat-card__label">Métiers répertoriés</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__number">{len(SECTOR_NAMES)}</div>
          <div class="stat-card__label">Secteurs d'emploi</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__number">460+</div>
          <div class="stat-card__label">Programmes d'études</div>
        </div>
      </section>
      <section class="section">
        <div class="section__header">
          <h2 class="section__title">Secteurs d'emploi</h2>
          <a href="/secteurs/" class="section__link">Voir tous les secteurs →</a>
        </div>
        <div class="sectors-grid">{sector_cards}</div>
      </section>
      <section class="section">
        <div class="section__header"><h2 class="section__title">Navigation</h2></div>
        <div class="sectors-grid">
          <a href="/secteurs/" class="sector-card"><div class="sector-card__icon sector-card__icon--blue">🗂️</div><div><div class="sector-card__name">Par secteur</div><div class="sector-card__count">{len(SECTOR_NAMES)} secteurs</div></div></a>
          <a href="/alpha/" class="sector-card"><div class="sector-card__icon sector-card__icon--green">🔤</div><div><div class="sector-card__name">Index alphabétique</div><div class="sector-card__count">{len(self.professions)} métiers</div></div></a>
        </div>
      </section>'''

        self.write("index.html",
                   page_shell("Accueil", "Portail des métiers du Québec", "home", sidebar, content))

    def run(self):
        print("Generating site...")
        self.gen_homepage()
        self.gen_sectors_index()
        self.gen_alpha()
        self.gen_search_data()

        # Group professions by sector for sector pages
        by_sector = {}
        for p in self.professions:
            sec = p.get("secteur", "inconnu")
            by_sector.setdefault(sec, []).append(p)

        for slug, name in SECTOR_NAMES.items():
            profs = by_sector.get(slug, [])
            if profs:
                self.gen_sector(slug, name, profs)

        count = 0
        for p in self.professions:
            self.gen_profession(p)
            count += 1
            if count % 100 == 0:
                print(f"  {count}/{len(self.professions)} pages...")

        print(f"Done! {count + len(SECTOR_NAMES) + 3} pages generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    Generator().run()
