# Documentation du prototype

## Pages

### index.html — Page d'accueil

- **Hero** : titre, sous-titre, barre de recherche centrée
- **Stats** : 3 cartes (1 500+ métiers, 32 secteurs, 460+ programmes)
- **Secteurs** : grille de 12 cartes cliquables avec icônes
- **Nouvelles** : liste des actualités (3 entrées)
- **Navigation** : 3 cartes (par secteur, index A-Z, recherche)

### secteur.html — Page secteur

- **Breadcrumb** : Accueil / Santé
- **En-tête** : tag, titre, description
- **Description** : section texte sur le secteur
- **Liste des métiers** : 20 métiers du secteur Santé avec filtre instantané
- **Portraits connexes** : 3 cartes liées

### profession.html — Page métier détaillé

- **Breadcrumb** : Accueil / Santé / Infirmière
- **En-tête** : retour, tag secteur, titre, niveau d'études
- **Méta-cards** : secteur, niveau, salaire, demande
- **Sections de contenu** (9 sections) :
  1. Définition du métier
  2. Formation requise
  3. Salaire
  4. Qualités et aptitudes requises
  5. Milieux de pratique
  6. Employeurs potentiels
  7. Permis de pratique
  8. Portrait de la profession (statistiques)
  9. Professions apparentées (grille de liens)

### alpha.html — Index alphabétique

- **Navigation par lettre** : 26 liens A-Z
- **Listes de métiers** : regroupés par lettre (exemples A, B, C, D, E, I, M, P, S, T, V)

## Composants CSS

| Composant | Classe | Description |
|-----------|--------|-------------|
| Header | `.header` | Barre fixe en haut avec logo, recherche, nav |
| Sidebar | `.sidebar` | Menu latéral fixe avec liens + secteurs |
| Hero | `.hero` | Section centrale accueil |
| Stat card | `.stat-card` | Carte chiffre + label |
| Sector card | `.sector-card` | Carte secteur avec icône |
| News item | `.news-item` | Élément actualité avec date |
| Content section | `.content-section` | Bloc de contenu avec titre icôné |
| Related grid | `.related-grid` | Grille de liens vers métiers apparentés |
| Alpha index | `.alpha-index` | Grille de lettres cliquables |
| Metier link | `.metier-link` | Ligne de liste de métier |
| Search results | `.search-results` | Dropdown de résultats de recherche |
| Breadcrumb | `.breadcrumb` | Fil d'Ariane |
| Back to top | `.back-to-top` | Bouton flottant retour en haut |

## Design tokens

```css
--primary: #1e40af        /* Bleu principal */
--primary-light: #3b82f6  /* Bleu clair */
--accent: #059669         /* Vert accent */
--bg: #f8fafc             /* Fond gris très clair */
--text: #1e293b           /* Texte principal */
--text-light: #64748b     /* Texte secondaire */
--border: #e2e8f0         /* Bordures */
--radius: 12px            /* Border radius défaut */
--sidebar-width: 280px    /* Largeur sidebar */
--header-height: 64px     /* Hauteur header */
```

## Responsive

| Breakpoint | Comportement |
|-----------|-------------|
| > 900px | Sidebar visible, nav header visible |
| ≤ 900px | Sidebar masquée (hamburger), nav header masquée |
| ≤ 600px | Recherche header masquée, stats empilées |

## JavaScript

### Recherche (`js/search.js`)

- **Données** : 65+ métiers et 22 secteurs en mémoire (prototype)
- **Algorithme** : fuzzy matching (incluse + subsequence)
- **Résultats** : max 15, tags couleur (Secteur / Métier)
- **Champs** : header search + hero search (indépendants)

### Navigation

- **Menu hamburger** : toggle sidebar + overlay sur mobile
- **Retour en haut** : bouton flottant visible après 300px de scroll
- **Filtre métiers** : sur la page secteur, filtre instantané par nom
