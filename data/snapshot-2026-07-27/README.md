# Snapshot pré-Sprint-1 (durcissement scraper)

**Date** : 2026-07-27
**Méthode** : `curl` direct sur `https://www.metiers-quebec.org/` (HTML brut, sans JS, sans navigateur), même méthode que l'audit CCW (`docs/audit-claude-code-web-structure-site.md`).
**But** : figer les pages de référence utilisées pour valider les correctifs du Sprint 1 (kb024 → brief scrape-v2-hardening), pour que "mon fix a marché" et "le site a changé entre-temps" restent distinguables.

Pages figées :
- `protection_ambulancier.htm` ← `protection/ambulancier.htm` (référence 20 sections, audit CCW §2.3)
- `batiment_tailleur_pierres.html` ← `batiment/tailleur_pierres.html` (référence 14 sections, audit CCW §2.2 — page historique kb010)
- `batiment_architecte.htm` ← `batiment/architecte.htm`
- `batiment_occupations.html` ← `batiment/occupations.html` (page multi-appellations, audit CCW §2.4)
- `batiment_batiment.htm` ← `batiment/batiment.htm` (page secteur, référence liens 104 total / 73 matchés = ~30% perdus, audit CCW §5.2 S2)
- `protection_protection.htm` ← `protection/protection.htm` (contre-exemple 45/45 liens matchés, 0 perte)

Ce corpus ne doit pas être re-téléchargé pendant le Sprint 1. Toute mesure avant/après (§critères d'acceptation du brief) doit être faite contre ces fichiers figés, pas contre le site live.
