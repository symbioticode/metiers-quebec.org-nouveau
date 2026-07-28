# Procédure de Scraping — metiers-quebec.org

## Résumé exécutif

Le scraping a permis de récupérer **413 métiers** détaillés sur 458 trouvés (90% de réussite), répartis dans **22 secteurs d'emploi**, pour un total de **446 pages HTML** générées statiquement. Les données incluent les tâches, formation, salaires, perspectives d'emploi et liens recommandés pour chaque métier.

---

## 1. Analyse préliminaire du site source

### 1.1 Structure du site original

Le site `metiers-quebec.org` utilise une architecture **HTML framesets** (Microsoft FrontPage 5.0/2002) :

```
index.html (frameset)
├── gauche: cadre.html (navigation, 25% largeur)
└── droite: accueil.html (page d'accueil)
    └── dropdown JS → /{secteur}/{metier}.htm
```

**Pages clés identifiées :**

| Type | Pattern URL | Exemple |
|------|-------------|---------|
| Accueil | `/` | `accueil.html` (dans frameset) |
| Secteur | `/{secteur}/{secteur}.htm` | `/sante/sante.htm` |
| Métier | `/{secteur}/{metier}.htm` | `/sante/medecin.htm` |
| Index A-Z | `/alphabetique/{lettre}.htm` | `/alphabetique/a.htm` |
| Programmes | `/programmes/{lettre}.htm` | `/programmes/a.htm` |
| Chercheurs | `/chercheurs/chercheur.htm` | — |

### 1.2 Décision : Pas de robots.txt ni sitemap

**Constat :** Le site n'a ni `robots.txt` ni `sitemap.xml`.

**Décision :** Respecter un delai de 0.3s entre les requêtes pour ne pas surcharger le serveur. Le site est maintenu par une seule personne (projet éducatif du gouvernement du Québec).

### 1.3 Encoding : windows-1252 vs UTF-8

**Constat :** Le `meta charset` déclare `windows-1252`, mais l'analyse des octets bruts révèle que **certains pages sont en UTF-8** malgré cette déclaration.

**Preuve :**
```
Page /sante/medecin.htm :
  - Meta charset : windows-1252
  - Octets bruts : Valide en windows-1252 (0 Ã trouvé)
  - Résultat : OK

Page /transport/transport1.html :
  - Meta charset : windows-1252
  - Octets bruts : Contient des séquences UTF-8 (Ã©, Ã¨, dâ€™)
  - Résultat : Mojibake si décodé en windows-1252
```

**Décision :** Implémenter une **détection d'encodage automatique** qui :
1. Vérifie le BOM (Byte Order Mark)
2. Essaie UTF-8 en premier
3. Détecte les motifs de mojibake (`Ã©`, `â€™`, etc.) pour identifier les pages UTF-8 mal déclarées
4. Fallback sur windows-1252

---

## 2. Architecture du scraper

### 2.1 Fichiers

```
scraper/
├── scrape_v2.py      # Script principal de scraping
├── generate.py       # Générateur de site statique
└── fix_encoding.py   # Correction d'encodage (obsolète après fix)
```

### 2.2 Pipeline en 3 étapes

```
Étape 1: Index alphabétique → URLs de tous les métiers
    ↓
Étape 2: Pages de secteurs → Relations secteur-métier
    ↓
Étape 3: Pages de métiers → Données structurées détaillées
```

**Pourquoi cet ordre ?**
- L'index alphabétique est la source la plus fiable pour obtenir la **liste complète** des métiers (pas de JavaScript requis, pas de frames).
- Les pages de secteurs servent de **référence croisée** pour mapper les métiers aux secteurs.
- Le scraping détaillé est le plus coûteux (413 requêtes) et doit être fait en dernier.

### 2.3 Détection d'encodage

```python
def detect_encoding(raw_bytes):
    # 1. BOM (Byte Order Mark)
    if raw_bytes[:3] == b'\xef\xbb\xbf':  # UTF-8 BOM
        return 'utf-8-sig'
    
    # 2. Essayer UTF-8
    try:
        text = raw_bytes.decode('utf-8')
        if any(c in text for c in 'àâäéèêëïîôùûüÿçœæ'):
            return 'utf-8'
    except UnicodeDecodeError:
        pass
    
    # 3. Détecter mojibake dans windows-1252
    text_1252 = raw_bytes.decode('windows-1252', errors='replace')
    utf8_indicators = ['â€™', 'Ã©', 'Ã¨', 'Ã ', 'Ã§', 'Ã®']
    for indicator in utf8_indicators:
        if indicator in text_1252:
            # Ré-interpréter comme UTF-8
            return 'utf-8-as-1252'
    
    return 'windows-1252'
```

