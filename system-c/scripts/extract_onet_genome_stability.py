#!/usr/bin/env python3
"""Extrait, pour un échantillon espacé de versions O*NET (2003-2026), trois
métriques par version : (a) la liste complète des Work Activities / GWA
("fonctions atomiques" — proxy le plus proche du concept testé par kb021),
(b) le nombre de Task Statements ("titres/tâches", couche volatile), (c) le
nombre de codes O*NET-SOC couverts (occupations).

Contexte : kb021 (hypothèse 4 — un alphabet de fonctions atomiques serait
plus stable dans le temps que les titres de métiers/tâches). Ce script
fournit les données longitudinales brutes nécessaires pour tester cela sans
attendre des années de corpus réel — proxy externe déjà longitudinal (idée
notée dans kb021 comme piste à vérifier).

Source : https://www.onetcenter.org/db_releases.html — zips texte des
releases O*NET. Licence CC BY 4.0 (O*NET, sponsorisé par US DOL/ETA).

GARDE-INTÉGRITÉ :
- Échantillonnage explicite, pas exhaustif (voir SAMPLE ci-dessous et sa
  justification dans le rapport docs/kb021-genome-stability-onet-test.md).
  Toutes les releases listées sur la page ont été vérifiées comme
  téléchargeables (200 OK) au moment de l'exécution (25/07/2026) ; voir
  anomalies["releases_disponibles"] pour le compte exact.
- Le nom de fichier interne change selon l'ère (WorkActivity.txt avant
  v10.0, "Work Activities.txt" après ; Tasks.txt avant v14.0,
  "Task Statements.txt" après ; onetsoc_data.txt avant v10.0,
  "Occupation Data.txt" après). Le script résout ces variantes par
  normalisation du nom de fichier (minuscules, espaces/underscores
  supprimés) plutôt que par un chemin figé par version — toute variante non
  reconnue est signalée en anomalie plutôt que silencieusement ignorée.
- "Green Task Statements.txt" (v17.0-v23.0, tâches liées à l'économie verte)
  n'est PAS compté avec Task Statements.txt — compté et rapporté séparément
  pour ne pas fausser la comparaison longitudinale (ce fichier disparaît
  après v23.0, ce qui casserait la continuité de la série si fusionné).

Usage : python3 scripts/extract_onet_genome_stability.py
Source (cache local, téléchargé si absent) : scratch dir (voir SCRATCH_DIR)
Sortie : data/reference/onet-genome-stability/<version>.json (un par
release) + data/reference/onet-genome-stability/_combined.json
"""
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

SCRATCH_DIR = Path(
    "/tmp/nix-shell-128177-0/claude-1000/-home-andrei-Projects-62-FREE-system-c/"
    "9c6ea0c7-1247-4b7a-982d-4fad8068a0a3/scratchpad/onet"
)
OUT_DIR = Path(__file__).resolve().parent.parent / "data/reference/onet-genome-stability"

# Échantillon : ~1 point/an 2003-2020 + points additionnels autour des deux
# révisions majeures de contenu/taxonomie connues (transition SOC 2000->2010
# entre v10 et v14 environ ; transition SOC 2010->2018 entre v21 et v23 ;
# introduction puis retrait des "Green Task Statements" v17-v23 ; ajout de
# nouveaux fichiers de liaison Skills/Abilities/Interests->Work Activities à
# partir de v25). 17 points au total — voir justification complète dans le
# rapport docs/kb021-genome-stability-onet-test.md.
SAMPLE = [
    ("5.0", "2003-04", "https://www.onetcenter.org/dl_files/db_50.zip"),
    ("6.0", "2004-07", "https://www.onetcenter.org/dl_files/db_60.zip"),
    ("8.0", "2005-06", "https://www.onetcenter.org/dl_files/db_80.zip"),
    ("10.0", "2006-06", "https://www.onetcenter.org/dl_files/db_10_0.zip"),
    ("12.0", "2007-06", "https://www.onetcenter.org/dl_files/db_12_0.zip"),
    ("14.0", "2009-06", "https://www.onetcenter.org/dl_files/db_14_0.zip"),
    ("15.0", "2010-07", "https://www.onetcenter.org/dl_files/db_15_0.zip"),
    ("17.0", "2012-07", "https://www.onetcenter.org/dl_files/db_17_0.zip"),
    ("19.0", "2014-07", "https://www.onetcenter.org/dl_files/db_19_0.zip"),
    ("20.0", "2015-08", "https://www.onetcenter.org/dl_files/db_20_0.zip"),
    ("21.0", "2016-08", "https://www.onetcenter.org/dl_files/database/db_21_0_text.zip"),
    ("22.0", "2017-08", "https://www.onetcenter.org/dl_files/database/db_22_0_text.zip"),
    ("23.0", "2018-08", "https://www.onetcenter.org/dl_files/database/db_23_0_text.zip"),
    ("25.0", "2020-08", "https://www.onetcenter.org/dl_files/database/db_25_0_text.zip"),
    ("27.0", "2022-08", "https://www.onetcenter.org/dl_files/database/db_27_0_text.zip"),
    ("29.0", "2024-08", "https://www.onetcenter.org/dl_files/database/db_29_0_text.zip"),
    ("30.3", "2026-05", "https://www.onetcenter.org/dl_files/database/db_30_3_text.zip"),
]

WORK_ACTIVITIES_NAMES = {"workactivity.txt", "workactivities.txt"}
TASKS_NAMES = {"tasks.txt", "taskstatements.txt"}
OCCUPATION_NAMES = {"onetsocdata.txt", "occupationdata.txt"}
GREEN_TASKS_NAMES = {"greentaskstatements.txt"}


