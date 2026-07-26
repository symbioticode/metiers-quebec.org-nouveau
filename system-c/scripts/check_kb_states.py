#!/usr/bin/env python3
"""
check_kb_states.py — Lint structurel des KB System C.

Vérifie UNIQUEMENT ce qui est scriptable (voir plan-cloture-hypotheses.md §1-6) :
- présence des deux champs d'état (proposé / confirmé)
- valeurs dans l'énumération autorisée
- présence de la ligne de risque résiduel (§6)
- (si un dossier git est fourni) ordre seuil → résultat → verdict (§3)

Ne juge JAMAIS si un état est épistémiquement justifié — seulement s'il est
présent, bien formé, et cohérent structurellement. Toute anomalie de contenu
(la valeur elle-même, la qualité d'un diagnostic) reste hors de portée par
conception : voir la distinction scriptable/non-scriptable du protocole.

Usage :
    python3 check_kb_states.py <dossier_kb> [--git-dir <chemin_repo_git>]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ETATS_VALIDES = {
    "corroborée", "infirmée", "contradictoire", "indéterminée",
    "principe — non fermable (proposé)",
    "principe — non fermable (confirmé)",
    "en attente",
}

TYPES_VALIDES = {"kb", "hx", "mixte"}

DOC_TYPE_RE = re.compile(
    r"\*\*Type de document\*\*\s*:\s*(KB|Hx|Mixte)\b", re.IGNORECASE
)

# Bloc d'hypothèse nommé, à l'intérieur d'un KB de type Mixte :
#   ### <identifiant libre — H4a, D/L/C, question-centrale, etc.>
#   **État proposé (auteur)** : ...
#   **État confirmé (relecture indépendante)** : ...
BLOC_HYPOTHESE_RE = re.compile(
    r"^#{2,4}\s*(.+?)\s*\n\s*\*\*État proposé \(auteur\)\*\*\s*:\s*(.+?)\s*\n"
    r"\s*\*\*État confirmé \(relecture indépendante\)\*\*\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

CHAMP_PROPOSE_RE = re.compile(
    r"\*\*État proposé \(auteur\)\*\*\s*:\s*(.+)", re.IGNORECASE
)
CHAMP_CONFIRME_RE = re.compile(
    r"\*\*État confirmé \(relecture indépendante\)\*\*\s*:\s*(.+)", re.IGNORECASE
)
RISQUE_RESIDUEL_RE = re.compile(
    r"\*\*Risque résiduel non couvert par ce protocole\*\*\s*:\s*(.+)", re.IGNORECASE
)


def normalize(val: str) -> str:
    return val.strip().strip(".").lower()


def check_hypothese_block(name: str, prop: str, conf: str) -> list[str]:
    """Valide un bloc d'hypothèse individuel (nom + état proposé + état confirmé)."""
    problems = []
    v_prop, v_conf = normalize(prop), normalize(conf)

    if v_prop not in ETATS_VALIDES:
        problems.append(f"§1 — bloc '{name}' : état proposé hors énumération : '{prop.strip()}'")
    if v_conf not in ETATS_VALIDES:
        problems.append(f"§1 — bloc '{name}' : état confirmé hors énumération : '{conf.strip()}'")
    if v_prop == "principe — non fermable (proposé)":
        # même règle §5 que pour un fichier Hx simple, mais scoped au bloc :
        # on exige juste la présence du mot dans le voisinage du bloc — la
        # vérification stricte par en-tête reste faite globalement au niveau
        # fichier (voir check_kb_file), ce test-ci sert de garde-fou minimal.
        pass  # couvert par la vérification globale ci-dessous
    return problems


