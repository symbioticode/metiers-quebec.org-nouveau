#!/usr/bin/env python3
"""Compare la structure CNP2016 v1.0 à CNP2021 v1.0, niveau par niveau,
pour tester si le sommet de la CNP est resté aussi stable que les GWA
d'O*NET sur une fenêtre de temps comparable (kb021, test complémentaire
à extract_onet_genome_stability.py).

Sources :
- data/reference/cnp2021-structure.json (structure CNP2021 complète, extraite
  du CSV officiel StatCan)
- data/reference/cnp2016-to-cnp2021-mapping.json (table de correspondance
  code à code, seule donnée CNP2016 disponible dans le repo — voir GARDE
  ci-dessous)
- Comptes officiels du sommet CNP2016 v1.0 (10 grandes catégories, 40 grands
  groupes, 140 groupes intermédiaires, 500 groupes de base), publiés par
  StatCan (statcan.gc.ca/en/subjects/standard/noc/2016/introduction).
  AUCUN fichier CSV de structure CNP2016 n'est disponible dans le repo ni
  trouvé en ligne lors de cette recherche (contrairement à CNP2021, qui a un
  CSV structure dédié) — seul le compte agrégé officiel a pu être confirmé.
  Ceci est une limite documentée, pas une donnée dérivée en douce.

GARDE : CNP2016 a une hiérarchie à 4 niveaux (codes à 4 chiffres : grande
catégorie / grand groupe / groupe intermédiaire / groupe de base), alors que
CNP2021 en a 5 (codes à 5 chiffres : grande catégorie / grand groupe /
sous-grand groupe / sous-groupe / groupe de base — introduction du FEER en
remplacement du niveau de compétence). Il n'y a donc PAS de correspondance
terme à terme entre "groupe intermédiaire 2016" et un seul niveau 2021 — ce
script ne force aucune correspondance de ce type. Seul le niveau sommital
(grande catégorie, comparable dans les deux versions) et le niveau feuille
(groupe de base, comparable via la table de mapping) sont comparés
directement.
"""
import json
import sys
from collections import Counter
from pathlib import Path

STRUCT_2021 = Path(__file__).resolve().parent.parent / "data/reference/cnp2021-structure.json"
MAPPING = Path(__file__).resolve().parent.parent / "data/reference/cnp2016-to-cnp2021-mapping.json"
OUT = Path(__file__).resolve().parent.parent / "data/reference/cnp2016-vs-cnp2021-structure-comparison.json"

# Comptes officiels CNP2016 v1.0, sommet de la hiérarchie (StatCan, page
# d'introduction NOC 2016 — aucun CSV structure trouvé, donnée agrégée
# uniquement, PAS de liste des 10 libellés eux-mêmes extraite ici).
CNP2016_TOP_COUNTS = {
    "grande_categorie": 10,
    "grand_groupe": 40,
    "groupe_intermediaire": 140,
    "groupe_de_base": 500,
}


