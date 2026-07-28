#!/usr/bin/env python3
"""
Scraping Jobboom + Emploisdecadres via Playwright (headless Chromium).
5 métiers × 2 sites → jusqu'à 3 offres par métier/site.
Sortie : system-c/data/raw-comparaison/offres/{cnp}.json
  clés "jobboom" et "emploisdecadres" ajoutées sans écraser "jobillico".

Technique Jobboom : utiliser l'URL _lfrk (résultats réels) et non _lfr (sponsorisés).
La mécanique : charger la page de recherche, remplir le formulaire, attendre la
redirection vers /fr/emploi/{slug}/_lfrk, puis extraire les data-url des job cards.
"""

import json
import os
import time
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Configuration ────────────────────────────────────────────────────────────

METIERS = [
    {"cnp": "31301", "nom": "infirmière",             "terme": "infirmière"},
    {"cnp": "73200", "nom": "plombier",               "terme": "plombier"},
    {"cnp": "21211", "nom": "analyste informatique",  "terme": "analyste informatique"},
    {"cnp": "64100", "nom": "vendeur détail",         "terme": "vendeur"},
    {"cnp": "14200", "nom": "technicien comptabilité","terme": "technicien comptabilité"},
]

OUT_DIR = Path(__file__).parent.parent / "data" / "raw-comparaison" / "offres"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_OFFRES = 3
TIMEOUT = 25_000  # ms

CHROMIUM = "/run/current-system/sw/bin/chromium"


# ── Helpers ──────────────────────────────────────────────────────────────────

def charger_existant(cnp: str) -> dict:
    path = OUT_DIR / f"{cnp}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"cnp": cnp}


def sauvegarder(cnp: str, data: dict):
    path = OUT_DIR / f"{cnp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → {path.name}")


def texte_propre(s: str) -> str:
    return re.sub(r'\s+', ' ', s or "").strip()


def slugify(s: str) -> str:
    """Convertit "analyste informatique" → "analyste-informatique"."""
    # Normaliser les accents
    nfkd = unicodedata.normalize('NFKD', s)
    ascii_str = nfkd.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', ascii_str.lower()).strip('-')


# ── Jobboom ──────────────────────────────────────────────────────────────────

def search_jobboom(page, terme: str) -> list[str]:
    """Retourne une liste d'URLs d'offres pour le terme donné."""
    # Charger la page de recherche vierge
    try:
        page.goto("https://www.jobboom.com/fr/emploi/_lfr",
                  wait_until="domcontentloaded", timeout=TIMEOUT)
    except PWTimeout:
        print(f"    [jobboom] Timeout chargement page de recherche")
        return []

    # Remplir le champ keyword et soumettre
    kw = page.query_selector("input[name='keyword']")
    if not kw:
        print(f"    [jobboom] Champ keyword introuvable")
        return []

    kw.fill("")
    time.sleep(0.2)
    kw.fill(terme)
    time.sleep(0.3)
    kw.press("Enter")

    # Attendre la navigation vers la page _lfrk
    try:
        page.wait_for_load_state("networkidle", timeout=TIMEOUT)
        time.sleep(2)
    except PWTimeout:
        print(f"    [jobboom] Timeout après soumission recherche")

    body = page.content()
    current_url = page.url
    print(f"    [jobboom] URL résultats: {current_url[:80]}")

    # Extraire les data-url des cards de job
    data_urls = re.findall(r'data-url="(/fr/offre-emploi/[^"]+)"', body)
    return data_urls


def get_jobboom_offre(page, path: str) -> dict | None:
    """Charge une page d'offre et extrait le texte des tâches."""
    full_url = f"https://www.jobboom.com{path}"
    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=TIMEOUT)
        time.sleep(1)
    except PWTimeout:
        return None
    except Exception as e:
        print(f"    [jobboom] Erreur offre: {e}")
        return None

    # Jobboom : utiliser le sélecteur spécifique du titre (pas h1 générique qui capte
    # la modale "Voulez-vous quitter ce processus?")
    titre = ""
    for sel_titre in [".jobDescHeaderTitle", "h1[data-test-id='job-title']",
                       "h1.jobDescHeaderTitle"]:
        el = page.query_selector(sel_titre)
        if el:
            titre = texte_propre(el.text_content() or "")
            if titre:
                break

    # Fallback sur la deuxième h1 si le sélecteur spécifique ne marche pas
    if not titre:
        h1s = page.query_selector_all("h1")
        for h1 in h1s:
            t = texte_propre(h1.text_content() or "")
            if t and "quitter" not in t.lower() and len(t) > 5:
                titre = t
                break

    if not titre or titre.lower() in ("404", ""):
        return None

    # Description du poste
    taches_raw = ""
    for sel in ["#job-description", ".jobDescMainDesc", "#job-content",
                 "[data-test-id='job-description']"]:
        el = page.query_selector(sel)
        if el:
            t = texte_propre(el.inner_text() or "")
            if len(t) > len(taches_raw):
                taches_raw = t
        if len(taches_raw) > 100:
            break

    return {
        "titre": titre,
        "url": full_url,
        "taches_verbatim": taches_raw[:3000],
    }


def scrape_jobboom(page, metier: dict) -> list[dict]:
    terme = metier["terme"]
    nom = metier["nom"]
    print(f"  Jobboom → '{terme}'")

    data_urls = search_jobboom(page, terme)
    if not data_urls:
        print(f"    [jobboom] 0 URL trouvé")
        return []

    print(f"    [jobboom] {len(data_urls)} candidats trouvés")

    offres = []
    for path in data_urls:
        if len(offres) >= MAX_OFFRES:
            break
        offre = get_jobboom_offre(page, path)
        if offre:
            offres.append(offre)
            print(f"    [jobboom] ✓ {offre['titre'][:55]}")
        time.sleep(0.8)

    return offres