def check_kb_file(path: Path) -> list[str]:
    """
    Retourne une liste d'anomalies structurelles. Vide = conforme.

    Le comportement dépend du **Type de document** déclaré :
    - KB     : chronique de projet, PAS un test d'hypothèse. Aucun champ
               d'état exigé — un KB documente le contenu, le code, les bugs,
               les hypothèses en cours, sans lui-même porter un verdict.
    - Hx     : un seul test d'hypothèse, un seul couple d'états au niveau du
               fichier (comportement historique du script).
    - Mixte  : un fichier de session contenant plusieurs hypothèses/questions
               distinctes, chacune avec son propre bloc d'état (## <nom> +
               les deux champs) — pas de split en fichiers séparés exigé, la
               lecture humaine n'est pas la contrainte principale ici.
    - (absent) : anomalie — tout KB doit désormais déclarer son type.
    """
    problems = []
    text = path.read_text(encoding="utf-8", errors="replace")

    m_type = DOC_TYPE_RE.search(text)
    if not m_type:
        return ["§0 — champ 'Type de document' (KB/Hx/Mixte) absent — classification requise"]

    doc_type = m_type.group(1).lower()

    if doc_type == "kb":
        # Chronique de projet : pas de vérification d'état. Une hypothèse
        # mentionnée en son sein reste au niveau de la prose, pas d'un champ
        # structuré — ce n'est pas ce type de document qui la ferme.
        return []

    if doc_type == "hx":
        m_prop = CHAMP_PROPOSE_RE.search(text)
        m_conf = CHAMP_CONFIRME_RE.search(text)
        m_risk = RISQUE_RESIDUEL_RE.search(text)

        if not m_prop:
            problems.append("§1 — champ 'État proposé (auteur)' absent")
        else:
            val = normalize(m_prop.group(1))
            if val not in ETATS_VALIDES:
                problems.append(f"§1 — État proposé hors énumération : '{m_prop.group(1).strip()}'")

        if not m_conf:
            problems.append("§1 — champ 'État confirmé (relecture indépendante)' absent")
        else:
            val = normalize(m_conf.group(1))
            if val not in ETATS_VALIDES:
                problems.append(f"§1 — État confirmé hors énumération : '{m_conf.group(1).strip()}'")

        if m_prop and not m_conf:
            problems.append(
                "§1 — incohérence : état proposé présent sans champ confirmé "
                "(même 'EN ATTENTE' doit être écrit explicitement)"
            )

        if m_prop and "principe" in normalize(m_prop.group(1)):
            if not re.search(r"^#{1,4}\s*diagnostic\b", text, re.IGNORECASE | re.MULTILINE):
                problems.append(
                    "§5 — 'PRINCIPE — non fermable' proposé sans en-tête markdown "
                    "'## Diagnostic' (ou niveau équivalent) identifiable dans le document"
                )

        if not m_risk:
            problems.append("§6 — ligne 'Risque résiduel non couvert par ce protocole' absente")
        elif not m_risk.group(1).strip():
            problems.append("§6 — ligne de risque résiduel présente mais vide")

        return problems

    if doc_type == "mixte":
        blocs = BLOC_HYPOTHESE_RE.findall(text)
        if not blocs:
            problems.append(
                "§1 — type 'Mixte' déclaré mais aucun bloc d'hypothèse (## <nom> + "
                "État proposé + État confirmé) détecté"
            )
        for name, prop, conf in blocs:
            problems.extend(check_hypothese_block(name, prop, conf))
            if "principe" in normalize(prop):
                # cherche un en-tête Diagnostic n'importe où après ce bloc
                # (vérification globale, pas positionnelle stricte — un Mixte
                # peut organiser ses diagnostics différemment).
                if not re.search(r"^#{1,4}\s*diagnostic\b", text, re.IGNORECASE | re.MULTILINE):
                    problems.append(
                        f"§5 — bloc '{name}' : 'PRINCIPE — non fermable' sans en-tête "
                        f"'## Diagnostic' identifiable dans le document"
                    )

        m_risk = RISQUE_RESIDUEL_RE.search(text)
        if not m_risk:
            problems.append(
                "§6 — aucune ligne 'Risque résiduel non couvert par ce protocole' "
                "trouvée dans ce document Mixte (au moins une, globale, exigée)"
            )
        elif not m_risk.group(1).strip():
            problems.append("§6 — ligne de risque résiduel présente mais vide")

        return problems

    return [f"§0 — Type de document non reconnu : '{m_type.group(1)}'"]


