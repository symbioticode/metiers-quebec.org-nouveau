#!/usr/bin/env python3
"""Tests for cnp_check.py — CNP×appellations validation."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from cnp_check import cnp_check, load_matrix

MATRIX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "reference", "cnp-appellations-officielles.json"
)


class TestCNPCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrice = load_matrix(MATRIX_PATH)

    # --- CNP exists + exact match ---
    def test_exact_match_appellation_principale(self):
        r = cnp_check("72300", "Plombiers/plombières", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")
        self.assertEqual(r["matched_term"], "Plombiers/plombières")

    def test_exact_match_autre_appellation(self):
        r = cnp_check("21222", "analyste de systèmes", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    def test_exact_match_case_insensitive(self):
        r = cnp_check("72300", "PLOMBIER/PLOMBIÈRE", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    # --- CNP exists + partial match ---
    def test_partial_match_substring(self):
        r = cnp_check("72300", "plombier", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "partielle")

    def test_partial_match_slash_variant(self):
        r = cnp_check("72300", "mécanicien en plomberie", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "partielle")
        self.assertIn("mécanicien", r["matched_term"])

    def test_partial_match_infirmier(self):
        r = cnp_check("31301", "infirmier", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "partielle")

    # --- CNP exists + no match ---
    def test_no_match(self):
        r = cnp_check("72300", "infirmière", self.matrice)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")
        self.assertIsNone(r["matched_term"])

    def test_no_match_unrelated_term(self):
        r = cnp_check("12200", "plombier", self.matrice)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")

    # --- CNP does not exist ---
    def test_nonexistent_cnp(self):
        r = cnp_check("99999", "rien", self.matrice)
        self.assertFalse(r["valide"])
        self.assertFalse(r["cnp_existe"])
        self.assertIsNone(r["appellation_principale"])
        self.assertEqual(r["type_correspondance"], "aucune")

    # --- Matrix structure ---
    def test_matrix_has_all_target_cnps(self):
        profs = self.matrice["professions"]
        for cnp in ["31301", "72300", "21222", "64100", "12200"]:
            self.assertIn(cnp, profs, f"CNP {cnp} missing from matrix")

    def test_matrix_total_professions(self):
        self.assertGreaterEqual(self.matrice["total_professions"], 500)

    def test_target_cnps_have_appellations(self):
        profs = self.matrice["professions"]
        for cnp in ["31301", "72300", "21222", "64100", "12200"]:
            p = profs[cnp]
            self.assertGreater(len(p["autres_appellations"]), 0, f"CNP {cnp} has no autres_appellations")

    # --- 12200 specific ---
    def test_12200_comptable_match(self):
        r = cnp_check("12200", "teneur de livres", self.matrice)
        self.assertTrue(r["valide"])

    def test_12200_no_plombier(self):
        r = cnp_check("12200", "plombier", self.matrice)
        self.assertFalse(r["valide"])

    # --- 64100 specific ---
    def test_64100_vendeur_match(self):
        r = cnp_check("64100", "commis-vendeur", self.matrice)
        self.assertTrue(r["valide"])

    def test_64100_no_infirmier(self):
        r = cnp_check("64100", "infirmier", self.matrice)
        self.assertFalse(r["valide"])

    # --- FIX 1: empty/whitespace/None ---
    def test_empty_string_never_valid(self):
        r = cnp_check("72300", "", self.matrice)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")

    def test_whitespace_only_never_valid(self):
        r = cnp_check("72300", "   \t  ", self.matrice)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")

    def test_none_terme_no_crash(self):
        r = cnp_check("72300", None, self.matrice)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")

    # --- FIX 4: singularize naive ---
    def test_singular_matches_plural_officielle(self):
        r = cnp_check("32101", "Infirmière auxiliaire", self.matrice)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "partielle")


if __name__ == "__main__":
    unittest.main()
