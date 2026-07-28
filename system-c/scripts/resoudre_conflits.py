#!/usr/bin/env python3
"""resoudre_conflits.py — Phase 3 : détection et résolution de conflits inter-sources.

Stricte stdlib. GARDE-AUTOJUGEMENT : un ingesteur ne fixe jamais sa propre
confiance. La résolution trie par confiance et ne choisit jamais en cas
d'égalité.

Usage:
  python3 scripts/resoudre_conflits.py --in data/atomic/
  python3 scripts/resoudre_conflits.py --test-egalite   # cas synthétique
"""

import argparse
import json
import sys
from pathlib import Path

# Ordre de confiance (du plus haut au plus bas)
ORDRE_CONFIANCE = {"haute": 3, "moyenne": 2, "basse": 1}


def detecter_conflits(fiche: dict) -> list[dict]:
    """Détecte les champs avec plus d'un FAIT dont les valeurs diffèrent.

    Retourne une liste de conflits, chacun étant :
      {"champ": str, "faits": [fait1, fait2, ...]}
    """
    par_champ: dict[str, list[dict]] = {}
    for fait in fiche["faits"]:
        par_champ.setdefault(fait["champ"], []).append(fait)

    conflits = []
    for champ, faits in par_champ.items():
        if len(faits) < 2:
            continue
        # Comparer les valeurs (repr string pour flexibilité)
        valeurs = set(json.dumps(f["valeur"], ensure_ascii=False, sort_keys=True) for f in faits)
        if len(valeurs) > 1:
            conflits.append({"champ": champ, "faits": faits})

    return conflits


def resoudre_conflit(faits_concurrents: list[dict]) -> tuple[dict | None, str]:
    """Résout un conflit entre FAITS concurrents par confiance.

    Retourne (gagnant, raison) ou (None, raison) si égalité.
    Ne choisit JAMAIS arbitrairement en cas d'égalité.
    """
    # Trier par confiance décroissante
    tries = sorted(
        faits_concurrents,
        key=lambda f: ORDRE_CONFIANCE.get(f["origine"]["confiance"], 0),
        reverse=True,
    )

    meilleur_confiance = ORDRE_CONFIANCE.get(tries[0]["origine"]["confiance"], 0)
    nb_meilleur = sum(
        1 for f in tries
        if ORDRE_CONFIANCE.get(f["origine"]["confiance"], 0) == meilleur_confiance
    )

    if nb_meilleur == 1:
        return tries[0], "resolu_par_confiance"
    else:
        return None, "conflit_non_resolu -- arbitrage humain requis"


def afficher_conflit(code: str, conflit: dict, resolution: tuple) -> None:
    """Affiche un conflit et sa résolution."""
    champ = conflit["champ"]
    gagnant, raison = resolution

    print(f"\n{'='*60}")
    print(f"CODE     : {code}")
    print(f"CHAMP    : {champ}")
    print(f"{'─'*60}")

    for fait in conflit["faits"]:
        src = fait["origine"]["source"]
        conf = fait["origine"]["confiance"]
        val = fait["valeur"]
        if isinstance(val, (int, float)):
            val_str = f"{val:,}$"
        else:
            val_str = str(val)[:120]
        print(f"  {src:20s}  conf={conf:8s}  valeur={val_str}")

    print(f"{'─'*60}")
    if gagnant:
        print(f"  RÉSULTAT : {gagnant['origine']['source']} gagne ({raison})")
        print(f"  VALEUR   : {gagnant['valeur']}")
    else:
        print(f"  RÉSULTAT : {raison}")


def test_egalite():
    """Test synthétique : égalité de confiance → conflit_non_resolu."""
    print("=" * 60)
    print("TEST ÉGALITÉ DE CONFIANCE (synthétique)")
    print("=" * 60)

    faits = [
        {
            "champ": "salaire_median",
            "valeur": 50000,
            "origine": {"source": "source_a", "methode": "api", "confiance": "moyenne",
                        "date_captee": "2026-01-01"},
        },
        {
            "champ": "salaire_median",
            "valeur": 55000,
            "origine": {"source": "source_b", "methode": "scraping", "confiance": "moyenne",
                        "date_captee": "2026-03-01"},
        },
    ]

    print("\nFAITS en conflit:")
    for f in faits:
        print(f"  {f['origine']['source']:20s}  conf={f['origine']['confiance']:8s}  valeur={f['valeur']:,}$")

    gagnant, raison = resoudre_conflit(faits)
    print(f"\nRÉSULTAT : raison={raison}")
    print(f"  gagnant={'None' if gagnant is None else gagnant['origine']['source']}")
    assert gagnant is None, "FAIL: un gagnant a été choisi malgré l'égalité"
    assert "non_resolu" in raison, f"FAIL: raison inattendue: {raison}"
    print("\nOK — égalité correctement détectée, aucun gagnant inventé.")


def main():
    parser = argparse.ArgumentParser(description="Détection et résolution de conflits")
    parser.add_argument("--in", dest="in_dir", default="data/atomic",
                        help="Dossier contenant les fiches atomiques")
    parser.add_argument("--test-egalite", action="store_true",
                        help="Exécuter le test synthétique d'égalité de confiance")
    args = parser.parse_args()

    if args.test_egalite:
        test_egalite()
        return

    atomic_dir = Path(args.in_dir)
    if not atomic_dir.exists():
        print(f"Erreur: {atomic_dir} introuvable", file=sys.stderr)
        sys.exit(1)

    total_fiches = 0
    total_conflits = 0
    total_resolu = 0
    total_non_resolu = 0

    for f in sorted(atomic_dir.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            fiche = json.load(fh)
        total_fiches += 1

        conflits = detecter_conflits(fiche)
        if not conflits:
            continue

        for conflit in conflits:
            total_conflits += 1
            resolution = resoudre_conflit(conflit["faits"])
            afficher_conflit(fiche["code"], conflit, resolution)

            if resolution[1] == "resolu_par_confiance":
                total_resolu += 1
            else:
                total_non_resolu += 1

    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"  Fiches analysées  : {total_fiches}")
    print(f"  Conflits détectés : {total_conflits}")
    print(f"  Résolus (confiance): {total_resolu}")
    print(f"  Non résolus (égalité): {total_non_resolu}")


if __name__ == "__main__":
    main()