def check_git_commit_order(git_dir: Path, branch: str = "HEAD") -> list[str]:
    """
    §3 — vérifie que, pour chaque triplet de commits identifiés par leur
    message ('seuil pré-enregistré — X', 'résultat — X', 'verdict — X'),
    l'ordre chronologique est respecté (seuil avant résultat avant verdict).
    Vérification purement mécanique sur les messages de commit + horodatage —
    ne juge jamais le contenu des commits.
    """
    problems = []
    try:
        log = subprocess.run(
            ["git", "-C", str(git_dir), "log", branch, "--format=%H|%ct|%s"],
            capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
    except subprocess.CalledProcessError as e:
        return [f"§3 — impossible de lire git log ({e})"]

    commits = []
    for line in log:
        h, ts, msg = line.split("|", 2)
        commits.append((h, int(ts), msg))

    # regrouper par nom de test entre crochets/tirets dans le message
    tests: dict[str, dict[str, tuple[str, int]]] = {}
    for h, ts, msg in commits:
        m = re.match(r"(seuil pré-enregistré|résultat|verdict)\s*—\s*(.+)", msg, re.IGNORECASE)
        if m:
            kind, name = m.group(1).lower(), m.group(2).strip()
            tests.setdefault(name, {})[kind] = (h, ts)

    for name, kinds in tests.items():
        if "seuil pré-enregistré" in kinds and "résultat" in kinds:
            if kinds["seuil pré-enregistré"][1] >= kinds["résultat"][1]:
                problems.append(
                    f"§3 — test '{name}' : commit résultat antérieur ou simultané "
                    f"au commit de seuil — test disqualifié d'office"
                )
        if "résultat" in kinds and "verdict" in kinds:
            if kinds["résultat"][1] >= kinds["verdict"][1]:
                problems.append(
                    f"§3 — test '{name}' : commit verdict antérieur ou simultané "
                    f"au commit de résultat"
                )
        if "verdict" in kinds and "seuil pré-enregistré" not in kinds:
            problems.append(
                f"§3 — test '{name}' : verdict présent sans commit de seuil "
                f"pré-enregistré identifiable — non vérifiable, à traiter comme "
                f"seuil non pré-enregistré"
            )

    return problems


def main():
    ap = argparse.ArgumentParser(description="Lint structurel des KB System C")
    ap.add_argument("kb_dir", type=Path, help="Dossier contenant les fichiers KB (.md)")
    ap.add_argument("--git-dir", type=Path, default=None,
                     help="Dépôt git à vérifier pour l'ordre des commits (§3)")
    ap.add_argument("--branch", default="HEAD")
    args = ap.parse_args()

    total_problems = 0
    files = sorted(args.kb_dir.glob("*.md"))
    if not files:
        print(f"Aucun fichier .md trouvé dans {args.kb_dir}")
        sys.exit(1)

    for f in files:
        problems = check_kb_file(f)
        if problems:
            total_problems += len(problems)
            print(f"\n{f.name} :")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"{f.name} : conforme (forme uniquement — pas un jugement de fond)")

    if args.git_dir:
        print(f"\n--- Vérification §3 (ordre des commits, {args.git_dir}) ---")
        git_problems = check_git_commit_order(args.git_dir, args.branch)
        if git_problems:
            total_problems += len(git_problems)
            for p in git_problems:
                print(f"  - {p}")
        else:
            print("  aucun triplet seuil/résultat/verdict trouvé, ou tous dans le bon ordre")

    print(f"\nTotal anomalies structurelles : {total_problems}")
    sys.exit(1 if total_problems else 0)


if __name__ == "__main__":
    main()
