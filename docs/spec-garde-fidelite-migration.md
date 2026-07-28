# Spécification — GARDE de fidélité de migration (`garde_fidelite_migration`)

**Statut** : Spécification — pas d'implémentation du corps de fonction sans validation explicite d'Andrei.
**Référence** : `durcissement-scraper-generateur_v0_1.md §2`, `gardes.py` (convention du module existant).
**Branche** : `experimental/durcissement-checklist-scraper`.

---

## Principe

Une fonction pure, séparée du générateur, jamais appelée pour corriger — seulement pour rapporter. Rejouable à chaque futur changement de `scrape_v2.py`/`generate.py`, sans dépendre d'un audit manuel refait à chaque fois.

## Signature

```python
def garde_fidelite_migration(
    fiche_source: dict,
    fiche_generee: dict,
    section_order: list[str] | None = None,
) -> dict:
    """
    Compare une fiche source (issue du scraper, ex. entrée de
    professions_details.json) avec la fiche générée (sortie du template,
    ex. contenu du fichier /metier/*/index.html) et rapporte les écarts.

    Retourne {"conforme": bool, "violations": list, "couverture": dict}.
    """
```

### Paramètres

| Paramètre | Type | Description |
|---|---|---|
| `fiche_source` | `dict` | Entrée brute de `professions_details.json` avec `sections`, `slug`, `nom` |
| `fiche_generee` | `dict` | Contenu parsé de la page générée `/metier/*/index.html` (sections HTML + contenu textuel extrait) |
| `section_order` | `list[str] \| None` | Ordre et liste des sections cibles à vérifier. Par défaut : `["description", "taches", "milieu", "qualites", "marche", "formation", "admission", "salaires", "placement", "perspectives"]` |

### Retour

```python
{
    "conforme": bool,        # True si aucune violation
    "violations": [
        {
            "type": str,     # "collision" | "key_missing" | "content_empty" | "key_orphan"
            "target": str,   # Nom de la section cible (ex. "salaires", "milieu")
            "detail": str,   # Description lisible de l'écart
            "source_key": str | None,          # Clé brute dans la source (si applicable)
            "generated_key": str | None,       # Clé dans la sortie générée (si applicable)
            "source_len": int | None,          # Longueur en caractères du contenu source
            "generated_len": int | None,       # Longueur en caractères du contenu généré
        }
    ],
    "couverture": {
        "target": {                              # Pour chaque section cible
            "present_in_source": bool,           # La clé existe dans fiche_source["sections"]
            "present_in_generated": bool,        # Du contenu non vide existe dans fiche_generee
            "source_len": int,                   # Caractères dans la source
            "generated_len": int,                # Caractères dans le généré
            "collision": bool,                   # True si cette cible avait une collision dans la source
            "collided_keys": [str],              # Liste des clés brutes en collision
            "winner_key": str | None,            # Clé retenue par "premier match gagne"
            "winner_len": int | None,            # Longueur du contenu retenu
            "loser_keys": [str],                 # Clés perdues par la collision
            "loser_max_len": int | None,         # Longueur maximale perdue
        }
    }
}
```

### Types de violations

| `type` | Déclencheur |
|---|---|
| `"key_missing"` | Une section cible a du contenu dans `fiche_source` mais pas dans `fiche_generee` (clé jamais mappée) |
| `"content_empty"` | Une section cible a une clé dans `fiche_generee` mais son contenu formaté est vide (`fmt()` produit `<p>Information non disponible.</p>`) |
| `"collision"` | Deux ou plusieurs clés brutes de `fiche_source` correspondent à la même cible — signale quelles clés sont en concurrence, laquelle a gagné, et la perte en caractères |
| `"key_orphan"` | Une clé brute dans `fiche_source` n'est mappée vers aucune cible (ex. `LIENS RECOMMANDÉS`, `VOIR AUSSI`, `PROFESSIONS APPARENTÉES`) — à signaler même si c'est un choix de scope, pas un bug |

### Règle de conformité

`conforme = False` si UNE SEULE des conditions suivantes est vraie :
- Au moins une violation de type `"collision"` (toute collision non résolue est un écart — même si la bonne clé a gagné par hasard)
- Au moins une violation de type `"key_missing"` (contenu source présent mais absent du généré)
- Au moins une violation de type `"content_empty"` (section présente mais vide en sortie)

Les `"key_orphan"` ne rendent pas `conforme = False` (ce sont des choix de conception documentés), mais sont listées pour transparence.

---

## Fixture de test qui force `conforme: False`

### Cas : collision admission + section salaires absente

Inspiré du cas `administration1` (audit kb024, collision milieu 26 vs 10062 caractères) et du cas Chorégraphe (salaires absent du généré), mais synthétique pour éviter une dépendance aux données réelles.

