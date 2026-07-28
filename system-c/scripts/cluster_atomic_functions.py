#!/usr/bin/env python3
"""Test H4b de kb021 : fait émerger un alphabet de fonctions atomiques PAR
clustering sur le corpus cumulé (kb019+kb020+second-wave), sans imposer de
nombre de clusters a priori, et teste sa stabilité quand on ajoute la
deuxième vague (second-wave, 33 fonctions / 11 métiers) au corpus initial
(kb019+kb020, 55 fonctions / 16 métiers).

MÉTHODE — décidée et documentée AVANT d'exécuter le clustering et de voir
un quelconque résultat, pour éviter le biais consistant à choisir une
méthode qui produirait un nombre de clusters proche de 41 (mimant O*NET) :

1. Vectorisation : TF-IDF sur des n-grammes de caractères (analyzer=
   'char_wb', ngram_range=(3,5)), texte en minuscules, accents conservés.
   Choix motivé : les libellés sont de courtes phrases verbales en
   français avec des variations morphologiques (accords, formes
   pronominales/infinitives) ; un TF-IDF de n-grammes de caractères capture
   la proximité lexicale entre verbes/objets partagés sans nécessiter de
   lemmatisation ni de liste d'arrêt (stopwords) qui introduirait un choix
   supplémentaire à justifier.
2. Distance : cosinus sur les vecteurs TF-IDF.
3. Algorithme : `AgglomerativeClustering` (scikit-learn), linkage='average',
   `n_clusters=None`, `distance_threshold=T` — le nombre de clusters n'est
   PAS fixé, il émerge du seuil de distance.
4. Seuils pré-enregistrés (choisis avant tout résultat) : T ∈ {0.50, 0.60,
   0.70} — un seuil bas (fusion stricte, seulement les libellés très
   proches lexicalement), un seuil moyen, un seuil haut (fusion permissive).
   Les trois seuils sont rapportés systématiquement, aucun n'est sélectionné
   après coup pour son nombre de clusters.

Étapes de comparaison :
- (a) clustering sur kb019+kb020 seuls (55 fonctions, 16 "métiers"/lectures)
- (full) clustering sur l'ensemble kb019+kb020+second-wave (88 fonctions,
  27 métiers) — reclustering complet, pas un ajout incrémental sur les
  centroïdes de (a), pour tester si la FORME des clusters change, pas
  seulement leur nombre.

Stabilité : pour chaque cluster de (a), on cherche le cluster de (full)
qui contient le plus de ses membres (meilleur recouvrement), et on mesure
la pureté (fraction des membres du cluster (a) qui restent groupés
ensemble dans un seul cluster de (full)) — une pureté proche de 1 pour
(presque) tous les clusters signale des clusters stables ; une pureté
basse généralisée signale que l'ajout de la deuxième vague redessine la
structure existante.

Source : data/reference/onet-genome-stability/atomic-functions-corpus.json
Sortie : data/reference/onet-genome-stability/clustering-h4b.json
         data/reference/onet-genome-stability/clustering-h4b.md
"""
import json
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_DIR = Path(__file__).resolve().parent.parent / "data/reference/onet-genome-stability"
CORPUS = DATA_DIR / "atomic-functions-corpus.json"
OUT_JSON = DATA_DIR / "clustering-h4b.json"
OUT_MD = DATA_DIR / "clustering-h4b.md"

THRESHOLDS = [0.50, 0.60, 0.70]


def vectorize(texts):
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True)
    return vec.fit_transform(texts)


def cluster(texts, threshold):
    X = vectorize(texts).toarray()
    model = AgglomerativeClustering(
        n_clusters=None, distance_threshold=threshold, linkage="average", metric="cosine"
    )
    labels = model.fit_predict(X)
    return [int(x) for x in labels]


def clusters_by_label(entries, labels):
    groups = {}
    for e, lab in zip(entries, labels):
        groups.setdefault(int(lab), []).append(e["fonction"])
    return groups


def stability(entries_a, labels_a, entries_full, labels_full):
    """Pour chaque cluster de (a), trouve le cluster de (full) qui contient le
    plus de ses membres et calcule la pureté (fraction des membres du cluster
    (a) qui atterrissent dans ce même cluster (full))."""
    id_to_full_label = {e["id"]: lab for e, lab in zip(entries_full, labels_full)}

    groups_a = {}
    for e, lab in zip(entries_a, labels_a):
        groups_a.setdefault(int(lab), []).append(e["id"])

    report = []
    for lab_a, ids in groups_a.items():
        full_labels_of_members = [id_to_full_label[i] for i in ids]
        counts = {}
        for fl in full_labels_of_members:
            counts[fl] = counts.get(fl, 0) + 1
        best_full_label, best_count = max(counts.items(), key=lambda kv: kv[1])
        purity = best_count / len(ids)
        report.append({
            "cluster_a_id": lab_a,
            "taille": len(ids),
            "cluster_full_correspondant": best_full_label,
            "purete": round(purity, 2),
            "nb_clusters_full_touches": len(counts),
        })
    return report


