#!/usr/bin/env python3
"""Rassemble, sans reformulation ni fusion, toutes les fonctions atomiques
candidates déjà nommées dans kb019, kb020 et le test bottom-up second-wave
(docs/kb021-bottom-up-second-wave-test.md), pour servir de corpus d'entrée
au clustering (scripts/cluster_atomic_functions.py) — test H4b de kb021.

Les libellés sont recopiés exactement tels qu'écrits dans chaque KB source,
même quand deux libellés désignent probablement la même chose vue de
l'extérieur (ex. "évaluer une performance individuelle" vs "évaluer le
niveau de maîtrise d'un outil chez un individu") — la déduplication
sémantique est précisément ce que le clustering doit révéler, pas une
étape manuelle en amont qui la présupposerait.

Ce fichier ne fait AUCUNE analyse — extraction brute uniquement.

Sortie : data/reference/onet-genome-stability/atomic-functions-corpus.json
(regroupé avec les autres artefacts du test de stabilité du génome, même
branche/sujet).
"""
import json
from pathlib import Path

OUT = (
    Path(__file__).resolve().parent.parent
    / "data/reference/onet-genome-stability/atomic-functions-corpus.json"
)

# wave "a" = corpus disponible au moment de kb021 initial (kb019 + kb020)
# wave "b" = ajout du test bottom-up second-wave (2026)

