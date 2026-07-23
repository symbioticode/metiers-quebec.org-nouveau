"""
test_gardes.py — Phase 1 : validation isolée des GARDES kb008-bis

Stdlib unittest uniquement. Fixtures synthétiques inspirées des cas
réels documentés dans kb002.md (infirmier, salaire) et kb005.md
(couverture source vs pipeline).

Usage:
    python3 test_gardes.py -v
"""

import unittest
from datetime import date

from gardes import (
    garde_partition,
    garde_autojugement,
    garde_non_reecriture,
    est_perimee,
    garde_irreversibilite,
    garde_irreversibilite_corpus,
    garde_completude_explicite,
)


class TestGardePartition(unittest.TestCase):
    def test_codes_uniques_conforme(self):
        atomiques = [{"code": "31301"}, {"code": "11101"}, {"code": "72200"}]
        r = garde_partition(atomiques)
        self.assertTrue(r["conforme"])
        self.assertEqual(r["violations"], [])

    def test_code_duplique_detecte(self):
        # Cas inspiré du bug vendeur/vendeur_autos (kb008) transposé au CNP
        atomiques = [{"code": "31301"}, {"code": "31301"}, {"code": "11101"}]
        r = garde_partition(atomiques)
        self.assertFalse(r["conforme"])
        self.assertIn("31301", r["violations"])


class TestGardeAutojugement(unittest.TestCase):
    def test_origine_complete_conforme(self):
        fait = {
            "champ": "salaire_median",
            "valeur": 78000,
            "origine": {"source": "isq", "confiance": "haute", "date_captee": "2026-05-01"},
        }
        r = garde_autojugement(fait)
        self.assertTrue(r["conforme"])

    def test_confiance_manquante_viole(self):
        # Un ingesteur qui produirait un FAIT sans confiance forcerait
        # implicitement la résolution -- doit être rejeté avant stockage
        fait = {
            "champ": "salaire_median",
            "valeur": 78000,
            "origine": {"source": "isq", "date_captee": "2026-05-01"},
        }
        r = garde_autojugement(fait)
        self.assertFalse(r["conforme"])
        self.assertIn("confiance absente de l'origine", r["violations"])


class TestGardeNonReecriture(unittest.TestCase):
    def test_valeur_fidele_au_brut(self):
        # Texte brut inspiré de kb002 : section TÂCHES ET RESPONSABILITÉS
        brut = "dans les hôpitaux et cliniques, prodigue des soins infirmiers aux patients"
        fait = {"valeur": "prodigue des soins infirmiers aux patients dans les hôpitaux"}
        r = garde_non_reecriture(fait, brut)
        self.assertTrue(r["conforme"])

    def test_valeur_inventee_detectee(self):
        brut = "dans les hôpitaux et cliniques, prodigue des soins infirmiers aux patients"
        fait = {"valeur": "pilote des avions long-courrier pour une compagnie aérienne"}
        r = garde_non_reecriture(fait, brut)
        self.assertFalse(r["conforme"])

    def test_source_brute_absente_signale(self):
        fait = {"valeur": "quelque chose"}
        r = garde_non_reecriture(fait, "")
        self.assertIsNone(r["conforme"])


class TestFraicheur(unittest.TestCase):
    def test_salaire_recent_pas_perime(self):
        fait = {"champ": "salaire_median", "origine": {"date_captee": "2026-06-01"}}
        self.assertFalse(est_perimee(fait, aujourdhui=date(2026, 7, 22)))

    def test_salaire_vieux_perime(self):
        # > 365 jours -> périmé
        fait = {"champ": "salaire_median", "origine": {"date_captee": "2023-01-01"}}
        self.assertTrue(est_perimee(fait, aujourdhui=date(2026, 7, 22)))

    def test_description_plus_tolerante(self):
        # Une description de 2 ans n'est pas périmée (seuil 3 ans) alors
        # qu'un salaire de 2 ans le serait (seuil 1 an)
        fait_desc = {"champ": "description", "origine": {"date_captee": "2024-07-01"}}
        fait_sal = {"champ": "salaire_median", "origine": {"date_captee": "2024-07-01"}}
        self.assertFalse(est_perimee(fait_desc, aujourdhui=date(2026, 7, 22)))
        self.assertTrue(est_perimee(fait_sal, aujourdhui=date(2026, 7, 22)))


class TestGardeIrreversibilite(unittest.TestCase):
    def test_ajout_nouvelle_date_conforme(self):
        historique = [
            {"champ": "salaire_median", "valeur": 75000,
             "origine": {"source": "isq", "date_captee": "2025-05-01"}}
        ]
        nouveau = {"champ": "salaire_median", "valeur": 78000,
                   "origine": {"source": "isq", "date_captee": "2026-05-01"}}
        r = garde_irreversibilite(historique, nouveau)
        self.assertTrue(r["conforme"])  # dates différentes -> ajout légitime

    def test_ecrasement_meme_cle_detecte(self):
        historique = [
            {"champ": "salaire_median", "valeur": 75000,
             "origine": {"source": "isq", "date_captee": "2026-05-01"}}
        ]
        nouveau = {"champ": "salaire_median", "valeur": 99999,
                   "origine": {"source": "isq", "date_captee": "2026-05-01"}}
        r = garde_irreversibilite(historique, nouveau)
        self.assertFalse(r["conforme"])


class TestGardeIrreversibiliteCorpus(unittest.TestCase):
    """Variante statique -- exécutable directement sur data/atomic/, sans
    avoir besoin de relancer l'ingesteur. C'est celle-ci que le smoke test
    appelle en pratique."""

    def test_faits_coherents_conforme(self):
        faits = [
            {"champ": "salaire_median", "valeur": 75000,
             "origine": {"source": "isq", "date_captee": "2025-05-01"}},
            {"champ": "salaire_median", "valeur": 78000,
             "origine": {"source": "isq", "date_captee": "2026-05-01"}},
        ]
        r = garde_irreversibilite_corpus(faits)
        self.assertTrue(r["conforme"])

    def test_meme_cle_valeurs_divergentes_detecte(self):
        # Deux FAITS avec exactement la même (champ, source, date_captee)
        # mais des valeurs différentes -- signe d'un écrasement en amont
        faits = [
            {"champ": "salaire_median", "valeur": 75000,
             "origine": {"source": "isq", "date_captee": "2026-05-01"}},
            {"champ": "salaire_median", "valeur": 99999,
             "origine": {"source": "isq", "date_captee": "2026-05-01"}},
        ]
        r = garde_irreversibilite_corpus(faits)
        self.assertFalse(r["conforme"])

    def test_cle_incomplete_ignoree_sans_crash(self):
        faits = [{"champ": "salaire_median", "valeur": 75000, "origine": {}}]
        r = garde_irreversibilite_corpus(faits)
        self.assertTrue(r["conforme"])  # signalé ailleurs par garde_autojugement


class TestGardeCompletude(unittest.TestCase):
    def test_completude_alignee_conforme(self):
        fiche = {
            "faits": [{"champ": "salaire_median", "valeur": 78000, "origine": {}}],
            "completude": {"salaire_median": True, "qualites": False},
        }
        r = garde_completude_explicite(fiche)
        self.assertTrue(r["conforme"])

    def test_completude_incoherente_detectee(self):
        # Cas inspiré de kb005 : pipeline affiche "salaire" sans donnée réelle
        fiche = {
            "faits": [],
            "completude": {"salaire_median": True},  # affirme présence sans FAIT
        }
        r = garde_completude_explicite(fiche)
        self.assertFalse(r["conforme"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
