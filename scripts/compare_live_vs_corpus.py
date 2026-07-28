#!/usr/bin/env python3
"""
Extraction brute et classification des diffs entre le site live metiers-quebec.org
et le snapshot corpus_raw_v2/.

Sortie : data/reference/migration-sens-structure/metiers-quebec-diffs.json
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

BASE_URL = "https://www.metiers-quebec.org"
CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "corpus_raw_v2")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reference", "migration-sens-structure")
DELAY = 0.3


def detect_encoding(raw_bytes):
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return 'utf-16'
    try:
        text = raw_bytes.decode('utf-8')
        if any(c in text for c in 'àâäéèêëïîôùûüÿçœæ'):
            return 'utf-8'
    except (UnicodeDecodeError, ValueError):
        pass
    text_1252 = raw_bytes.decode('windows-1252', errors='replace')
    utf8_indicators = ['â€™', 'â€"', 'â€œ', 'Ã©', 'Ã¨', 'Ã ', 'Ã§', 'Ã®', 'dâ€™']
    for indicator in utf8_indicators:
        if indicator in text_1252:
            try:
                fixed = text_1252.encode('windows-1252', errors='replace').decode('utf-8', errors='replace')
                if fixed != text_1252:
                    return 'utf-8-as-1252'
            except Exception:
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
                    html = raw.decode('windows-1252', errors='replace')
                    try:
                        html = html.encode('windows-1252', errors='replace').decode('utf-8', errors='replace')
                    except Exception:
                        pass
                else:
                    html = raw.decode(enc, errors="replace")
                self.request_count += 1
                if self.request_count % 50 == 0:
                    print(f"  [INFO] {self.request_count} requêtes...", flush=True)
                time.sleep(self.delay)
                return html
        except urllib.error.HTTPError as e:
            return None
        except Exception as e:
            return None


class ProfessionParserV2(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.current_tag = None
        self.tag_stack = []
        self.skip_tags = {"script", "style", "head"}
        self.in_skip = 0

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        if tag in self.skip_tags:
            self.in_skip += 1
            return
        if tag == "br":
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
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_skip > 0:
            return
        text = data.strip()
        if text:
            self.text_parts.append(data)

    def get_full_text(self):
        return "\n".join("".join(self.text_parts).split())

    def parse_sections(self):
        full_text = self.get_full_text()

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

        parts = re.split(r"(" + "|".join(section_patterns) + r")", full_text, flags=re.IGNORECASE)

        for part in parts:
            if part is None:
                continue
            part = part.strip()
            if not part:
                continue
            matched = False
            for pattern in section_patterns:
                if re.match(pattern, part, re.IGNORECASE):
                    current_section = part.upper().strip()
                    sections[current_section] = ""
                    matched = True
                    break
            if not matched and current_section:
                if part and len(part) > 3:
                    existing = sections.get(current_section, "")
                    if existing:
                        sections[current_section] = existing + "\n" + part
                    else:
                        sections[current_section] = part
        return sections


def normalize_key(key):
    """Normalise une clé de section pour comparaison : minuscules, sans sauts de ligne, sans accents."""
    n = key.lower().strip()
    n = re.sub(r'\s+', ' ', n)
    n = re.sub(r'[^a-z0-9 ]', '', n)
    return n.strip()

def key_display(k):
    """Affiche une clé en remplaçant les \n par des espaces pour lisibilité."""
    return k.replace('\n', ' ').strip()


def load_corpus():
    """Charge toutes les fiches corpus_raw_v2."""
    fiches = {}
    if not os.path.isdir(CORPUS_DIR):
        print(f"[ERREUR] Répertoire corpus introuvable : {CORPUS_DIR}")
        return fiches
    for fname in os.listdir(CORPUS_DIR):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(CORPUS_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            slug = data.get('slug', fname.replace('.json', ''))
            fiches[slug] = data
        except (json.JSONDecodeError, IOError) as e:
            print(f"  [ERREUR] Lecture {fname}: {e}")
    return fiches


def classify_diff(corpus_key, live_key):
    """Détermine si un changement est structurel ou sémantique.
    
    structural : ajout/suppression/renommage de champ
    sémantique  : reformulation dans un champ existant
    """
    if corpus_key is None and live_key is not None:
        return "structure", f"section ajoutée côté live: '{live_key}'"
    if corpus_key is not None and live_key is None:
        return "structure", f"section supprimée côté live: '{corpus_key}'"
    if corpus_key is not None and live_key is not None and corpus_key != live_key:
        return "structure", f"clé renommée: '{corpus_key}' -> '{live_key}'"
    return None, None


def text_similarity(a, b):
    """Compare deux textes et retourne un score de similarité simple (0-1)."""
    if not a or not b:
        return 0.0
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0.0
    intersection = a_words & b_words
    union = a_words | b_words
    return len(intersection) / len(union)


def main():
    print("=" * 60)
    print("EXTRACTION BRUTE : live metiers-quebec.org vs corpus_raw_v2")
    print("=" * 60)
    print()

    # Charger le corpus existant
    print("=== Chargement du corpus ===")
    corpus = load_corpus()
    print(f"  {len(corpus)} fiches chargées\n")

    if not corpus:
        print("[ERREUR] Aucune fiche chargée. Arrêt.")
        sys.exit(1)

    fetcher = SimpleFetcher()

    # Préparer les slugs à traiter (tous ceux du corpus)
    slugs = sorted(corpus.keys())

    all_diffs = {}
    stats = {
        "total_fiches": len(slugs),
        "scraped_ok": 0,
        "scraped_fail": 0,
        "structural_changes": 0,
        "semantic_changes": 0,
        "fiches_with_changes": 0,
        "fiches_unchanged": 0,
        "structural_only": 0,
        "semantic_only": 0,
        "both_types": 0,
    }

    print(f"=== Scraping et comparaison ({len(slugs)} fiches) ===")
    for idx, slug in enumerate(slugs):
        if (idx + 1) % 50 == 0:
            print(f"  Progression : {idx + 1}/{len(slugs)}", flush=True)

        corpus_fiche = corpus[slug]
        source_url = corpus_fiche.get("source_url", f"/../{corpus_fiche.get('secteur', 'inconnu')}/{slug}.htm")

        # Scraper la page live
        html = fetcher.fetch(source_url)
        if not html:
            # Essayer quelques variantes d'URL
            secteur = corpus_fiche.get("secteur", "")
            for variant in [f"/{secteur}/{slug}.htm", f"/{secteur}/{slug}.html"]:
                html = fetcher.fetch(variant)
                if html:
                    break
        if not html:
            stats["scraped_fail"] += 1
            all_diffs[slug] = {
                "nom": corpus_fiche.get("nom", slug),
                "error": "HTTP échec ou page introuvable",
                "source_url": source_url,
            }
            continue

        stats["scraped_ok"] += 1

        # Parser la page live
        parser = ProfessionParserV2()
        try:
            parser.feed(html)
        except Exception as e:
            all_diffs[slug] = {
                "nom": corpus_fiche.get("nom", slug),
                "error": f"Parse error: {e}",
                "source_url": source_url,
            }
            continue

        live_sections = parser.parse_sections()
        corpus_sections = corpus_fiche.get("sections_raw", {})

        # Comparer les sections
        # Indexer les sections du corpus par clé normalisée
        corpus_by_norm = {}
        for k, v in corpus_sections.items():
            nk = normalize_key(k)
            if nk not in corpus_by_norm:
                corpus_by_norm[nk] = []
            corpus_by_norm[nk].append((k, v))

        # Indexer les sections live par clé normalisée
        live_by_norm = {}
        for k, v in live_sections.items():
            nk = normalize_key(k)
            if nk not in live_by_norm:
                live_by_norm[nk] = []
            live_by_norm[nk].append((k, v))

        diffs = {
            "slug": slug,
            "nom": corpus_fiche.get("nom", slug),
            "source_url": source_url,
            "structural": [],
            "semantic": [],
            "indetermine": [],
        }

        # Vérifier les clés du corpus qui n'existent pas ou diffèrent dans le live
        all_norm_keys = set(list(corpus_by_norm.keys()) + list(live_by_norm.keys()))

        fiche_has_structural = False
        fiche_has_semantic = False

        for nk in sorted(all_norm_keys):
            corpus_entries = corpus_by_norm.get(nk, [])
            live_entries = live_by_norm.get(nk, [])

            if not live_entries:
                # Section présente dans corpus mais absente du live
                for ck, cv in corpus_entries:
                    dtype, desc = classify_diff(key_display(ck), None)
                    diffs["structural"].append({"type": dtype, "description": desc, "key": key_display(ck), "old_value_preview": cv[:200] if cv else ""})
                    fiche_has_structural = True
                continue

            if not corpus_entries:
                # Section présente dans live mais absente du corpus
                for lk, lv in live_entries:
                    dtype, desc = classify_diff(None, key_display(lk))
                    diffs["structural"].append({"type": dtype, "description": desc, "key": key_display(lk), "new_value_preview": lv[:200] if lv else ""})
                    fiche_has_structural = True
                continue

            # La section existe dans les deux — comparer les valeurs textuelles
            # Utiliser la paire la mieux appariée (première entrée de chaque côté)
            ck, cv = corpus_entries[0]
            lk, lv = live_entries[0]
            
            # Vérifier si la clé normalisée diffère (véritable renommage, pas juste \n vs espace)
            ck_norm = normalize_key(ck)
            lk_norm = normalize_key(lk)
            if ck_norm != lk_norm:
                dtype, desc = classify_diff(key_display(ck), key_display(lk))
                diffs["structural"].append({"type": dtype, "description": desc, "key_corpus": key_display(ck), "key_live": key_display(lk)})
                fiche_has_structural = True
            
            # Comparer le contenu textuel
            sim = text_similarity(cv, lv)
            if sim < 0.95:
                diffs["semantic"].append({
                    "type": "semantique",
                    "description": f"reformulation dans section '{key_display(lk)}'",
                    "key": key_display(lk),
                    "similarity": round(sim, 4),
                    "old_preview": cv[:300] if cv else "",
                    "new_preview": lv[:300] if lv else "",
                })
                fiche_has_semantic = True

        # Nettoyer les doublons sémantiques (même clé, on garde le plus bas similarity)
        seen_keys = {}
        cleaned_semantic = []
        for d in diffs["semantic"]:
            k = d["key"]
            if k not in seen_keys or d["similarity"] < seen_keys[k]["similarity"]:
                seen_keys[k] = d
        diffs["semantic"] = sorted(seen_keys.values(), key=lambda x: x["similarity"])

        # Vérifier si un même commit touche les deux catégories de manière indissociable
        if fiche_has_structural and fiche_has_semantic:
            diffs["indetermine"].append({
                "type": "indetermine",
                "description": "changements structurels ET sémantiques sur cette fiche — impossible de départager lequel a motivé l'autre sans historique de révisions",
            })
            stats["both_types"] += 1
        elif fiche_has_structural:
            stats["structural_only"] += 1
        elif fiche_has_semantic:
            stats["semantic_only"] += 1

        if diffs["structural"] or diffs["semantic"]:
            stats["fiches_with_changes"] += 1
            stats["structural_changes"] += len(diffs["structural"])
            stats["semantic_changes"] += len(diffs["semantic"])
        else:
            stats["fiches_unchanged"] += 1

        all_diffs[slug] = diffs

    # Statistiques finales
    print(f"\n=== Résultat ===")
    print(f"  Fiches scrappées OK : {stats['scraped_ok']}")
    print(f"  Fiches en échec     : {stats['scraped_fail']}")
    print(f"  Fiches sans changement : {stats['fiches_unchanged']}")
    print(f"  Fiches avec changements : {stats['fiches_with_changes']}")
    print(f"    - Structurels seulement : {stats['structural_only']}")
    print(f"    - Sémantiques seulement : {stats['semantic_only']}")
    print(f"    - Les deux (indéterminé): {stats['both_types']}")
    print(f"  Total changements structurels : {stats['structural_changes']}")
    print(f"  Total changements sémantiques : {stats['semantic_changes']}")

    output = {
        "meta": {
            "title": "Extraction brute — metiers-quebec.org live vs corpus_raw_v2",
            "description": "Diff champ par champ entre le site live (scrapé en direct) et le snapshot corpus_raw_v2",
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "corpus": "metiers-quebec.org (live) vs data/corpus_raw_v2/",
            "nb_fiches_total": stats["total_fiches"],
            "method": "Chaque fiche est rescrapée depuis metiers-quebec.org. Les sections sont extraites avec parse_sections() (identique à scrape_v2.py). Comparaison clé par clé normalisée, avec seuil de similarité textuelle à 0.95 pour détecter les reformulations.",
            "limites": [
                "Snapshot unique : pas d'historique de versions, donc pas de séquençage temporel possible",
                "Le parseur peut ne pas capturer exactement les mêmes sections que le parseur original selon l'évolution du HTML du site live",
                "Similarité lexicale (Jaccard sur mots) — peut manquer des reformulations profondes ou au contraire signaler un faux positif si le texte a seulement été réordonné",
            ]
        },
        "stats": stats,
        "fiches": all_diffs,
        "classification_categories": {
            "structure": [
                "ajout de section (présente dans le live, absente du corpus)",
                "suppression de section (présente dans le corpus, absente du live)",
                "renommage de clé de section",
            ],
            "sens": [
                "reformulation du texte à l'intérieur d'une section existante (similarité < 0.95)",
            ],
            "indetermine": [
                "même fiche a des changements structurels ET sémantiques sans qu'on puisse départager la causalité",
            ]
        }
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    outpath = os.path.join(OUTPUT_DIR, "metiers-quebec-diffs.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Sortie brute : {outpath}")
    print("=" * 60)


if __name__ == "__main__":
    main()