```python
# --- Fixture source : fiche avec collision + section manquante ---
FICHE_SOURCE_COLLISION = {
    "slug": "test-collision-administration",
    "nom": "Test Collision Administration",
    "sections": {
        "intro": ["SECTEUR: ADMINISTRATION"],
        "MILIEU DE TRAVAIL": [
            "Le préposé à l'administration travaille dans un bureau."
        ],
        "MILIEUX DE TRAVAIL": [
            # Contenu plus riche, volontairement perdu par le "premier match"
            "Le préposé à l'administration peut travailler dans :\n"
            "- un bureau traditionnel\n"
            "- un environnement gouvernemental\n"
            "- une entreprise privée\n"
            "- un organisme à but non lucratif\n"
            "- un centre d'appels\n"
            "- une institution financière\n"
            "Chaque milieu a ses propres contraintes et avantages."
        ],
        "SALAIRE": [
            # Cette clé ne sera pas mappée par la section_key_map actuelle
            "Le salaire moyen est de 45 000$ par année."
        ],
        "TÂCHES ET RESPONSABILITÉS": [
            "Gère les dossiers administratifs, répond aux demandes."
        ],
        "PLACEMENT": [
            "Bonnes perspectives de placement dans la région."
        ],
        "EXIGENCES DU MARCHÉ DU TRAVAIL": [
            "Un diplôme d'études collégiales est généralement requis."
        ],
        "LIENS RECOMMANDÉS": [
            "https://example.com/info-administration"
        ],
    },
}

# --- Fixture générée : résultat attendu du pipeline actuel ---
FICHE_GENEREE_AVEC_ECARTS = {
    "slug": "test-collision-administration",
    "nom": "Test Collision Administration",
    "sections_generated": {
        "description": "<p>Information non disponible.</p>",
        "taches": "<p>Gère les dossiers administratifs, répond aux demandes.</p>",
        "milieu": "<p>Le préposé à l'administration travaille dans un bureau.</p>",
        # Note : MILIEU DE TRAVAIL (26 mots, gagnant) vs MILIEUX DE TRAVAIL (52 mots, perdant)
        "qualites": "<p>Information non disponible.</p>",
        "marche": "<p>Un diplôme d'études collégiales est généralement requis.</p>",
        "formation": "<p>Information non disponible.</p>",
        "admission": "<p>Information non disponible.</p>",
        "salaires": "<p>Information non disponible.</p>",  # SALAIRE non mappé → absent
        "placement": "<p>Bonnes perspectives de placement dans la région.</p>",
        "perspectives": "<p>Information non disponible.</p>",
    },
}
```

### Assertions attendues sur la fixture

```python
def test_fixture_force_faux():
    resultat = garde_fidelite_migration(FICHE_SOURCE_COLLISION, FICHE_GENEREE_AVEC_ECARTS)
    assert resultat["conforme"] is False
    # Doit contenir au moins :
    # 1. Violation "collision" pour "milieu" (MILIEU DE TRAVAIL vs MILIEUX DE TRAVAIL)
    #    winner = "MILIEU DE TRAVAIL" (26 mots, moins riche)
    #    loser = "MILIEUX DE TRAVAIL" (52 mots, plus riche)
    # 2. Violation "key_missing" pour "salaires" (SALAIRE présent dans source mais pas dans généré)
    # 3. Violation "key_orphan" pour "LIENS RECOMMANDÉS" (non mappé)
    types = [v["type"] for v in resultat["violations"]]
    assert "collision" in types
    assert "key_missing" in types
    assert "key_orphan" in types
```

---

## Notes d'implémentation (pour la phase de code)

### Où placer la fonction

Dans `system-c/scripts/gardes.py`, à côté des GARDES existantes (`garde_partition`, `garde_autojugement`, etc.). La fixture de test va dans `system-c/scripts/test_gardes.py`.

### Dépendances

Aucune en dehors de la stdlib. La fonction ne doit pas importer `generate.py` — elle opère sur les structures de données déjà sérialisées.

### Ce que la GARDE ne fait PAS (périmètre exclu)

- Elle ne rescrape pas le site live. Elle compare `fiche_source` (issue du corpus stocké) à `fiche_generee` (issue du générateur). Pour une vérification bout-en-bout incluant le scraper, voir les scripts dans `data/reference/migration-sens-structure/`.
- Elle ne vérifie pas la fidélité textuelle (reformulation, perte de contenu au sein d'une section correctement mappée) — seulement la présence/absence et les collisions. La vérification sémantique fine est du ressort de `garde_non_reecriture` (déjà existante dans `gardes.py`).
- Elle ne décide pas quel contenu garder en cas de collision — elle le signale seulement.

### Cas particuliers à documenter dans l'implémentation

- `intro` n'est pas une section cible — son contenu est utilisé comme filet de secours pour `description` et `formation`. La GARDE doit l'ignorer comme source directe mais le mentionner comme provenance indirecte si un filet de secours a été activé.
- Les sections vides après formatage (`fmt()` produisant `<p>Information non disponible.</p>`) comptent comme absentes pour le calcul de conformité, même si la clé est techniquement présente.
- L'apostrophe courbe (`'`) et droite (`'`) doivent être normalisées avant comparaison des clés. Sans cette normalisation, la GARDE signalerait de faux écarts pour `EXIGENCES D'ADMISSION` (courbe, 337 fiches) vs `EXIGENCES D'ADMISSION` (droite, 26 fiches).
