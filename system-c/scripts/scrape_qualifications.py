#!/usr/bin/env python3
"""Scrape qualificationsquebec.com for all CNP×appellations data via AJAX API."""

import json
import os
import re
import sys
import time
import urllib.request

BASE_URL = "https://qualificationsquebec.com"
AJAX_URL = BASE_URL + "/ajax/professions"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reference")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "cnp-appellations-officielles.json")

TARGET_CNPS = ["31301", "72300", "21222", "64100", "12200"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SystemC-Research/1.0)",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_all_professions():
    """Fetch all professions in one AJAX call with limit=600."""
    print("Fetching all professions via AJAX endpoint...")
    data = "limit=600&pg=1".encode()
    req = urllib.request.Request(AJAX_URL, data=data, headers=HEADERS, method="POST")
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode("utf-8"))
    html = result["html"]

    pattern = r'href="/profession/([^"]+)"[^>]*>.*?<p class="title">(.*?)</p>.*?<p class="cnp">CNP\s+(\d{5})</p>'
    items = re.findall(pattern, html, re.DOTALL)

    professions = []
    for slug, title, cnp in items:
        title = re.sub(r"<[^>]+>", "", title).strip()
        professions.append({"slug": slug, "appellation": title, "cnp": cnp})

    print(f"  Total professions: {len(professions)}")
    print(f"  Unique CNPs: {len(set(p['cnp'] for p in professions))}")
    return professions


def fetch_profession_page(slug):
    """Fetch a single profession page and extract 'Autres appellations d'emplois'."""
    url = f"{BASE_URL}/profession/{slug}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SystemC-Research/1.0)"})
    resp = urllib.request.urlopen(req, timeout=30)
    html = resp.read().decode("utf-8")

    appellations = []
    m = re.search(
        r"Autres appellations d.emplois.*?<ul[^>]*>(.*?)</ul>",
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        items = re.findall(r"<li[^>]*>(.*?)</li>", m.group(1), re.DOTALL)
        for item in items:
            clean = re.sub(r"<[^>]+>", "", item).strip()
            if clean:
                appellations.append(clean)
    return appellations


def main():
    professions = fetch_all_professions()

    # Build the basic matrix first (all 550 professions with appellation_principale)
    by_cnp = {}
    for p in professions:
        cnp = p["cnp"]
        if cnp not in by_cnp:
            by_cnp[cnp] = {
                "cnp": cnp,
                "appellation_principale": p["appellation"],
                "slug": p["slug"],
                "autres_appellations": [],
            }

    # Fetch detailed pages for target CNPs
    print("\nFetching individual pages for target CNPs...")
    target_professions = {p["cnp"]: p for p in professions if p["cnp"] in TARGET_CNPS}
    for cnp, prof in target_professions.items():
        print(f"  CNP {cnp}: {prof['slug']}...")
        try:
            other = fetch_profession_page(prof["slug"])
            by_cnp[cnp]["autres_appellations"] = other
            print(f"    → {len(other)} autres appellations")
        except Exception as e:
            print(f"    FAILED: {e}")
        time.sleep(0.5)

    # Build final matrix
    matrix = {
        "source": "https://qualificationsquebec.com",
        "description": "Matrice officielle CNP × appellations d'emplois (Québec). Appellation principale = titre officiel sur qualificationsquebec.com. Autres appellations = liste verbatim de la page individuelle (section 'Autres appellations d'emplois').",
        "total_professions": len(by_cnp),
        "professions": by_cnp,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {OUTPUT_FILE}")
    print(f"Total CNP codes: {len(by_cnp)}")
    with_others = sum(1 for p in by_cnp.values() if p["autres_appellations"])
    print(f"  with autres appellations: {with_others}")


if __name__ == "__main__":
    main()
