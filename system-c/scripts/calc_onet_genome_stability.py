#!/usr/bin/env python3
"""Calcule, pour chaque paire de releases O*NET consécutives échantillonnées
(sortie de extract_onet_genome_stability.py), les deltas et ratios testant
kb021 hypothèse 4 : le nombre de fonctions atomiques (GWA) nouvelles
devrait croître beaucoup plus lentement que les titres/tâches (Task
Statements) et les occupations couvertes.

Pour chaque période (version N -> version N+1) :
- ΔGWA : ajouts et retraits par comparaison de labels (pas seulement de
  comptes) — un même ID avec un label légèrement différent est classé
  "renommage" (signalé, pas compté comme ajout+retrait) si l'ID est
  identique ; un ID qui disparaît et un autre qui apparaît sans lien
  évident sont comptés séparément comme retrait + ajout.
- ΔTasks, ΔOccupations : simple différence de comptes (le détail fin par
  tâche n'est pas conservé par le script d'extraction — volume ~19000,
  hors périmètre de ce calcul).
- Ratios ΔTasks/ΔGWA et ΔOccupations/ΔGWA : quand ΔGWA=0 (le cas général
  observé), le ratio est indéfini (division par zéro) — rapporté comme
  "inf" explicitement plutôt que masqué ou mis à 0/1, car un ΔGWA nul est
  en lui-même la donnée la plus importante pour l'hypothèse 4, pas une
  anomalie de calcul.

Source : data/reference/onet-genome-stability/<version>.json
Sortie : data/reference/onet-genome-stability/deltas.json
         data/reference/onet-genome-stability/deltas.md (table brute)
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data/reference/onet-genome-stability"

VERSIONS_ORDER = [
    "5.0", "6.0", "8.0", "10.0", "12.0", "14.0", "15.0", "17.0", "19.0",
    "20.0", "21.0", "22.0", "23.0", "25.0", "27.0", "29.0", "30.3",
]


def load(version: str) -> dict:
    return json.loads((DATA_DIR / f"{version}.json").read_text(encoding="utf-8"))


def ratio(delta_num, delta_den):
    if delta_den == 0:
        if delta_num == 0:
            return 0.0
        return float("inf")
    return round(delta_num / delta_den, 2)


def main():
    releases = [load(v) for v in VERSIONS_ORDER]
    periods = []
    anomalies = []

    for a, b in zip(releases, releases[:-1] and releases[1:]):
        gwa_a = {g["id"]: g["label"] for g in a["gwa"]}
        gwa_b = {g["id"]: g["label"] for g in b["gwa"]}

        ids_a, ids_b = set(gwa_a), set(gwa_b)
        added_ids = ids_b - ids_a
        removed_ids = ids_a - ids_b
        common_ids = ids_a & ids_b
        renamed = {i: (gwa_a[i], gwa_b[i]) for i in common_ids if gwa_a[i] != gwa_b[i]}

        n_added = len(added_ids)
        n_removed = len(removed_ids)
        d_gwa_net = len(gwa_b) - len(gwa_a)
        d_gwa_churn = n_added + n_removed  # ajouts+retraits bruts (hors renommages)

        d_tasks = (b["n_tasks"] or 0) - (a["n_tasks"] or 0)
        d_occ = (b["n_occupations"] or 0) - (a["n_occupations"] or 0)

        if a["n_tasks"] is None or b["n_tasks"] is None:
            anomalies.append(f"{a['version']}->{b['version']}: n_tasks manquant, delta non fiable")
        if a["n_occupations"] is None or b["n_occupations"] is None:
            anomalies.append(f"{a['version']}->{b['version']}: n_occupations manquant, delta non fiable")

        period = {
            "from": a["version"],
            "to": b["version"],
            "from_date": a["date"],
            "to_date": b["date"],
            "gwa_added": sorted(added_ids),
            "gwa_removed": sorted(removed_ids),
            "gwa_renamed_same_id": {k: {"from": v[0], "to": v[1]} for k, v in sorted(renamed.items())},
            "d_gwa_net": d_gwa_net,
            "d_gwa_churn": d_gwa_churn,
            "d_tasks": d_tasks,
            "d_occupations": d_occ,
            "ratio_tasks_per_gwa_churn": ratio(abs(d_tasks), d_gwa_churn),
            "ratio_occupations_per_gwa_churn": ratio(abs(d_occ), d_gwa_churn),
        }
        periods.append(period)

    out = {
        "method": (
            "ΔGWA net = nouveaux IDs - IDs retirés entre deux releases consécutives "
            "échantillonnées (pas nécessairement adjacentes dans la numérotation O*NET "
            "réelle — voir échantillonnage documenté dans extract_onet_genome_stability.py). "
            "ΔGWA churn = |ajouts| + |retraits| (renommages à ID identique exclus, listés "
            "séparément). Ratio = |Δtasks| / churn_GWA (et idem occupations) ; 'inf' si "
            "churn_GWA = 0, ce qui est le cas observé pour toutes les périodes de cet "
            "échantillon (voir data)."
        ),
        "periods": periods,
        "anomalies": anomalies,
    }

    (DATA_DIR / "deltas.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Deltas O*NET — GWA (fonctions atomiques) vs Tasks vs Occupations",
        "",
        "| Période | ΔGWA net | ΔGWA churn (add/rem) | ΔTasks | ΔOccupations | ratio Tasks/GWAchurn | ratio Occ/GWAchurn |",
        "|---|---|---|---|---|---|---|",
    ]
    for p in periods:
        lines.append(
            f"| {p['from']} ({p['from_date']}) -> {p['to']} ({p['to_date']}) "
            f"| {p['d_gwa_net']} | {p['d_gwa_churn']} | {p['d_tasks']} | {p['d_occupations']} "
            f"| {p['ratio_tasks_per_gwa_churn']} | {p['ratio_occupations_per_gwa_churn']} |"
        )
    lines.append("")
    lines.append("## Renommages à ID identique détectés (hors churn)")
    lines.append("")
    any_renamed = False
    for p in periods:
        if p["gwa_renamed_same_id"]:
            any_renamed = True
            lines.append(f"- {p['from']} -> {p['to']}:")
            for gid, chg in p["gwa_renamed_same_id"].items():
                lines.append(f"  - `{gid}`: \"{chg['from']}\" -> \"{chg['to']}\"")
    if not any_renamed:
        lines.append("(aucun)")
    lines.append("")
    if anomalies:
        lines.append("## Anomalies")
        lines.append("")
        for a in anomalies:
            lines.append(f"- {a}")

    (DATA_DIR / "deltas.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Écrit: {DATA_DIR / 'deltas.json'}")
    print(f"Écrit: {DATA_DIR / 'deltas.md'}")
    print(f"Périodes calculées: {len(periods)}")
    if anomalies:
        print(f"ANOMALIES ({len(anomalies)}):")
        for a in anomalies:
            print(f"  - {a}")


if __name__ == "__main__":
    main()
