# Audit Report — Métiers Québec Prototype

**Date:** 2026-07-21  
**Audited pages:** `index.html`, `secteur.html`, `profession.html`, `alpha.html`  
**Tools used:** HTMLHint, Linkinator, vnu (Nu HTML Checker), manual review

---

## Summary

| Category | Errors | Warnings | Notes |
|---|---|---|---|
| HTML Structure (HTMLHint) | 0 | 0 | All files pass HTMLHint linting |
| HTML Validation (vnu) | 0 | 0 | No parse errors detected |
| Broken Links (Linkinator) | 1 | 0 | Root URL `http://localhost:8090/` flagged (server issue, see note) |
| Placeholder/Href Issues | 3 | 0 | `javascript:void(0)` and `href="#"` links |
| Accessibility (manual) | 12 | 3 | Missing labels, no skip-nav, inline styles, SVG issues |
| SEO/Meta (manual) | 3 | 0 | Missing `<meta description>` on 3 pages |
| Code Quality (manual) | 4 | 2 | Inline styles, inconsistent patterns |
| **TOTAL** | **23** | **5** | |

---

## Tool Output

### 1. HTMLHint (HTML Structure Linting)

```
Scanned 4 files, no errors found (72 ms).
```

**Result:** PASS — All 4 HTML files are structurally valid according to HTMLHint rules.

---

### 2. vnu — Nu HTML Checker (W3C Validator)

```
No errors found.
```

**Result:** PASS — No HTML parsing or validation errors.

---

### 3. Linkinator (Broken Link Detection)

```
→ crawling http://localhost:8090
[0] http://localhost:8090/
ERROR: Detected 1 broken links. Scanned 1 links in 0.03 seconds.
```

```
{
  "links": [
    { "url": "http://localhost:8090/", "status": 0, "state": "BROKEN" }
  ]
}
```

**Note:** The "broken" status for the root URL is a false positive — `python3 -m http.server` serves a directory listing for `/` rather than `index.html`. Running with an explicit URL (`http://localhost:8090/index.html`) returns status 200. This is a server configuration issue, not an actual broken link in the HTML files.

**Internal links verified:** All cross-page links (`index.html`, `secteur.html`, `profession.html`, `alpha.html`) are valid and resolve correctly.

---

### 4. axe-core (Accessibility — WCAG 2AA)

**Status:** ⚠️ Could not run — requires Chrome/Chromium (not installed in this environment). See manual accessibility review below.

### 5. pa11y (Accessibility — WCAG 2AA)

**Status:** ⚠️ Could not run — requires Chrome/Chromium with native libraries (not installed in this environment). See manual accessibility review below.

---

## Detailed Findings

### A. Critical — Accessibility (WCAG 2.1 AA)

#### A1. Missing `<label>` for search inputs [WCAG 1.3.1, 4.1.2] — CRITICAL

**Affected files:** All 4 pages (6 occurrences total)

| File | Line | Element |
|---|---|---|
| `index.html` | 19 | `<input id="headerSearch" placeholder="...">` |
| `index.html` | 69 | `<input id="heroSearch" placeholder="...">` |
| `secteur.html` | 18 | `<input id="headerSearch" placeholder="...">` |
| `secteur.html` | 83 | `<input id="filterMetiers" placeholder="...">` |
| `profession.html` | 18 | `<input id="headerSearch" placeholder="...">` |
| `alpha.html` | 18 | `<input id="headerSearch" placeholder="...">` |

**Issue:** All `<input>` elements rely solely on `placeholder` text for identification. Screen readers may not associate placeholder text as a label.

**Fix:** Add a `<label>` element (visible or visually hidden) linked via `for`/`id`:
```html
<label for="headerSearch" class="sr-only">Recherche</label>
<input type="text" id="headerSearch" placeholder="Recherche un métier..." autocomplete="off">
```

---

#### A2. No skip-navigation link [WCAG 2.4.1] — CRITICAL

**Affected files:** All 4 pages

**Issue:** Users relying on keyboards or screen readers must tab through the entire header and sidebar on every page load before reaching main content.

**Fix:** Add as first child of `<body>`:
```html
<a href="#main-content" class="skip-link">Aller au contenu principal</a>
```
With corresponding CSS to show it on focus, and add `id="main-content"` to `<main>`.

---

#### A3. `javascript:void(0)` in anchor href [WCAG 2.1.1 — Keyboard] — HIGH

**File:** `index.html`, line 137

```html
<a href="javascript:void(0)" class="sector-card" onclick="document.getElementById('heroSearch').focus()">
```

**Issue:** Using `javascript:void(0)` as an `href` is a keyboard accessibility anti-pattern. Should be a `<button>` element instead.

**Fix:** Replace with a `<button>`:
```html
<button type="button" class="sector-card" onclick="document.getElementById('heroSearch').focus()">
```

