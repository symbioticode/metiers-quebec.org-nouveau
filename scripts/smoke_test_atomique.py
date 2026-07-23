"""
smoke_test_atomique.py — Phase 4 : validation bout-en-bout

CORRECTIF (2026-07-22) : la première version n'appelait que 3 des 5
GARDES (garde_partition, garde_autojugement, garde_completude_explicite).
garde_non_reecriture et garde_irreversibilite n'étaient jamais exécutées
-- le message "OK — toutes les GARDES respectées" était donc inexact.
Cette version appelle les 5.

Convention CLI alignée sur scripts/build-feed.py :
    python3 smoke_test_atomique.py --in data/atomic/ --quiet

Étapes :
1. Charge chaque fichier data/atomic/{code}.json
2. Valide la structure minimale (champs requis)
3. Exécute les 5 GARDES sur l'ensemble du corpus chargé :
   - garde_partition (inter-fiches)
   - garde_autojugement (par FAIT)
   - garde_non_reecriture (par FAIT, contre corpus_raw_v2 si accessible)
   - garde_irreversibilite_corpus (par fiche, statique -- ne nécessite
     pas de relancer l'ingesteur)
   - garde_completude_explicite (par fiche)
4. Rapport détaillé pass/fail par GARDE, code de sortie non-zéro si une
   GARDE échoue
"""

import argparse
import json
import sys
from pathlib import Path

from gardes import (
    garde_partition,
    garde_autojugement,
    garde_non_reecriture,
    garde_irreversibilite_corpus,
    garde_completude_explicite,
    est_perimee,
)


def valider_structure_minimale(fiche, chemin):
    """Validation manuelle minimale sans dépendance jsonschema (stdlib only)."""
    erreurs = []
    for champ_requis in ("code", "noms", "faits", "completude"):
        if champ_requis not in fiche:
            erreurs.append(f"{chemin}: champ requis '{champ_requis}' manquant")
    for fait in fiche.get("faits", []):
        for champ_requis in ("champ", "valeur", "origine"):
            if champ_requis not in fait:
                erreurs.append(f"{chemin}: FAIT invalide, '{champ_requis}' manquant")
        origine = fait.get("origine", {})
        for champ_requis in ("source", "date_captee", "methode", "confiance"):
            if champ_requis not in origine:
                erreurs.append(f"{chemin}: origine invalide, '{champ_requis}' manquant")
    return erreurs


def charger_texte_brut(code, corpus_raw_dir):
    """
    Charge le texte brut disponible pour un métier, pour vérification
    contre GARDE-NON-RÉÉCRITURE.

    Sous l'Option B (mapping CNP provisoire, PASSATION_BIG_PICKLE.md),
    `code` est le slug metiers-quebec.org -- donc corpus_raw_v2/{code}.json
    est directement accessible sans mapping supplémentaire. Sous
    l'Option A (vrai CNP), cette fonction retournera None tant que le
    mapping inverse code->slug n'existe pas -- à corriger quand l'Option A
    sera en place.

    Retourne le texte concaténé de toutes les sections brutes, ou None
    si le fichier source est introuvable. Concaténer plutôt que mapper
    champ-par-champ est une approximation : ça affaiblit la précision de
    la GARDE (un faux positif de "recouvrement suffisant" est possible
    si la valeur provient d'une autre section que celle attendue) mais
    reste correct pour détecter une valeur totalement inventée.
    """
    chemin = corpus_raw_dir / f"{code}.json"
    if not chemin.exists():
        return None
    with open(chemin, encoding="utf-8") as f:
        brut = json.load(f)
    sections = brut.get("sections_raw", {})
    return " ".join(str(v) for v in sections.values())