**Résultat :** Après implémentation, **0 mojibake** dans les 413 métiers récupérés.

---

## 3. Extraction des URLs de métiers

### 3.1 Source : Index alphabétique

Les 20 pages `/alphabetique/{lettre}.htm` contiennent la liste de tous les métiers avec des liens hypertextes.

**Pattern de traitement :**
```python
# Extraire tous les liens <a href="...">texte</a>
links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', html)

# Filtrer les liens de navigation
if not any(x in href.lower() for x in [
    "accueil", "cadre", "alphabetique", "programmes",
    "javascript", "#", ".pdf", "portrait"
]):
    professions[href] = text
```

**Résultat :** 458 métiers uniques trouvés.

### 3.2 Décision : Filtrer les liens non-métier

**Pourquoi ?** Les pages alphabétiques contiennent aussi des liens de navigation (retour, accueil, secteurs) et des liens vers des programmes d'études. Le filtre élimine :
- Liens contenant `accueil`, `cadre`, `alphabetique` (navigation)
- Liens vers `.pdf` (documents externes)
- Liens `javascript:` (interactions JS)
- Liens `#` (ancres internes)
- Liens vers `portrait` (pages d'information)

---

## 4. Récupération des secteurs

### 4.1 Extraction depuis les pages de secteurs

Chaque secteur a une page `/{secteur}/{secteur}.htm` contenant la liste de ses métiers.

**Pattern :**
```python
for slug, name in sectors.items():
    html = fetcher.fetch(f"/{slug}/{slug}.htm")
    links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', html)
    professions = filter_and_normalize(links)
```

### 4.2 Secteurs non trouvés (404)

9 secteurs ont retourné une erreur 404 :
- `communication` → `/communication/communication.htm`
- `fabric_mec` → `/fabric_mec/fabric_mec.htm`
- `environnement` → `/environnement/environnement.htm`
- `lettres` → `/lettres/lettres.htm`
- `mecanique_entr` → `/mecanique_entr/mecanique_entr.htm`
- `mines` → `/mines/mines.htm`
- `humaines` → `/humaines/humaines.htm`
- `beaute` → `/beaute/beaute.htm`
- `comptabilite` → `/comptabilite/comptabilite.htm`

**Décision :** Ajouter ces secteurs à la liste avec les noms connus, même sans page de secteur. Les métiers de ces secteurs sont quand même récupérables via l'index alphabétique (leur URL contient le slug du secteur).

---

## 5. Mapping Métier → Secteur

### 5.1 Problème

Les URLs de l'index alphabétique utilisent un format relatif : `/../sante/infirmier.htm`
Les pages de secteurs utilisent un format absolu : `/sante/infirmier.htm`

### 5.2 Solution : Correspondance multi-variantes

```python
# Construire un mapping complet avec toutes les variantes d'URL
url_to_sector = {}
for slug, data in sectors.items():
    for m in data['metiers']:
        variants = set()
        variants.add(raw_url)                     # /../sante/medecin.htm
        variants.add(raw_url.lstrip('/'))          # ../sante/medecin.htm
        fixed = re.sub(r'^/\.\./', '/', raw_url)  # /sante/medecin.htm
        variants.add(fixed)
        
        # Swap extensions .htm ↔ .html
        for v in list(variants):
            if v.endswith('.htm'):
                variants.add(v[:-4] + '.html')
        
        # Juste le nom de fichier
        filename = raw_url.split('/')[-1]
        variants.add(filename)
```

**Résultat :** 413/413 métiers correctement mappés à un secteur.

### 5.3 Dernier recours : Extraction depuis l'URL

```python
# Si pas de correspondance, extraire le secteur depuis le chemin
m = re.search(r'/(\w+)/[^/]+$', url)
if m:
    sector = m.group(1)  # ex: "sante" depuis "/../sante/medecin.htm"
```

---

## 6. Parsing des pages de métiers

### 6.1 HTMLParser personnalisé

Le HTML standard Parser de Python (`html.parser.HTMLParser`) est utilisé car :
- **Pas de dépendances externes** (pas besoin de BeautifulSoup, lxml, etc.)
- **Léger** et rapide
- **Robuste** face au HTML FrontPage mal formé

### 6.2 Extraction des données structurées

Le parser extrait :
- **Texte brut** : via `handle_data()` avec gestion des balises à ignorer (`<script>`, `<style>`)
- **Tableaux** : via `handle_starttag('table')` → `handle_endtag('table')`
- **Liens** : via `handle_starttag('a')` → `handle_endtag('a')`
- **Listes** : via `handle_starttag('li')` → `handle_endtag('li')`

### 6.3 Normalisation des sections

Le site original utilise des en-têtes variables pour les mêmes sections :

| Nom original | Nom normalisé |
|-------------|---------------|
| `TÂCHES ET RESPONSABILITÉS` | `taches` |
| `TACHES ET RESPONSABILITÉS` | `taches` |
| `QUALITÉS ET APTITUDES REQUISES` | `qualites` |
| `QUALITÉS ET APTITUDES` | `qualites` |
| `DONNÉES SALARIALES` | `salaires` |
| `DONNÉE SALARIALE` | `salaires` |
| `EXIGENCES D'ADMISSION` | `admission` |
| `EXIGENCE D'ADMISSION` | `admission` |

**Décision :** Utiliser un dictionnaire de mapping pour normaliser toutes les variantes vers des clés standardisées.

---

## 7. Données récupérées

### 7.1 Statistiques finales

| Métrique | Valeur |
|----------|--------|
| Métiers uniques trouvés | 458 |
| Métiers scrapés avec succès | 413 (90%) |
| Métiers en erreur | 45 (10%) |
| Secteurs identifiés | 22 (+ 8 sans page dédiée) |
| Pages HTML générées | 446 |
| Taille totale du site | 18 Mo |
| Requêtes HTTP totales | ~460 |
| Delai moyen par requête | 0.3s |
| Temps total de scraping | ~2-3 minutes |

### 7.2 Contenu par métier

Chaque fiche métier contient potentiellement :
- Description du métier
- Tâches et responsabilités
- Milieu de travail
- Qualités et aptitudes requises
- Marché du travail (exigences)
- Formation requise
- Conditions d'admission
- Données salariales
- Statistiques de placement
- Perspectives d'emploi
- Liens recommandés
- Métiers similaires (voir aussi)

### 7.3 Causes des 45 erreurs

Les erreurs proviennent principalement de :
- Pages redirigeant vers un autre métier
- Pages avec un format HTML radicalement différent
- Métiers supprimés ou renommés depuis la dernière mise à jour

---

## 8. Génération du site statique

### 8.1 Architecture de sortie

```
dist/
├── index.html                    # Page d'accueil
├── css/style.css                 # Design responsive
├── js/search.js                  # Recherche fuzzy côté client
├── data/search.json              # Index de recherche JSON
├── secteurs/index.html           # Liste des secteurs
├── secteur/{slug}/index.html     # Page par secteur (22 pages)
├── alpha/index.html              # Index alphabétique
└── metier/{slug}/index.html      # Page par métier (413 pages)
```

### 8.2 Template HTML

Chaque page utilise un template commun avec :
- **Header** avec logo et navigation
- **Sidebar** avec navigation contextuelle
- **Breadcrumb** pour la navigation hiérarchique
- **Footer** avec attribution à la source originale
- **Bouton back-to-top** pour l'UX

### 8.3 Recherche côté client

Le fichier `data/search.json` contient un index léger (62 Ko) de tous les métiers. La recherche fuzzy est implémentée en JavaScript pur (pas de framework) avec correspondance partielle sur le nom du métier.

---

## 9. Décisions techniques clés

| Décision | Alternative rejetée | Justification |
|----------|-------------------|---------------|
| Python + urllib | requests, httpx | Pas de dépendances externes (NixOS) |
| HTMLParser stdlib | BeautifulSoup, lxml | Pas de pip install nécessaire |
| Scraping par étapes | Tout en parallèle | Plus facile à debugger, respectueux du serveur |
| windows-1252 détection | Toujours UTF-8 | Le site mélange les encodages |
| JSON pour les données | CSV, SQLite | Simple, lisible, versionnable |
| Générateur statique | Jekyll, Hugo | Pas de dépendances, contrôle total |
| Fichiers séparés | Monolithique | Meilleure maintenabilité |
| Mapping multi-variantes | Regex simple | Gère les variations d'URL (.htm/.html, /../) |

---

## 10. Reproductibilité

Pour relancer le scraping :

```bash
# 1. Scraping complet (~3 minutes)
python3 scraper/scrape_v2.py

# 2. Corriger l'encodage si nécessaire
python3 scraper/fix_encoding.py

# 3. Générer le site
python3 scraper/generate.py

# 4. Copier les assets
cp css/style.css dist/css/
cp js/search.js dist/js/

# 5. Tester localement
cd dist && python3 -m http.server 8080
```

**Note :** Le scraping nécessite un accès Internet et produit ~460 requêtes HTTP vers metiers-quebec.org. Le delai de 0.3s entre les requêtes est inclus par défaut.
