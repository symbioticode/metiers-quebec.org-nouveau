# Rapport d'extraction - Offres d'emploi (Phase 2)
**Date:** 2026-07-24
**Objectif:** Extraire les descriptions de tâches brutes de vraies offres d'emploi actives pour 5 codes CNP

## Résumé global

| CNP | Métier | Offres extraites | Taux de succès |
|-----|--------|-------------------|----------------|
| 31301 | Infirmières et infirmiers autorisés | 2 | 100% (jobillico) |
| 72300 | Plombiers | 1 | 100% (jobillico) |
| 21222 | Spécialistes en informatique | 3 | 100% (jobillico) |
| 64100 | Vendeurs de commerce de détail | 2 | 100% (jobillico) |
| 12200 | Techniciens en comptabilité | 0 | 0% - échec partiel |
| **Total** | | **8 offres** | **4/5 métiers avec au moins 1 offre** |

## Détail par site × métier

### Jobillico (jobillico.com)

| CNP | Statut | Détails |
|-----|--------|---------|
| 31301 | ✅ Succès (2 offres) | 16194985 - Multi Options Nursing (infirmier flex), 17204914 - CHSLD Côté-Jardins (infirmier CHSLD) |
| 72300 | ✅ Succès (1 offre) | 16654752 - Groupe Noël inc. (plombier compagnon, cartes CCQ) |
| 21222 | ✅ Succès (3 offres) | 16865571 - Ciao (analyste info), 16999996 - Micrologic (analyste info), 17337443 - CSS Grandes-Seigneuries (analyste spécialisé) |
| 64100 | ✅ Succès (2 offres) | 17323190 - Magasin Latulippe (vendeur archerie), 17332109 - RONA (conseiller vendeur peinture) |
| 12200 | ❌ Échec | Les recherches retournent des postes de contrôleur financier/analyste financier, pas de technicien comptable. |

### Jobboom (jobboom.com)

| CNP | Statut | Détails |
|-----|--------|---------|
| 31301 | ❌ Échec | JS-rendered, pages search retournent 404 ou HTML sans offres |
| 72300 | ❌ Échec | Idem |
| 21222 | ❌ Échec | Idem |
| 64100 | ❌ Échec | Idem |
| 12200 | ❌ Échec | Offre Furneco International expirée/supprimée |

### Emploisdecadres (emploiscadres.com)

| CNP | Statut | Détails |
|-----|--------|---------|
| 31301 | ❌ N/A | Site de cadres/executifs - pas d'offres infirmière |
| 72300 | ❌ N/A | Pas d'offres plombier |
| 21222 | ❌ Échec | Requêtes bloquées (vérification bot/404) |
| 64100 | ❌ N/A | Pas d'offres vendeur détail |
| 12200 | ❌ Échec | Requêtes bloquées |

## Problèmes identifiés

1. **Jobboom**: entièrement JavaScript-rendered - impossible d'extraire des données sans navigateur headless
2. **Emploisdecadres**: blocage actif des bots (vérification Cloudflare ou similaire)
3. **Jobillico anciennes URLs**: plusieurs offres old jobillico retournent 410 Gone (expirées)
4. **CNP 12200 (technicien comptable)**: titre trop spécifique - les sites listent plutôt "comptable", "analyste financier", "contrôleur" qui sont des catégories CNP différentes
5. **Jobillico pages individuelles**: nécessitent JavaScript pour le contenu complet - seuls les extraits de la page de recherche sont accessibles

## Recommandations

- Pour le CNP 12200, élargir la recherche à "comptable" ou "technicien en comptabilité" sur Indeed ou Québec Emploi
- Pour des données plus complètes de jobboom, utiliser un outil comme Playwright ou Puppeteer
- Considérer Indeed.com comme source complémentaire (non-ciblé initialement)
