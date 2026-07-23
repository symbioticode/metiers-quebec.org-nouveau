#!/usr/bin/env python3
"""ingest_imt_manuel.py — Phase 3 : ajout FAITS imt_en_ligne (données réelles).

Stricte stdlib. Ajoute des FAITS salaire_median à des fiches existantes
dans data/atomic/, avec des données réelles curées depuis :
  quebec.ca/emploi/.../explorer-metiers-professions/{CNP}-...

Source : imt_en_ligne (source gouvernementale officielle)
Méthode : manuel (données curées, pas scrapées)
Confiance : haute (source officielle)
Unité : salaire annuel médian (publié sur quebec.ca)

6 métiers (CNP confirmé). Chaque FAIT porte une reference URL pour traçabilité.

Ne produit que des FAITS imt_en_ligne. Ne fabrique pas de FAITS
metiers_quebec — GARDE-NON-RÉÉCRITURE les rejetterait (valeur absente
de corpus_raw_v2).
"""

import json
import sys
from datetime import date
from pathlib import Path

# --- Données réelles curées depuis quebec.ca ---
# Toutes les valeurs : "Salaire annuel en 2020" publié sur la page indiquée.

IMT_SALAIRES = {
    # code slug               CNP     salaire_annuel  reference (URL quebec.ca)
    "infirmier":              (31301,  86000,
        "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/31301-infirmieres-infirmiers-autorises-infirmiers-psychiatriques-autorises"),
    "architecte":             (21200,  74500,
        "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/21200-architectes"),
    "vendeur":                (64100,  40800,
        "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/64100-vendeurs-vendeuses-et-decorateurs-etalagistes-decoratrices-etalagistes-commerce-de-detail"),
    "plombier":               (72300,  61200,
        "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/72300-plombiers-plombieres"),
    "comptabilite":           (12200,  50000,
        "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/12200-techniciens-techniciennes-en-comptabilite-et-teneurs-teneuses-de-livres"),
    "analyste_informatiquel": (21222,  87000,
        "https://www.quebec.ca/emploi/informer-metier-profession/explorer-metiers-professions/21222-specialistes-en-informatique"),
}

IMT_ORIGINE_BASE = {
    "source": "imt_en_ligne",
    "methode": "manuel",
    "confiance": "haute",
}


def ajouter_fait(fiche: dict, champ: str, valeur, origine: dict) -> bool:
    """Ajoute un FAIT à une fiche s'il n'existe pas déjà (champ+source). Retourne True si ajouté."""
    deja_la = any(
        fait["champ"] == champ and fait["origine"]["source"] == origine["source"]
        for fait in fiche["faits"]
    )
    if deja_la:
        return False

    fiche["faits"].append({
        "champ": champ,
        "valeur": valeur,
        "origine": origine,
    })
    fiche["completude"][champ] = True
    return True


def main():
    atomic_dir = Path("data/atomic")
    if not atomic_dir.exists():
        print(f"Erreur: {atomic_dir} introuvable", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    stats = {"lues": 0, "imt": 0}

    for f in sorted(atomic_dir.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            fiche = json.load(fh)
        stats["lues"] += 1
        code = fiche["code"]

        if code in IMT_SALAIRES:
            cnp, salaire, ref = IMT_SALAIRES[code]
            origine = {**IMT_ORIGINE_BASE, "date_captee": today, "reference": ref}
            if ajouter_fait(fiche, "salaire_median", salaire, origine):
                stats["imt"] += 1
                with open(f, "w", encoding="utf-8") as fh:
                    json.dump(fiche, fh, ensure_ascii=False, indent=2)

    print(f"Fiches lues: {stats['lues']}")
    print(f"FAITS imt_en_ligne ajoutés: {stats['imt']}")


if __name__ == "__main__":
    main()