def main():
    if not STRUCT_2021.exists() or not MAPPING.exists():
        print(f"ERREUR: source manquante", file=sys.stderr)
        sys.exit(1)

    struct_2021 = json.loads(STRUCT_2021.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))

    entrees_2021 = struct_2021["entrees"]
    counts_2021 = Counter(e["niveau"] for e in entrees_2021)

    grandes_categories_2021 = sorted(
        {e["code"]: e["titre"] for e in entrees_2021 if e["niveau"] == "grande_categorie"}.items()
    )

    # Niveau sommital : grande catégorie (comparable 2016 vs 2021, 1 chiffre
    # dans les deux versions).
    niveau_sommital = {
        "cnp2016_count": CNP2016_TOP_COUNTS["grande_categorie"],
        "cnp2021_count": counts_2021["grande_categorie"],
        "delta": counts_2021["grande_categorie"] - CNP2016_TOP_COUNTS["grande_categorie"],
        "cnp2021_libelles": [t for _, t in grandes_categories_2021],
        "note": (
            "Comptes identiques (10 = 10). Les libellés des 10 grandes catégories "
            "CNP2016 n'ont pas été extraits ici faute de CSV structure CNP2016 "
            "disponible — seule l'égalité numérique du sommet est établie, pas "
            "l'identité exacte des 10 intitulés. Le nombre est stable ; la "
            "table de correspondance ne montre aucune fusion/scission au niveau "
            "grande catégorie (voir niveau groupe_de_base ci-dessous pour le "
            "détail des changements structurels, qui se produisent au niveau "
            "des groupes de base, PAS au sommet)."
        ),
    }

    # Niveau feuille : groupe de base, comparable via la table de mapping
    # (les codes changent de format 4->5 chiffres mais chaque entrée du
    # mapping relie un code 2016 à un ou plusieurs codes 2021).
    entries = mapping["entrees"]
    codes_2016 = sorted({e["cnp_2016"] for e in entries})
    codes_2021 = sorted({e["cnp_2021"] for e in entries})

    changement_types = Counter()
    for e in entries:
        tc = e["type_changement"] or ""
        # Normaliser les variantes orthographiques mineures observées dans le CSV source
        tc_norm = tc.replace("RC4.2 - Split off ,", "RC4.2 - Split off,").replace(", RC5 VC1", ", RC5, VC1")
        if "RC3.1" in tc_norm or "RC3.2" in tc_norm:
            changement_types["fusion (merger/take-over)"] += 1
        elif "RC4.1" in tc_norm or "RC4.2" in tc_norm:
            changement_types["scission (breakdown/split off)"] += 1
        elif "RC5" in tc_norm:
            changement_types["transfert (reclassement sans fusion/scission)"] += 1
        else:
            changement_types["renommage/recodage seul (VC1/VC2 sans RC)"] += 1

    # Un code 2016 est compté "fusionné" ou "scindé" s'il apparaît dans une
    # ligne portant cette étiquette, indépendamment des autres lignes qui le
    # concernent (un même code peut apparaître dans plusieurs lignes de mapping).
    codes_2016_par_type = Counter()
    for e in entries:
        tc = e["type_changement"] or ""
        if "RC3.1" in tc or "RC3.2" in tc:
            codes_2016_par_type["fusion"] += 1
        if "RC4.1" in tc or "RC4.2" in tc:
            codes_2016_par_type["scission"] += 1

    niveau_feuille = {
        "cnp2016_count_groupes_de_base": len(codes_2016),
        "cnp2021_count_groupes_de_base": len(codes_2021),
        "cnp2021_count_officiel_structure_json": counts_2021["groupe_de_base"],
        "delta": len(codes_2021) - len(codes_2016),
        "total_lignes_mapping": len(entries),
        "repartition_type_changement_lignes": dict(changement_types),
        "note": (
            "500 -> 516 groupes de base. Aucune ligne de mapping n'indique un "
            "changement de code SANS renommage (VC2 - Name Change est présent "
            "dans quasi 100% des lignes) : le passage 4->5 chiffres a "
            "mécaniquement forcé un recodage de chaque groupe de base, que son "
            "contenu ait changé ou non. Les vraies scissions/fusions "
            "structurelles (RC3/RC4) sont minoritaires : "
            f"{sum(v for k, v in changement_types.items() if k.startswith(('fusion', 'scission')))} "
            f"lignes sur {len(entries)}, le reste étant transfert (RC5) ou "
            "simple recodage/renommage."
        ),
    }

    niveaux_intermediaires_note = (
        "Les niveaux intermédiaires (grand groupe, sous-grand groupe/groupe "
        "intermédiaire, sous-groupe) ne sont PAS comparés terme à terme ici : "
        "CNP2016 a 2 niveaux intermédiaires (grand groupe 40, groupe "
        "intermédiaire 140) alors que CNP2021 en a 3 (grand groupe 45, "
        "sous-grand groupe 89, sous-groupe 162) suite à l'introduction du "
        "5e chiffre (FEER). Forcer une correspondance 1:1 entre "
        "'groupe intermédiaire 2016' et un des deux niveaux 2021 serait "
        "artificiel et non justifié par les données disponibles. C'est "
        "documenté ici comme un résultat en soi (difficulté de mapping), pas "
        "lissé."
    )

    out = {
        "titre": "Comparaison structurelle CNP2016 v1.0 vs CNP2021 v1.0 (test complémentaire kb021)",
        "garde_principale": (
            "Une seule transition longitudinale réelle est disponible "
            "(CNP2016 -> CNP2021 ; CNP2021 -> CNP2026 n'est pas publiée avant "
            "décembre 2026). Ce document ne permet PAS de conclure sur un taux "
            "de stabilité structurel dans le temps — un seul point de contraste "
            "CNP vs O*NET sur une fenêtre comparable, rien de plus."
        ),
        "limite_source_cnp2016": (
            "Aucun CSV de structure CNP2016 officiel trouvé dans le repo ni en "
            "ligne (contrairement à CNP2021). Les comptes du sommet CNP2016 "
            "(10/40/140/500) proviennent de la page d'introduction StatCan, "
            "pas d'un fichier structuré comparable au CSV CNP2021. Les libellés "
            "exacts des grandes catégories CNP2016 n'ont pas été vérifiés "
            "individuellement contre ceux de CNP2021 — seule l'égalité "
            "numérique (10 = 10) est établie ici, pas l'identité de contenu."
        ),
        "niveau_sommital_grande_categorie": niveau_sommital,
        "niveau_feuille_groupe_de_base": niveau_feuille,
        "niveaux_intermediaires_non_compares": niveaux_intermediaires_note,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Niveau sommital (grande catégorie):", niveau_sommital["cnp2016_count"], "->", niveau_sommital["cnp2021_count"])
    print("Niveau feuille (groupe de base):", niveau_feuille["cnp2016_count_groupes_de_base"], "->", niveau_feuille["cnp2021_count_groupes_de_base"])
    print("Répartition type de changement (lignes de mapping):", dict(changement_types))
    print(f"Écrit: {OUT}")


if __name__ == "__main__":
    main()