def norm(name: str) -> str:
    base = name.rsplit("/", 1)[-1]
    return re.sub(r"[\s_]", "", base).lower()


def find_member(zf: zipfile.ZipFile, wanted: set) -> str | None:
    for info in zf.infolist():
        if norm(info.filename) in wanted:
            return info.filename
    return None


def download(version: str, url: str) -> Path:
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    dest = SCRATCH_DIR / f"db_{version}.zip"
    if not dest.exists():
        print(f"  téléchargement {url} -> {dest}", file=sys.stderr)
        urllib.request.urlretrieve(url, dest)
    return dest


def read_tsv_rows(zf: zipfile.ZipFile, member: str):
    with zf.open(member) as fh:
        text = fh.read().decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    if not lines:
        return [], []
    header = lines[0].split("\t")
    rows = [ln.split("\t") for ln in lines[1:] if ln.strip()]
    return header, rows


def extract_release(version: str, date: str, url: str) -> dict:
    zpath = download(version, url)
    anomalies = []
    with zipfile.ZipFile(zpath) as zf:
        wa_member = find_member(zf, WORK_ACTIVITIES_NAMES)
        task_member = find_member(zf, TASKS_NAMES)
        occ_member = find_member(zf, OCCUPATION_NAMES)
        green_member = find_member(zf, GREEN_TASKS_NAMES)

        if wa_member is None:
            anomalies.append("Work Activities: fichier introuvable (aucun nom reconnu)")
        if task_member is None:
            anomalies.append("Task Statements: fichier introuvable (aucun nom reconnu)")
        if occ_member is None:
            anomalies.append("Occupation Data: fichier introuvable (aucun nom reconnu)")

        gwa_entries = {}
        if wa_member:
            header, rows = read_tsv_rows(zf, wa_member)
            try:
                id_idx = header.index("Element ID")
                name_idx = header.index("Element Name")
            except ValueError:
                anomalies.append(f"Work Activities ({wa_member}): colonnes Element ID/Element Name absentes; header={header}")
                id_idx = name_idx = None
            if id_idx is not None:
                for r in rows:
                    if len(r) <= max(id_idx, name_idx):
                        continue
                    gwa_entries[r[id_idx]] = r[name_idx]

        n_tasks = None
        if task_member:
            header, rows = read_tsv_rows(zf, task_member)
            try:
                tid_idx = header.index("Task ID")
                distinct_ids = {r[tid_idx] for r in rows if len(r) > tid_idx and r[tid_idx] not in ("n/a", "")}
                n_tasks = len(distinct_ids) if distinct_ids else len(rows)
            except ValueError:
                n_tasks = len(rows)
                anomalies.append(f"Task Statements ({task_member}): pas de colonne Task ID exploitable, compte = nb de lignes brutes ({n_tasks})")

        n_green_tasks = None
        if green_member:
            _, rows = read_tsv_rows(zf, green_member)
            n_green_tasks = len(rows)

        n_occ = None
        if occ_member:
            header, rows = read_tsv_rows(zf, occ_member)
            try:
                soc_idx = header.index("O*NET-SOC Code")
                n_occ = len({r[soc_idx] for r in rows if len(r) > soc_idx})
            except ValueError:
                anomalies.append(f"Occupation Data ({occ_member}): colonne O*NET-SOC Code absente; header={header}")

    result = {
        "version": version,
        "date": date,
        "source_url": url,
        "internal_filenames": {
            "work_activities": wa_member,
            "task_statements": task_member,
            "green_task_statements": green_member,
            "occupation_data": occ_member,
        },
        "n_gwa": len(gwa_entries),
        "gwa": [{"id": k, "label": v} for k, v in sorted(gwa_entries.items())],
        "n_tasks": n_tasks,
        "n_green_tasks": n_green_tasks,
        "n_occupations": n_occ,
        "anomalies": anomalies,
    }
    return result


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    combined = {
        "source": "O*NET Database releases (onetcenter.org/db_releases.html), CC BY 4.0",
        "note": (
            "Échantillon espacé de 17 releases 2003-2026 (voir SAMPLE dans le script "
            "pour la justification). GWA = Work Activities (~40 fonctions atomiques "
            "génériques), proxy testé par kb021 hypothèse 4."
        ),
        "releases": [],
        "global_anomalies": [],
    }
    for version, date, url in SAMPLE:
        print(f"=== {version} ({date}) ===", file=sys.stderr)
        try:
            rel = extract_release(version, date, url)
        except Exception as e:
            print(f"  ERREUR: {e}", file=sys.stderr)
            combined["global_anomalies"].append(f"{version}: échec extraction — {e}")
            continue
        for a in rel["anomalies"]:
            print(f"  ANOMALIE: {a}", file=sys.stderr)
        print(
            f"  GWA={rel['n_gwa']} tasks={rel['n_tasks']} green_tasks={rel['n_green_tasks']} occ={rel['n_occupations']}",
            file=sys.stderr,
        )
        out_path = OUT_DIR / f"{version}.json"
        out_path.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
        combined["releases"].append({
            "version": rel["version"],
            "date": rel["date"],
            "n_gwa": rel["n_gwa"],
            "n_tasks": rel["n_tasks"],
            "n_green_tasks": rel["n_green_tasks"],
            "n_occupations": rel["n_occupations"],
            "anomalies": rel["anomalies"],
            "file": f"{version}.json",
        })

    combined_path = OUT_DIR / "_combined.json"
    combined_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nÉcrit: {combined_path}", file=sys.stderr)
    print(f"Releases traitées avec succès: {len(combined['releases'])}/{len(SAMPLE)}", file=sys.stderr)


if __name__ == "__main__":
    main()