# ── Emploisdecadres ──────────────────────────────────────────────────────────

def scrape_emploisdecadres(page, metier: dict) -> list[dict]:
    terme = metier["terme"]
    nom = metier["nom"]
    print(f"  Emploisdecadres → '{terme}'")

    encoded = quote(terme)
    url = f"https://www.emploisdecadres.com/fr/emplois?motcle={encoded}&province=QC"
    offres = []

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)
        time.sleep(2)
        content = page.content()

        if any(k in content.lower() for k in ["cloudflare", "just a moment", "challenge"]):
            print(f"    [emploisdecadres] Cloudflare détecté — abandon (conforme aux instructions)")
            return offres

        page.wait_for_selector("a[href], .job-card, article, h2, h3", timeout=TIMEOUT)
    except PWTimeout:
        try:
            c = page.content()
            if any(k in c.lower() for k in ["cloudflare", "just a moment"]):
                print(f"    [emploisdecadres] Cloudflare confirmé après timeout — abandon")
            else:
                print(f"    [emploisdecadres] Timeout liste (pas de résultats visibles)")
        except Exception:
            pass
        return offres
    except Exception as e:
        print(f"    [emploisdecadres] Erreur liste: {e}")
        return offres

    # Extraire les liens d'offres
    liens = page.query_selector_all("a[href*='/fr/emploi/'], a[href*='/offre/'], a[href*='/job/']")
    hrefs = []
    for l in liens:
        href = l.get_attribute("href") or ""
        if href and href not in hrefs:
            hrefs.append(href)

    hrefs_uniq = list(dict.fromkeys(hrefs))[:MAX_OFFRES * 3]
    if not hrefs_uniq:
        print(f"    [emploisdecadres] 0 lien trouvé")
        return offres

    for href in hrefs_uniq:
        if len(offres) >= MAX_OFFRES:
            break
        full_url = href if href.startswith("http") else f"https://www.emploisdecadres.com{href}"
        try:
            page.goto(full_url, wait_until="domcontentloaded", timeout=TIMEOUT)
            c = page.content()
            if any(k in c.lower() for k in ["cloudflare", "just a moment"]):
                print(f"    [emploisdecadres] Cloudflare sur offre — abandon")
                break
            page.wait_for_selector("h1", timeout=10_000)
        except PWTimeout:
            continue
        except Exception as e:
            continue

        titre = texte_propre(page.text_content("h1") or "")
        if not titre:
            continue

        taches_raw = ""
        for sel in ["[class*='description']", "section", "article", ".job-description"]:
            el = page.query_selector(sel)
            if el:
                t = texte_propre(el.inner_text() or "")
                if len(t) > len(taches_raw):
                    taches_raw = t
            if len(taches_raw) > 200:
                break

        offres.append({
            "titre": titre,
            "url": full_url,
            "taches_verbatim": taches_raw[:3000],
        })
        print(f"    [emploisdecadres] ✓ {titre[:55]}")
        time.sleep(1)

    return offres


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    rapport = {"tentatives": 0, "succes": 0, "echecs": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="fr-CA",
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = ctx.new_page()

        for metier in METIERS:
            cnp = metier["cnp"]
            nom = metier["nom"]
            print(f"\n── {nom.upper()} (CNP {cnp}) ──")

            data = charger_existant(cnp)
            data.setdefault("cnp", cnp)
            data.setdefault("nom", nom)

            # ── Jobboom ──
            rapport["tentatives"] += 1
            jb = scrape_jobboom(page, metier)
            if jb:
                data["jobboom"] = {"offres": jb, "nb": len(jb)}
                rapport["succes"] += 1
                print(f"  Jobboom : {len(jb)} offre(s)")
            else:
                data["jobboom"] = {"offres": [], "nb": 0, "echec": True,
                                   "cause": "0 offre extrait"}
                rapport["echecs"].append(f"jobboom/{nom}")
                print(f"  Jobboom : 0 offre")

            # ── Emploisdecadres ──
            rapport["tentatives"] += 1
            ed = scrape_emploisdecadres(page, metier)
            if ed:
                data["emploisdecadres"] = {"offres": ed, "nb": len(ed)}
                rapport["succes"] += 1
                print(f"  Emploisdecadres : {len(ed)} offre(s)")
            else:
                data["emploisdecadres"] = {
                    "offres": [], "nb": 0, "echec": True,
                    "cause": "Cloudflare ou 0 offre",
                }
                rapport["echecs"].append(f"emploisdecadres/{nom}")
                print(f"  Emploisdecadres : 0 offre")

            sauvegarder(cnp, data)

        browser.close()

    print("\n\n═══ RAPPORT FINAL ═══")
    print(f"Tentatives : {rapport['tentatives']}")
    print(f"Succès     : {rapport['succes']}")
    pct = 100 * rapport["succes"] // rapport["tentatives"] if rapport["tentatives"] else 0
    print(f"Taux réel  : {rapport['succes']}/{rapport['tentatives']} ({pct}%)")
    if rapport["echecs"]:
        print("Échecs :")
        for e in rapport["echecs"]:
            print(f"  - {e}")
    else:
        print("Aucun échec.")


if __name__ == "__main__":
    main()