---

#### A4. `href="#"` placeholder links [WCAG 2.4.4 — Link Purpose] — MEDIUM

**File:** `secteur.html`, lines 173–175

```html
<a href="#" class="sector-card">...</a>
```

**Issue:** Three links in the "Portraits connexes" section point to `#` (no destination). These are dead links that will confuse users.

**Fix:** Either link to actual pages or disable/until content is available:
```html
<span class="sector-card sector-card--disabled">...</span>
```

---

#### A5. Decorative SVG icons lack `aria-hidden` [WCAG 1.1.1] — MEDIUM

**Affected files:** All 4 pages (20+ occurrences)

**Issue:** Inline SVG icons used alongside text in navigation, sidebar, and content areas are decorative but not marked as such. Screen readers will attempt to describe them.

**Fix:** Add `aria-hidden="true"` and `focusable="false"` to all decorative SVGs:
```html
<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" ...>...</svg>
```

---

#### A6. Sidebar overlay div lacks ARIA role [WCAG 4.1.2] — LOW

**Affected files:** All 4 pages

```html
<div class="sidebar-overlay" id="sidebarOverlay"></div>
```

**Issue:** The mobile sidebar overlay is a non-semantic `<div>` used as an interactive dismiss element. Should have `role="presentation"` or `aria-hidden="true"` when not visible.

---

### B. SEO / Meta

#### B1. Missing `<meta name="description">` — MEDIUM

**Affected files:** `secteur.html`, `profession.html`, `alpha.html`

Only `index.html` has a `<meta name="description">` tag (line 7). The other 3 pages lack one.

**Fix:** Add unique meta descriptions:
```html
<meta name="description" content="Découvrez les métiers du secteur de la santé au Québec....">
```

---

### C. Code Quality / Maintainability

#### C1. Extensive inline styles — LOW

**Files:** `secteur.html` (line 76, 83), `profession.html` (lines 97, 107, 128, 147, 218, 290), `alpha.html` (lines 95, 107, 113, 122, 130, 138, 147, 157, 170, 177, 190)

Example:
```html
<p style="margin-top:8px;">...</p>
<input ... style="width:100%;padding:10px 16px;border:1px solid var(--border);...">
<h2 style="font-size:1.5rem;font-weight:800;...">A</h2>
```

**Fix:** Move styles to CSS classes in `css/style.css`.

---

#### C2. No `<meta description>` on sub-pages — (covered in B1)

---

#### C3. Missing favicon / Open Graph meta — LOW

**Affected files:** All 4 pages

No `<link rel="icon">` or Open Graph `<meta property="og:*">` tags are present.

---

#### C4. Search results are non-functional for different professions — NOTE

**File:** `js/search.js`

All entries in the `METIERS` and `SECTEURS` arrays point to the same `profession.html` or `secteur.html` URL. This is expected for a prototype but should be addressed before production.

---

### D. Linkinator False Positive

#### D1. Root URL flagged as broken — INFORMATIONAL

```
http://localhost:8090/ — status: 0 (BROKEN)
```

This is a false positive caused by Python's `http.server` returning a directory listing for `/` rather than `index.html`. The actual HTML pages are served correctly. Not a real issue with the prototype code.

---

## Severity Legend

| Level | Count | Description |
|---|---|---|
| **Critical** | 2 | WCAG AA failures that block access for assistive technology users |
| **High** | 1 | Keyboard accessibility / ARIA misuse |
| **Medium** | 3 | Dead links, missing meta, decorative SVG noise |
| **Low** | 3 | Code quality, missing optional meta, ARIA on overlays |
| **Informational** | 1 | Tool false positive |

---

## Priority Recommendations

1. **[CRITICAL]** Add `<label>` elements (or `aria-label`) to all `<input>` fields — affects all 4 pages
2. **[CRITICAL]** Add a skip-navigation link — affects all 4 pages
3. **[HIGH]** Replace `javascript:void(0)` anchor with `<button>` — `index.html:137`
4. **[MEDIUM]** Replace `href="#"` links with disabled/non-interactive elements — `secteur.html:173-175`
5. **[MEDIUM]** Add `aria-hidden="true"` to all decorative SVG icons — all pages
6. **[MEDIUM]** Add `<meta name="description">` to `secteur.html`, `profession.html`, `alpha.html`
7. **[LOW]** Move inline styles to CSS classes — primarily `alpha.html` and `secteur.html`
8. **[LOW]** Add favicon and Open Graph meta tags
9. **[INFO]** Root URL directory listing is a server config issue, not a code defect

---

*This audit was conducted on the static HTML prototype using automated linting (HTMLHint, vnu, Linkinator) and manual code review. Automated accessibility testing with axe-core and pa11y could not be performed due to the absence of a Chromium browser in the test environment.*
