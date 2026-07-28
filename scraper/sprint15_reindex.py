#!/usr/bin/env python3
"""
Sprint 1.5 : Re-scanner l'index live, scraper les pages vraiment manquantes.
Contourne les erreurs d'extension/répertoire de urls-manquantes-86.json.
"""

import json
import os
import re
import sys
import time
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urljoin

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
SCRAPER_DIR = os.path.join(ROOT, "scraper")
sys.path.insert(0, SCRAPER_DIR)
from scrape_v2 import SimpleFetcher, ProfessionParserV2

BASE_URL = "https://www.metiers-quebec.org"

EXCLUDE = {
    "../programmes/programmes.htm",
    "../index.html",
    "../accueil.html",
}


def fetch_live_index(fetcher):
    letters = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "jk",
        "l", "m", "n", "o", "p", "qr", "s", "t", "uv", "wxyz"
    ]
    all_links = defaultdict(list)
    for letter in letters:
        path = f"/alphabetique/{letter}.htm"
        html = fetcher.fetch(path)
        if not html:
            continue
        parser = HTMLParser()
        links = []
        # Simple inline link extraction
        for m in re.finditer(r'<a\s+[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE):
            href, text = m.groups()
            text = re.sub(r'<[^>]+>', '', text).strip()
            if (text and len(text) > 3
                and not text.lower().startswith("retour")
                and not any(x in href.lower() for x in ["accueil", "cadre", "alphabetique", "programmes", "javascript", "#", ".pdf", "portrait"])):
                links.append((href, text))
        for href, text in links:
            if not href.startswith("/"):
                href = f"/{href}"
            # Normalize: keep canonical path (strip /../)
            canonical = re.sub(r'^/(\.\./)+', '', href)
            if text not in all_links[canonical]:
                all_links[canonical].append(text)
    return dict(all_links)


def check_accessible(fetcher, canonical_path, max_attempts=3):
    """Try various URL forms to find the page."""
    variants = [
        f"../{canonical_path}",
        f"/../{canonical_path}",
        canonical_path,
    ]
    # Try alternative extensions
    base, ext = os.path.splitext(canonical_path)
    alt_ext = ".html" if ext == ".htm" else ".htm"
    parts = canonical_path.split("/")
    # For restau_tour/foo.htm, try restau_tourisme/foo.htm
    dir_aliases = {
        "restau_tour": "restau_tourisme",
        "fabric_mecanique": "fabric_mec",
        "mecanique_entretien": "mecanique_entr",
    }
    dir_aliases_rev = {v: k for k, v in dir_aliases.items()}
    for attempt in range(max_attempts):
        for variant in variants:
            html = fetcher.fetch(variant)
            if html:
                return variant, html
        # Try other extension
        alt_path = f"{base}{alt_ext}"
        for v in [f"../{alt_path}", f"/../{alt_path}"]:
            html = fetcher.fetch(v)
            if html:
                return v, html
        # Try dir alias
        if len(parts) >= 2:
            sector = parts[0]
            rest = "/".join(parts[1:])
            for s in [sector, dir_aliases.get(sector), dir_aliases_rev.get(sector)]:
                if s and s != sector:
                    alt = f"{s}/{rest}"
                    for v in [f"../{alt}", f"/../{alt}"]:
                        html = fetcher.fetch(v)
                        if html:
                            return v, html
                    # Also try with alt ext
                    alt2 = f"{s}/{base.split('/')[-1]}{alt_ext}"
                    for v in [f"../{alt2}", f"/../{alt2}"]:
                        html = fetcher.fetch(v)
                        if html:
                            return v, html
        break  # Only try once per path
    return None, None


def main():
    print("=" * 60)
    print("SPRINT 1.5 — Re-indexation live + scraping manquants")
    print("=" * 60)

    fetcher = SimpleFetcher(base_url=BASE_URL, delay=0.3)

    # 1. Scrape live index
    print("\n=== Index live ===")
    live = fetch_live_index(fetcher)
    print(f"URLs uniques dans l'index live : {len(live)}")

    # 2. Load existing corpus
    details_path = os.path.join(DATA_DIR, "professions_details.json")
    with open(details_path) as f:
        existing = json.load(f)
    existing_canonical = set()
    for e in existing:
        u = e.get("url_source", "")
        c = re.sub(r'^/(\.\./)+', '', u)
        # Also normalize extension
        c_norm = re.sub(r'\.html?$', '', c)
        existing_canonical.add(c_norm)
    print(f"Fiches existantes : {len(existing)}")

    # 3. Find truly missing and check accessibility
    print("\n=== Pages manquantes et accessibilité ===")
    accessible = {}
    dead = {}
    already_have = 0

    for canonical, names in sorted(live.items()):
        if canonical in EXCLUDE or f"../{canonical}" in EXCLUDE:
            already_have += 1
        c_norm = re.sub(r'\.html?$', '', canonical)
        if c_norm in existing_canonical:
            already_have += 1
        else:
            found_path, html = check_accessible(fetcher, canonical)
            if found_path:
                accessible[canonical] = {"path": found_path, "names": names}
                print(f"  OK  {canonical:55s} -> {found_path}")
            else:
                dead[canonical] = names
                print(f"  DEAD {canonical:55s}")

    print(f"\nDéjà dans corpus : {already_have}")
    print(f"Accessibles : {len(accessible)}")
    print(f"Morts (404/timeout) : {len(dead)}")

    # 4. Scrape accessible pages
    print("\n=== Scraping ===")
    new_entries = []
    scrape_errors = []

    for canonical, info in sorted(accessible.items()):
        found_path = info["path"]
        names = info["names"]
        html = fetcher.fetch(found_path)
        if not html:
            scrape_errors.append({"canonical": canonical, "raison": "fetch failed"})
            continue

        parser = ProfessionParserV2()
        try:
            parser.feed(html)
        except Exception as e:
            scrape_errors.append({"canonical": canonical, "raison": f"parse: {e}"})
            continue

        sections = parser.parse_sections()
        salaries = parser.extract_salary_data()
        links = parser.extract_links()

        title = ""
        for part in parser.text_parts[:20]:
            part = part.strip()
            if part and len(part) > 5 and "NIVEAU" in part.upper():
                title = part
                break

        parts = canonical.strip("/").split("/")
        sector = parts[0] if len(parts) >= 2 else "inconnu"
        base_slug = canonical.split("/")[-1].replace(".htm", "").replace(".html", "")

        entry = {
            "nom": names[0],
            "noms": names,
            "slug": base_slug,
            "url_source": f"/../{canonical}",
            "secteur": sector,
            "titre": title,
            "sections": sections,
            "salaires": salaries,
            "liens": links[:5],
            "page_groupee": len(names) > 1,
        }
        new_entries.append(entry)
        n_sec = len(sections)
        n_sal = len(salaries)
        print(f"  [OK] {canonical:55s} -> {n_sec} sections, {n_sal} salaires [{sector}]")

    print(f"\nScrapés avec succès : {len(new_entries)}")
    for e in scrape_errors:
        print(f"  [ERR] {e['canonical']}: {e['raison']}")

    # 5. Merge
    print("\n=== Fusion ===")
    existing_urls = {e.get("url_source") for e in existing}
    new_urls = {e.get("url_source") for e in new_entries}
    overlap = existing_urls & new_urls
    if overlap:
        print(f"  [AVERTISSEMENT] {len(overlap)} URLs déjà présentes : {overlap}")
    merged = existing + new_entries
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Fusion : {len(existing)} -> {len(merged)} fiches")
    with open(os.path.join(DATA_DIR, "professions_details.new.json"), "w", encoding="utf-8") as f:
        json.dump(new_entries, f, ensure_ascii=False, indent=2)
    print(f"Nouvelles sauvegardées séparément")

    # 6. Audit
    audit = {
        "index_live_urls": len(live),
        "corpus_avant": len(existing),
        "deja_presents": already_have,
        "accessibles": {k: {"path": v["path"], "noms": len(v["names"])} for k, v in accessible.items()},
        "morts": dict(dead),
        "scrapes_reussis": len(new_entries),
        "scrapes_erreurs": scrape_errors,
        "corpus_apres": len(merged),
    }
    audit_path = os.path.join(ROOT, "docs", "audit-sprint1-5-fiches-manquantes.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    print(f"\nAudit : {audit_path}")

    # 7. Doc audit
    lines = []
    lines.append("# Audit Sprint 1.5 — Fiches manquantes\n")
    lines.append(f"Date : {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"\n## Résumé")
    lines.append(f"\n- Index live : {len(live)} URLs uniques")
    lines.append(f"- Corpus avant : {len(existing)} fiches")
    lines.append(f"- Déjà présents (normalisé) : {already_have}")
    lines.append(f"- Accessibles (HTTP 200) : {len(accessible)}")
    lines.append(f"- Morts (404/timeout) : {len(dead)}")
    lines.append(f"- Scrapés avec succès : {len(new_entries)}")
    lines.append(f"- Corpus après : {len(merged)} fiches\n")
    lines.append(f"## Pages scrapées ({len(new_entries)})\n")
    for e in new_entries:
        lines.append(f"- {e['url_source']} : {len(e['sections'])} sections, {len(e['salaires'])} salaires")
    lines.append(f"\n## Pages mortes ({len(dead)})\n")
    for url, names in sorted(dead.items()):
        n = ", ".join(names[:3])
        lines.append(f"- {url} ({n})")
    lines.append(f"\n## Erreurs de scraping\n")
    for e in scrape_errors:
        lines.append(f"- {e['canonical']}: {e['raison']}")
    lines.append(f"\n## Faux-positifs exclus\n")
    lines.append(f"- `programmes/programmes.htm` : lien navigation générique (confirmé exclu)")
    lines.append(f"- `index.html` : non présent dans l'index live")

    doc_path = os.path.join(ROOT, "docs", "audit-sprint1-5-fiches-manquantes.md")
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Doc audit : {doc_path}")


if __name__ == "__main__":
    main()
