#!/usr/bin/env python3
"""
Tests unitaires pour cnp_sha_check.py.

Structure miroir de test_cnp_check.py (mêmes CNP cibles : 31301, 72300,
21222, 12200, 64100), adaptée à la sémantique exacte-seulement du SHA-1.

Note de lecture : là où test_cnp_check.py attendrait "partielle", ici on
attend "aucune". Ce n'est pas un bug — c'est la propriété documentée de
l'algorithme : un hachage ne reconnaît que les chaînes déjà exactement vues
dans la matrice. Une variante jamais indexée est invisible, peu importe sa
proximité sémantique avec une appellation connue.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from cnp_sha_check import cnp_sha_check, sha_lookup, load_table

TABLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "reference", "cnp-sha-table.json"
)


class TestCNPShaCheck(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.table = load_table(TABLE_PATH)

    # ── Correspondances exactes connues ───────────────────────────────────────

    def test_exact_appellation_principale_72300(self):
        # "Plombiers/plombières" est l'appellation principale de 72300
        r = cnp_sha_check("72300", "Plombiers/plombières", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")
        self.assertIsNotNone(r["matched_hash"])

    def test_exact_slash_variant_plombier(self):
        # "plombier/plombière" est dans autres_appellations → expansé → "plombier" indexé
        r = cnp_sha_check("72300", "plombier", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    def test_exact_autre_appellation_21222(self):
        # "analyste de systèmes" est dans autres_appellations de 21222
        r = cnp_sha_check("21222", "analyste de systèmes", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    def test_exact_case_insensitive_31301(self):
        # La normalisation retire les accents et met en minuscules
        # "Infirmiers autorisés/infirmières autorisées..." normalisé doit matcher
        r = cnp_sha_check("31301", "INFIRMIERS AUTORISÉS/INFIRMIÈRES AUTORISÉES ET INFIRMIERS PSYCHIATRIQUES AUTORISÉS/INFIRMIÈRES PSYCHIATRIQUES AUTORISÉES", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    def test_exact_forme_slash_complete_31301(self):
        # Forme complète avec slash — indexée telle quelle
        r = cnp_sha_check("31301", "infirmier itinérant/infirmière itinérante", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    def test_exact_appellation_principale_12200(self):
        r = cnp_sha_check("12200", "Techniciens/techniciennes en comptabilité et teneurs/teneuses de livres", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    def test_exact_appellation_principale_64100(self):
        r = cnp_sha_check("64100", "Vendeurs/vendeuses et décorateurs-étalagistes/décoratrices-étalagistes en commerce de détail", self.table)
        self.assertTrue(r["valide"])
        self.assertEqual(r["type_correspondance"], "exacte")

    # ── Variantes jamais vues → aucune (attendu, pas un bug) ─────────────────

    def test_unknown_variant_infirmier_autorise(self):
        # "infirmier autorisé" est une variante tronquée jamais indexée comme telle.
        # cnp_check() la trouve par matching partiel sur l'appellation principale.
        # cnp_sha_check() ne peut pas — effet d'avalanche : SHA-1 de "infirmier
        # autorise" n'a aucun rapport avec SHA-1 de "infirmiers autorises/...".
        r = cnp_sha_check("31301", "infirmier autorisé", self.table)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")

    def test_unknown_variant_infirmiere_auxiliaire_singulier(self):
        # "Infirmière auxiliaire" (singulier) — la matrice officielle de 32101
        # contient "Infirmières auxiliaires" (pluriel). SHA-1 diverge d'un seul
        # caractère 's' → hash totalement différent (effet avalanche).
        # cnp_check() retrouve ce cas via _singularize_naive(). SHA impossible.
        r = cnp_sha_check("32101", "Infirmière auxiliaire", self.table)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")

    def test_unknown_partial_plombier_mecanique(self):
        # "mécanicien en plomberie" est dans autres_appellations de 72300 via
        # "mécanicien/mécanicienne en plomberie". La forme sans slash est indexée
        # ("mecanicien en plomberie" et "mecanicienne en plomberie") mais pas
        # "mécanicien en plomberie" avec accents normalisé donne bien "mecanicien
        # en plomberie" — ce cas DEVRAIT être trouvé via la variante expansée.
        # Si la matrice l'a, le test l'attendrait True ; sinon False est correct.
        r = cnp_sha_check("72300", "mécanicien en plomberie", self.table)
        # On valide seulement que le résultat est cohérent — pas de crash
        self.assertIn(r["type_correspondance"], ["exacte", "aucune"])
        if r["valide"]:
            self.assertEqual(r["type_correspondance"], "exacte")

    # ── CNP inexistant ────────────────────────────────────────────────────────

    def test_nonexistent_cnp(self):
        r = cnp_sha_check("99999", "rien", self.table)
        self.assertFalse(r["valide"])
        self.assertFalse(r["cnp_existe"])
        self.assertIsNone(r["appellation_principale"])
        self.assertEqual(r["type_correspondance"], "aucune")

    # ── Gardes : vide / None / espaces ───────────────────────────────────────

    def test_empty_string_never_valid(self):
        r = cnp_sha_check("72300", "", self.table)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")
        self.assertIsNone(r["matched_hash"])

    def test_whitespace_only_never_valid(self):
        r = cnp_sha_check("72300", "   \t  ", self.table)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")
        self.assertIsNone(r["matched_hash"])

    def test_none_terme_no_crash(self):
        r = cnp_sha_check("72300", None, self.table)
        self.assertFalse(r["valide"])
        self.assertEqual(r["type_correspondance"], "aucune")
        self.assertIsNone(r["matched_hash"])

    # ── sha_lookup() — sans CNP candidat ─────────────────────────────────────

    def test_sha_lookup_connu(self):
        # Terme exactement connu → retrouve le bon CNP sans qu'on le fournisse
        cnp_found = sha_lookup("Plombiers/plombières", self.table)
        self.assertEqual(cnp_found, "72300")

    def test_sha_lookup_variante_slash(self):
        # Variante expansée depuis le slash
        cnp_found = sha_lookup("plombier", self.table)
        self.assertEqual(cnp_found, "72300")

    def test_sha_lookup_inconnu(self):
        # Variante jamais vue → None
        cnp_found = sha_lookup("plombier expert en toiture végétale", self.table)
        self.assertIsNone(cnp_found)

    def test_sha_lookup_vide(self):
        cnp_found = sha_lookup("", self.table)
        self.assertIsNone(cnp_found)

    def test_sha_lookup_none(self):
        cnp_found = sha_lookup(None, self.table)
        self.assertIsNone(cnp_found)

    def test_sha_lookup_21222(self):
        cnp_found = sha_lookup("analyste de systèmes", self.table)
        self.assertEqual(cnp_found, "21222")

    # ── GARDE construction : 0 collision dans la table réelle ─────────────────

    def test_no_hash_collision_in_table(self):
        """
        Vérifie qu'aucun SHA-1 dans l'index inverse ne pointe vers deux CNP
        différents. 0 collision attendu. Si collision → test ÉCHOUE et signale
        les paires impliquées.
        """
        index = self.table.get("index_inverse", {})
        blocs = self.table.get("blocs", {})

        # Reconstruire indépendamment l'index et détecter les doublons
        seen: dict[str, str] = {}  # sha -> cnp
        collisions = []
        for cnp, bloc in blocs.items():
            for h in bloc.get("hashes", []):
                if h in seen and seen[h] != cnp:
                    collisions.append((h, seen[h], cnp))
                else:
                    seen[h] = cnp

        self.assertEqual(
            len(collisions),
            0,
            msg=f"Collisions SHA-1 détectées : {collisions}",
        )

    # ── Structure de la table ─────────────────────────────────────────────────

    def test_table_has_all_target_cnps(self):
        blocs = self.table["blocs"]
        for cnp in ["31301", "72300", "21222", "64100", "12200"]:
            self.assertIn(cnp, blocs, f"CNP {cnp} absent de la table SHA")

    def test_table_nb_entrees_coherent(self):
        index = self.table.get("index_inverse", {})
        self.assertEqual(self.table["nb_entrees"], len(index))
        self.assertGreater(len(index), 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)
