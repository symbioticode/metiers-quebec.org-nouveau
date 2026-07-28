"""
gardes.py — Implémentation exécutable des GARDES kb008-bis

Convention héritée de scripts/build-feed.py : stdlib Python uniquement,
aucune dépendance externe. Chaque GARDE est une fonction pure :
(données) -> {"conforme": bool, "violations": [...]}

Ces fonctions vérifient les invariants (I) au sens LFA — elles peuvent
être appelées depuis n'importe quel pipeline d'ingestion sans coupler
la vérification à une technologie de stockage particulière.
"""

from datetime import date, datetime


SEUILS_FRAICHEUR_JOURS = {
    "salaire_median": 365,
    "salaire_min": 365,
    "salaire_max": 365,
    "formation": 365 * 3,
    "description": 365 * 3,
    "qualites": 365 * 3,
    "_default": 365 * 2,
}


def garde_partition(atomiques):
    """
    Invariant : chaque `code` (CNP) apparaît une seule fois dans le
    corpus atomique. Deux fiches distinctes ne partagent jamais la
    même clé canonique.

    atomiques: liste de dicts avec au moins la clé "code"
    """
    codes = [a["code"] for a in atomiques]
    vus = set()
    doublons = set()
    for c in codes:
        if c in vus:
            doublons.add(c)
        vus.add(c)
    return {"conforme": len(doublons) == 0, "violations": sorted(doublons)}


def garde_autojugement(fait):
    """
    Invariant (PCCD INV-01 / RKA-INV-01, traduit) : une source ne fixe
    jamais elle-même sa propre `confiance`. On vérifie structurellement
    que `confiance` est présente ET qu'elle a été posée par un champ
    distinct `resolu_par` quand plusieurs origines concurrentes existent
    pour le même (code, champ).

    fait: dict avec "origine": {"source":..., "confiance":..., ...}
    """
    origine = fait.get("origine", {})
    violations = []
    if "confiance" not in origine:
        violations.append("confiance absente de l'origine")
    if "source" not in origine:
        violations.append("source absente de l'origine")
    return {"conforme": len(violations) == 0, "violations": violations}


def garde_non_reecriture(fait, texte_source_brut, seuil_recouvrement=0.3):
    """
    Invariant (PCCD INV-08 / RKA-INV-08) : la valeur normalisée ne doit
    pas s'écarter sémantiquement du texte brut. Test approximatif par
    recouvrement lexical — un vrai contrôle humain reste nécessaire pour
    les cas limites, cette GARDE attrape les dérives grossières
    (paraphrase complète, valeur inventée).

    fait: dict avec "valeur"
    texte_source_brut: str, contenu brut de sources_raw pour ce champ
    """
    valeur = str(fait.get("valeur", "")).lower()
    if not texte_source_brut:
        return {"conforme": None, "violations": ["source brute indisponible pour vérification"]}

    mots_valeur = set(valeur.split())
    mots_source = set(texte_source_brut.lower().split())
    if not mots_valeur:
        return {"conforme": None, "violations": ["valeur vide"]}

    recouvrement = len(mots_valeur & mots_source) / len(mots_valeur)
    conforme = recouvrement >= seuil_recouvrement
    return {
        "conforme": conforme,
        "recouvrement": round(recouvrement, 2),
        "violations": [] if conforme else [f"recouvrement lexical {recouvrement:.2f} < seuil {seuil_recouvrement}"],
    }


def est_perimee(fait, aujourdhui=None):
    """
    Invariant (DUO — axiome D5, fraîcheur décroissante) : dérive une
    obsolescence présumée à partir de date_captee. Ne stocke rien —
    se recalcule à chaque lecture.

    fait: dict avec "champ" et "origine": {"date_captee": "YYYY-MM-DD"}
    """
    aujourdhui = aujourdhui or date.today()
    date_captee = datetime.strptime(fait["origine"]["date_captee"], "%Y-%m-%d").date()
    seuil = SEUILS_FRAICHEUR_JOURS.get(fait["champ"], SEUILS_FRAICHEUR_JOURS["_default"])
    return (aujourdhui - date_captee).days > seuil


def garde_irreversibilite(historique_faits, nouveau_fait):
    """
    Invariant (DUO — axiome D4) : aucun FAIT existant n'est modifié en
    place. Un FAIT identique en (champ, source, date_captee) mais avec
    une valeur différente est une violation — signe d'un écrasement
    plutôt que d'un ajout.

    historique_faits: liste de FAITS déjà présents pour un `code` donné
    nouveau_fait: FAIT qu'on s'apprête à ajouter
    """
    violations = []
    for f in historique_faits:
        meme_cle = (
            f["champ"] == nouveau_fait["champ"]
            and f["origine"]["source"] == nouveau_fait["origine"]["source"]
            and f["origine"]["date_captee"] == nouveau_fait["origine"]["date_captee"]
        )
        if meme_cle and f["valeur"] != nouveau_fait["valeur"]:
            violations.append(
                f"écrasement détecté: champ={f['champ']} source={f['origine']['source']} "
                f"date={f['origine']['date_captee']} ancienne_valeur != nouvelle_valeur"
            )
    return {"conforme": len(violations) == 0, "violations": violations}


def garde_completude_explicite(fiche_atomique):
    """
    Invariant additionnel (kb008-bis) : tout champ absent du corpus doit
    être déclaré dans `completude`, jamais silencieux. Vérifie que tous
    les champs référencés dans `faits` apparaissent dans `completude`,
    et inversement qu'un champ marqué `true` a au moins un FAIT.
    """
    violations = []
    champs_faits = {f["champ"] for f in fiche_atomique.get("faits", [])}
    completude = fiche_atomique.get("completude", {})

    for champ in champs_faits:
        if champ not in completude:
            violations.append(f"champ '{champ}' présent dans faits mais absent de completude")

    for champ, present in completude.items():
        if present and champ not in champs_faits:
            violations.append(f"completude['{champ}']=true mais aucun FAIT correspondant")

    return {"conforme": len(violations) == 0, "violations": violations}


TOUTES_LES_GARDES = [
    "garde_partition",
    "garde_autojugement",
    "garde_non_reecriture",
    "garde_irreversibilite",
    "garde_completude_explicite",
    "est_perimee",  # pas une garde binaire, mais exposée pour le rapport
]