def main():
    parser = argparse.ArgumentParser(description="Smoke test format atomique kb008-bis")
    parser.add_argument("--in", dest="in_dir", default="data/atomic/", help="Répertoire des fiches atomiques")
    parser.add_argument("--corpus-raw", dest="corpus_raw_dir", default="data/corpus_raw_v2/",
                         help="Répertoire du corpus brut, pour GARDE-NON-RÉÉCRITURE")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    in_dir = Path(args.in_dir)
    corpus_raw_dir = Path(args.corpus_raw_dir)
    if not in_dir.exists():
        print(f"ERREUR: répertoire {in_dir} introuvable. Rien à valider.", file=sys.stderr)
        sys.exit(2)

    fiches = []
    erreurs_structure = []
    for fichier in sorted(in_dir.glob("*.json")):
        with open(fichier, encoding="utf-8") as f:
            fiche = json.load(f)
        erreurs_structure.extend(valider_structure_minimale(fiche, fichier.name))
        fiches.append(fiche)

    if not args.quiet:
        print(f"{len(fiches)} fiches chargées depuis {in_dir}")

    if erreurs_structure:
        print(f"ÉCHEC structure ({len(erreurs_structure)} erreurs) :", file=sys.stderr)
        for e in erreurs_structure[:20]:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    compteurs = {
        "garde_partition": {"conforme": 0, "violations": 0},
        "garde_autojugement": {"conforme": 0, "violations": 0},
        "garde_non_reecriture": {"conforme": 0, "violations": 0, "non_verifiable": 0},
        "garde_irreversibilite_corpus": {"conforme": 0, "violations": 0},
        "garde_completude_explicite": {"conforme": 0, "violations": 0},
    }
    echecs_detail = []
    perimes = 0
    corpus_raw_absent_pour = []
    total_faits = 0

    r_partition = garde_partition(fiches)
    if r_partition["conforme"]:
        compteurs["garde_partition"]["conforme"] = len(fiches)
    else:
        compteurs["garde_partition"]["violations"] = len(r_partition["violations"])
        echecs_detail.append(f"garde_partition: doublons {r_partition['violations']}")

    for fiche in fiches:
        code = fiche.get("code")
        texte_brut = charger_texte_brut(code, corpus_raw_dir)
        if texte_brut is None:
            corpus_raw_absent_pour.append(code)

        for fait in fiche.get("faits", []):
            total_faits += 1
            r_auto = garde_autojugement(fait)
            if r_auto["conforme"]:
                compteurs["garde_autojugement"]["conforme"] += 1
            else:
                compteurs["garde_autojugement"]["violations"] += 1
                echecs_detail.append(f"{code} / {fait.get('champ')}: {r_auto['violations']}")

            r_reecr = garde_non_reecriture(fait, texte_brut, source_attendue="metiers_quebec")
            if r_reecr["conforme"] is None:
                compteurs["garde_non_reecriture"]["non_verifiable"] += 1
            elif r_reecr["conforme"]:
                compteurs["garde_non_reecriture"]["conforme"] += 1
            else:
                compteurs["garde_non_reecriture"]["violations"] += 1
                echecs_detail.append(
                    f"{code} / {fait.get('champ')}: recouvrement insuffisant "
                    f"({r_reecr.get('recouvrement')}) -- {r_reecr['violations']}"
                )

            if est_perimee(fait):
                perimes += 1

        r_irrev = garde_irreversibilite_corpus(fiche.get("faits", []))
        if r_irrev["conforme"]:
            compteurs["garde_irreversibilite_corpus"]["conforme"] += 1
        else:
            compteurs["garde_irreversibilite_corpus"]["violations"] += 1
            echecs_detail.append(f"{code}: {r_irrev['violations']}")

        r_comp = garde_completude_explicite(fiche)
        if r_comp["conforme"]:
            compteurs["garde_completude_explicite"]["conforme"] += 1
        else:
            compteurs["garde_completude_explicite"]["violations"] += 1
            echecs_detail.append(f"{code}: {r_comp['violations']}")

    print("\n=== Rapport GARDE par GARDE ===")
    print(f"garde_partition        : conforme={compteurs['garde_partition']['conforme']} "
          f"violations={compteurs['garde_partition']['violations']}")
    print(f"garde_autojugement      : conforme={compteurs['garde_autojugement']['conforme']} "
          f"violations={compteurs['garde_autojugement']['violations']}")
    print(f"garde_non_reecriture    : conforme={compteurs['garde_non_reecriture']['conforme']} "
          f"violations={compteurs['garde_non_reecriture']['violations']} "
          f"non_verifiable={compteurs['garde_non_reecriture']['non_verifiable']}")
    print(f"garde_irreversibilite   : conforme={compteurs['garde_irreversibilite_corpus']['conforme']} "
          f"violations={compteurs['garde_irreversibilite_corpus']['violations']}")
    print(f"garde_completude        : conforme={compteurs['garde_completude_explicite']['conforme']} "
          f"violations={compteurs['garde_completude_explicite']['violations']}")
    print(f"FAITS périmés (fraîcheur dépassée) : {perimes}")

    if corpus_raw_absent_pour:
        print(f"\nATTENTION : corpus_raw_v2 introuvable pour {len(corpus_raw_absent_pour)} fiches "
              f"-- garde_non_reecriture non vérifiable pour ces fiches (premiers 10) : "
              f"{corpus_raw_absent_pour[:10]}", file=sys.stderr)

    if echecs_detail:
        print(f"\n=== Détail des {len(echecs_detail)} violations ===", file=sys.stderr)
        for e in echecs_detail[:50]:
            print(f"  - {e}", file=sys.stderr)
        if len(echecs_detail) > 50:
            print(f"  ... et {len(echecs_detail) - 50} de plus", file=sys.stderr)

    total_violations = sum(c.get("violations", 0) for c in compteurs.values())
    if total_violations:
        print(f"\nÉCHEC : {total_violations} violations de GARDE détectées", file=sys.stderr)
        sys.exit(1)

    if total_faits and compteurs["garde_non_reecriture"]["non_verifiable"] == total_faits:
        print(
            "\nATTENTION : garde_non_reecriture n'a pu être vérifiée sur AUCUN FAIT "
            "(corpus_raw_v2 introuvable partout) -- ne pas considérer ceci comme "
            "'OK — toutes les GARDES respectées'.",
            file=sys.stderr,
        )
        sys.exit(3)

    print("\nOK — toutes les GARDES respectées (voir rapport détaillé ci-dessus)")
    sys.exit(0)


if __name__ == "__main__":
    main()