ENTRIES = [
    # --- kb019, lecture (a) "coacher une IA" — source: docs/kb019.md ---
    {"fonction": "évaluer une sortie générée par un système contre des critères de qualité", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "comparer deux réponses et classer une préférence", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "annoter/étiqueter des données de sortie", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "détecter des biais/erreurs dans une sortie de système", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "rédiger des instructions/prompts de test", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "documenter des cas limites (edge cases) et rédiger un rapport de correction", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "ajuster des paramètres/règles d'un système", "metier": "Coach IA — lecture (a)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    # --- kb019, lecture (c) "coacher des humains, IA comme outil" ---
    {"fonction": "évaluer une performance individuelle", "metier": "Coach IA — lecture (c)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "transférer une compétence", "metier": "Coach IA — lecture (c)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "élaborer un plan de développement personnel", "metier": "Coach IA — lecture (c)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "animer une séance de suivi individuel", "metier": "Coach IA — lecture (c)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "utiliser un outil logiciel dans sa pratique professionnelle", "metier": "Coach IA — lecture (c)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "consigner/documenter une progression", "metier": "Coach IA — lecture (c)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    # --- kb019, lecture (d) "coacher des humains sur l'usage de l'IA" ---
    {"fonction": "expliquer un concept technique à un public non-technique", "metier": "Coach IA — lecture (d)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "former à l'utilisation d'un outil logiciel", "metier": "Coach IA — lecture (d)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "évaluer le niveau de maîtrise d'un outil chez un individu", "metier": "Coach IA — lecture (d)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "concevoir un programme de formation", "metier": "Coach IA — lecture (d)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},
    {"fonction": "accompagner un changement organisationnel (adoption)", "metier": "Coach IA — lecture (d)", "source": "kb019", "wave": "a", "date": "2026 (kb019)"},

    # --- kb020, 13 métiers — source: docs/kb020.md ---
    {"fonction": "concevoir une instruction textuelle structurée", "metier": "Prompt Engineer", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "tester itérativement une sortie générée", "metier": "Prompt Engineer", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "documenter un patron de requête réutilisable", "metier": "Prompt Engineer", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "comparer deux réponses et classer une préférence", "metier": "AI Trainer", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "annoter des données d'entraînement", "metier": "AI Trainer", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "ajuster des paramètres de modèle", "metier": "AI Trainer", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "évaluer les impacts éthiques/sociaux d'un système", "metier": "AI Ethicist", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "rédiger des lignes directrices de conformité", "metier": "AI Ethicist", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "conseiller une organisation sur un risque réglementaire", "metier": "AI Ethicist", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "superviser une interaction entre opérateur et système automatisé", "metier": "Coordinateur humain-machine", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "arbitrer une décision entre recommandation machine et jugement humain", "metier": "Coordinateur humain-machine", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "assembler des composants logiciels préconstruits sans écrire de code", "metier": "Product Builder no-code", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "configurer une logique métier dans une interface visuelle", "metier": "Product Builder no-code", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "négocier des limites de consentement avec des interprètes", "metier": "Coordinateur d'intimité", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "chorégraphier une scène à contenu sensible", "metier": "Coordinateur d'intimité", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "assurer une médiation entre production et acteurs sur un tournage", "metier": "Coordinateur d'intimité", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "conduire un procédé de fermentation/culture cellulaire à l'échelle industrielle", "metier": "Technicien en bioproduction", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "contrôler la qualité d'un lot biologique", "metier": "Technicien en bioproduction", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "documenter un dossier de lot pharmaceutique", "metier": "Technicien en bioproduction", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "réaliser un geste de soin technique standardisé au domicile d'un patient", "metier": "Intervenant médico-technique à domicile", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "installer/entretenir un équipement médical à domicile", "metier": "Intervenant médico-technique à domicile", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "transmettre une observation clinique à une équipe soignante", "metier": "Intervenant médico-technique à domicile", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "assembler des éléments préfabriqués en atelier (hors chantier)", "metier": "Ouvrier de la construction modulaire hors site", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "monter une structure modulaire en bois ou en acier", "metier": "Ouvrier de la construction modulaire hors site", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "contrôler la conformité d'un module avant expédition", "metier": "Ouvrier de la construction modulaire hors site", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "conduire une ligne de production automatisée", "metier": "Pilote de ligne de production de batteries de véhicules électriques", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "contrôler la qualité de composants électriques en série", "metier": "Pilote de ligne de production de batteries de véhicules électriques", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "ajuster des paramètres de procédé de fabrication", "metier": "Pilote de ligne de production de batteries de véhicules électriques", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "évaluer l'état et la valeur résiduelle d'un objet/matériau", "metier": "Technicien valoriste du réemploi", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "démonter ou remettre en état un bien pour réemploi", "metier": "Technicien valoriste du réemploi", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "orienter un flux de matière vers une filière de valorisation", "metier": "Technicien valoriste du réemploi", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "construire un modèle virtuel synchronisé avec un système physique", "metier": "Spécialiste en jumeau numérique", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "intégrer des flux de données de capteurs dans une simulation", "metier": "Spécialiste en jumeau numérique", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "utiliser une simulation pour prédire une défaillance", "metier": "Spécialiste en jumeau numérique", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "mesurer l'empreinte environnementale d'une infrastructure informatique", "metier": "Responsable Green IT", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "définir une politique de sobriété numérique", "metier": "Responsable Green IT", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},
    {"fonction": "piloter un projet de réduction de consommation énergétique de systèmes IT", "metier": "Responsable Green IT", "source": "kb020", "wave": "a", "date": "2024-2025 (kb020)"},

    # --- second-wave, 11 métiers — source: docs/kb021-bottom-up-second-wave-test.md ---
    {"fonction": "piloter une stratégie d'approvisionnement en énergie", "metier": "Responsable en approvisionnement et performance énergétiques", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "auditer la performance énergétique d'une installation", "metier": "Responsable en approvisionnement et performance énergétiques", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "négocier un contrat d'approvisionnement énergétique", "metier": "Responsable en approvisionnement et performance énergétiques", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "réaliser une inspection technique préliminaire d'un véhicule endommagé", "metier": "Préparateur technique d'actes d'expertise automobile", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "documenter un rapport de préparation pour expert", "metier": "Préparateur technique d'actes d'expertise automobile", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "chiffrer une estimation de réparation", "metier": "Préparateur technique d'actes d'expertise automobile", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "surveiller des sources de renseignement sur les menaces informatiques", "metier": "Expert en renseignement et investigation sur les cybermenaces", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "investiguer un incident de cybersécurité", "metier": "Expert en renseignement et investigation sur les cybermenaces", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "produire un rapport de renseignement sur une menace émergente", "metier": "Expert en renseignement et investigation sur les cybermenaces", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "mesurer une empreinte carbone d'un site industriel", "metier": "Expert en décarbonation et performance environnementale", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "élaborer un plan de décarbonation", "metier": "Expert en décarbonation et performance environnementale", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "conseiller une organisation sur une trajectoire de réduction d'émissions", "metier": "Expert en décarbonation et performance environnementale", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "auditer l'empreinte environnementale d'un tournage", "metier": "Coordinateur écoproduction audiovisuelle et cinéma", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "mettre en œuvre des pratiques de réduction de déchets sur un plateau", "metier": "Coordinateur écoproduction audiovisuelle et cinéma", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "coordonner des fournisseurs pour des choix éco-responsables de production", "metier": "Coordinateur écoproduction audiovisuelle et cinéma", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "concevoir une architecture d'orchestration multi-agents", "metier": "AI Agent Architect", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "définir des garde-fous de performance pour un système autonome", "metier": "AI Agent Architect", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "superviser la collaboration entre plusieurs agents IA", "metier": "AI Agent Architect", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "simuler une attaque adversariale contre un modèle", "metier": "AI Security & Red Teaming Specialist", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "documenter une vulnérabilité découverte", "metier": "AI Security & Red Teaming Specialist", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "recommander un correctif de sécurité pour un système IA", "metier": "AI Security & Red Teaming Specialist", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "analyser comment un contenu est cité par un moteur de génération de réponse", "metier": "GEO/AEO Specialist", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "adapter la structure d'un contenu pour maximiser sa citabilité par une IA", "metier": "GEO/AEO Specialist", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "mesurer la visibilité d'une marque dans des réponses générées", "metier": "GEO/AEO Specialist", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "former des équipes à l'adoption d'un outil IA", "metier": "AI Enablement & Literacy Lead", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "accompagner un changement organisationnel lié à l'IA", "metier": "AI Enablement & Literacy Lead", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "concevoir un programme de littératie IA", "metier": "AI Enablement & Literacy Lead", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "définir une stratégie d'adoption de l'IA à l'échelle de l'organisation", "metier": "Chief AI Officer / CAIO", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "arbitrer des priorités d'investissement technologique", "metier": "Chief AI Officer / CAIO", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "superviser la gouvernance éthique d'une organisation en matière d'IA", "metier": "Chief AI Officer / CAIO", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "auditer la qualité d'un jeu de données destiné à l'entraînement d'un modèle", "metier": "AI Data Governance Manager", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "définir une politique de gouvernance des données", "metier": "AI Data Governance Manager", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
    {"fonction": "assurer la conformité réglementaire d'un pipeline de données", "metier": "AI Data Governance Manager", "source": "second-wave", "wave": "b", "date": "2026 (second-wave)"},
]


def main():
    for i, e in enumerate(ENTRIES):
        e["id"] = i

    n_a = sum(1 for e in ENTRIES if e["wave"] == "a")
    n_b = sum(1 for e in ENTRIES if e["wave"] == "b")
    n_metiers_a = len({e["metier"] for e in ENTRIES if e["wave"] == "a"})
    n_metiers_b = len({e["metier"] for e in ENTRIES if e["wave"] == "b"})

    out = {
        "description": (
            "Corpus brut de fonctions atomiques candidates, recopiées telles quelles "
            "depuis kb019, kb020 et le test bottom-up second-wave — aucune reformulation "
            "ni fusion manuelle. Sert d'entrée au clustering (cluster_atomic_functions.py) "
            "pour le test H4b de kb021 (émergence d'un alphabet par clustering vs "
            "imposition d'une liste de catégories a priori)."
        ),
        "n_fonctions_total": len(ENTRIES),
        "n_fonctions_wave_a": n_a,
        "n_fonctions_wave_b": n_b,
        "n_metiers_wave_a": n_metiers_a,
        "n_metiers_wave_b": n_metiers_b,
        "entrees": ENTRIES,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Fonctions totales: {len(ENTRIES)} (wave a: {n_a}, wave b: {n_b})")
    print(f"Métiers: wave a = {n_metiers_a}, wave b = {n_metiers_b}")
    print(f"Écrit: {OUT}")


if __name__ == "__main__":
    main()