def main():
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    entries = data["entrees"]

    entries_a = [e for e in entries if e["wave"] == "a"]
    entries_full = entries  # a + b, reclustering complet

    n_metiers_a = len({e["metier"] for e in entries_a})
    n_metiers_full = len({e["metier"] for e in entries_full})

    result = {
        "method": (
            "TF-IDF char_wb n-grammes (3,5) + AgglomerativeClustering "
            "(linkage=average, metric=cosine, n_clusters=None, "
            "distance_threshold=T). Seuils pré-enregistrés avant tout résultat: "
            f"{THRESHOLDS}."
        ),
        "n_fonctions_a": len(entries_a),
        "n_fonctions_full": len(entries_full),
        "n_metiers_a": n_metiers_a,
        "n_metiers_full": n_metiers_full,
        "par_seuil": {},
    }

    md_lines = [
        "# Clustering H4b — alphabet de fonctions atomiques émergent (kb021)",
        "",
        f"Corpus (a) kb019+kb020 : {len(entries_a)} fonctions, {n_metiers_a} métiers/lectures.",
        f"Corpus (full) + second-wave : {len(entries_full)} fonctions, {n_metiers_full} métiers.",
        f"Croissance du corpus : fonctions +{round((len(entries_full)/len(entries_a)-1)*100)}%, "
        f"métiers +{round((n_metiers_full/n_metiers_a-1)*100)}%.",
        "",
    ]

    for T in THRESHOLDS:
        labels_a = cluster([e["fonction"] for e in entries_a], T)
        labels_full = cluster([e["fonction"] for e in entries_full], T)

        k_a = len(set(labels_a))
        k_full = len(set(labels_full))

        growth_clusters_pct = round((k_full / k_a - 1) * 100, 1) if k_a else None
        growth_metiers_pct = round((n_metiers_full / n_metiers_a - 1) * 100, 1)

        stab = stability(entries_a, labels_a, entries_full, labels_full)
        n_stable = sum(1 for s in stab if s["purete"] == 1.0)
        n_split = sum(1 for s in stab if s["nb_clusters_full_touches"] > 1)
        purete_moyenne = round(sum(s["purete"] for s in stab) / len(stab), 3)

        result["par_seuil"][str(T)] = {
            "k_clusters_a": k_a,
            "k_clusters_full": k_full,
            "croissance_clusters_pct": growth_clusters_pct,
            "croissance_metiers_pct": growth_metiers_pct,
            "clusters_a_detail": clusters_by_label(entries_a, labels_a),
            "clusters_full_detail": clusters_by_label(entries_full, labels_full),
            "stabilite_par_cluster_a": stab,
            "n_clusters_a_parfaitement_stables_purete_1": n_stable,
            "n_clusters_a_eclates_sur_plusieurs_clusters_full": n_split,
            "purete_moyenne": purete_moyenne,
        }

        md_lines.append(f"## Seuil T={T}")
        md_lines.append("")
        md_lines.append(f"- Clusters (a) kb019+kb020 : **{k_a}** (pour {len(entries_a)} fonctions, {n_metiers_a} métiers)")
        md_lines.append(f"- Clusters (full) avec second-wave : **{k_full}** (pour {len(entries_full)} fonctions, {n_metiers_full} métiers)")
        md_lines.append(f"- Croissance clusters : {growth_clusters_pct}% vs croissance métiers : {growth_metiers_pct}%")
        md_lines.append(f"- Clusters (a) parfaitement stables (pureté=1, tous les membres restent groupés) : {n_stable}/{k_a}")
        md_lines.append(f"- Clusters (a) éclatés sur plusieurs clusters (full) : {n_split}/{k_a}")
        md_lines.append(f"- Pureté moyenne : {purete_moyenne}")
        md_lines.append("")

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Écrit: {OUT_JSON}")
    print(f"Écrit: {OUT_MD}")
    for T in THRESHOLDS:
        r = result["par_seuil"][str(T)]
        print(f"T={T}: k_a={r['k_clusters_a']} -> k_full={r['k_clusters_full']} "
              f"(croissance clusters {r['croissance_clusters_pct']}% vs métiers {r['croissance_metiers_pct']}%), "
              f"pureté moyenne={r['purete_moyenne']}, stables={r['n_clusters_a_parfaitement_stables_purete_1']}/{r['k_clusters_a']}")


if __name__ == "__main__":
    main()
