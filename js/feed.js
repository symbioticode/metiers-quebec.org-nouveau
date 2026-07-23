/**
 * feed.js — Module de visualisation du flux Emploi Québec
 *
 * Consomme feed/emploi.json (JSON Feed 1.1) et affiche
 * les items dans une grille filtrable avec modal de détail.
 *
 * Usage: <script src="js/feed.js"></script>
 *        <div id="feed-root"></div>
 */

(function () {
  "use strict";

  const FEED_URL = "feed/emploi.json";

  const TYPE_LABELS = {
    gouvernement_provincial: "Gouvernement QC",
    organisme_institutionnel: "Institution QC",
    donnees_ouvertes: "Données ouvertes",
    federal: "Fédéral Canada",
  };

  const TYPE_COLORS = {
    gouvernement_provincial: "#1e40af",
    organisme_institutionnel: "#7c3aed",
    donnees_ouvertes: "#059669",
    federal: "#dc2626",
  };

  const CATEGORIE_ICONS = {
    emploi: "💼",
    metiers: "🔧",
    formation: "🎓",
    statistiques: "📊",
    marche_du_travail: "📈",
    donnees_ouvertes: "🔓",
    classification: "📋",
  };

  // ─── State ──────────────────────────────────────────────────────────────────
  let feedData = null;
  let filteredItems = [];
  let activeFilters = { type: "all", categorie: "all", tag: "all" };

  // ─── Fetch ──────────────────────────────────────────────────────────────────
  async function fetchFeed() {
    const root = document.getElementById("feed-root");
    if (!root) return;

    root.innerHTML = `<div class="feed-loading">
      <div class="feed-spinner"></div>
      <p>Chargement du flux Emploi Québec…</p>
    </div>`;

    try {
      const resp = await fetch(FEED_URL);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      feedData = await resp.json();
      filteredItems = [...feedData.items];
      renderFeed(root);
    } catch (err) {
      root.innerHTML = `<div class="feed-error">
        <p>❌ Impossible de charger le flux</p>
        <p class="feed-error-detail">${err.message}</p>
        <p class="feed-error-hint">Vérifie que <code>feed/emploi.json</code> existe.</p>
      </div>`;
    }
  }

  // ─── Render ─────────────────────────────────────────────────────────────────
  function renderFeed(root) {
    const items = filteredItems;
    const allTags = collectTags(feedData.items);

    root.innerHTML = `
      <div class="feed-layout">
        ${renderSidebar(items, allTags)}
        <main class="feed-main">
          <div class="feed-header-bar">
            <h2 class="feed-count">${items.length} source${items.length > 1 ? "s" : ""}</h2>
            <div class="feed-search-box">
              <input type="text" id="feedSearch" placeholder="Rechercher…" autocomplete="off" />
            </div>
          </div>
          <div class="feed-grid" id="feedGrid">
            ${items.map(renderCard).join("")}
          </div>
        </main>
      </div>
      <div class="feed-modal-overlay" id="modalOverlay">
        <div class="feed-modal" id="modalContent"></div>
      </div>
    `;

    bindEvents(root);
  }

  function renderSidebar(items, allTags) {
    const types = countBy(items, (i) => i._quebec_emploi?.type_source);
    const categories = countBy(items, (i) => i._quebec_emploi?.categorie);

    return `
      <aside class="feed-sidebar">
        <h3>Filtres</h3>

        <div class="feed-filter-group">
          <h4>Type de source</h4>
          <button class="feed-filter-btn ${activeFilters.type === "all" ? "active" : ""}"
                  data-filter="type" data-value="all">Toutes <span class="badge">${items.length}</span></button>
          ${Object.entries(TYPE_LABELS)
            .map(([key, label]) => {
              const count = types[key] || 0;
              if (count === 0) return "";
              return `<button class="feed-filter-btn ${activeFilters.type === key ? "active" : ""}"
                        data-filter="type" data-value="${key}">
                        <span class="dot" style="background:${TYPE_COLORS[key]}"></span>
                        ${label} <span class="badge">${count}</span>
                      </button>`;
            })
            .join("")}
        </div>

        <div class="feed-filter-group">
          <h4>Catégorie</h4>
          <button class="feed-filter-btn ${activeFilters.categorie === "all" ? "active" : ""}"
                  data-filter="categorie" data-value="all">Toutes</button>
          ${Object.entries(categories)
            .map(([key, count]) => {
              return `<button class="feed-filter-btn ${activeFilters.categorie === key ? "active" : ""}"
                        data-filter="categorie" data-value="${key}">
                        ${CATEGORIE_ICONS[key] || ""} ${key.replace(/_/g, " ")} <span class="badge">${count}</span>
                      </button>`;
            })
            .join("")}
        </div>

        <div class="feed-filter-group">
          <h4>Tags</h4>
          <div class="feed-tags-list">
            ${allTags
              .slice(0, 20)
              .map(
                (tag) =>
                  `<button class="feed-tag ${activeFilters.tag === tag ? "active" : ""}"
                    data-filter="tag" data-value="${tag}">${tag}</button>`
              )
              .join("")}
          </div>
        </div>

        <div class="feed-sidebar-meta">
          <p>Flux JSON Feed 1.1</p>
          <p>15 sources agrégées</p>
          <p><a href="https://jsonfeed.org" target="_blank" rel="noopener">jsonfeed.org</a></p>
        </div>
      </aside>
    `;
  }

  function renderCard(item) {
    const ext = item._quebec_emploi || {};
    const typeColor = TYPE_COLORS[ext.type_source] || "#64748b";
    const typeLabel = TYPE_LABELS[ext.type_source] || ext.type_source;
    const catIcon = CATEGORIE_ICONS[ext.categorie] || "📄";
    const apiBadge = ext.api_disponible
      ? `<span class="feed-badge feed-badge--api" title="API disponible">⚡ API</span>`
      : `<span class="feed-badge feed-badge--noapi" title="Pas d'API">📄 HTML</span>`;
    const dateStr = item.date_modified
      ? new Date(item.date_modified).toLocaleDateString("fr-CA", {
          year: "numeric",
          month: "short",
          day: "numeric",
        })
      : "";

    return `
      <article class="feed-card" data-id="${item.id}">
        <div class="feed-card-top">
          <span class="feed-card-type" style="background:${typeColor}">${typeLabel}</span>
          ${apiBadge}
        </div>
        <h3 class="feed-card-title">${catIcon} ${escapeHtml(item.title)}</h3>
        <p class="feed-card-summary">${escapeHtml(item.summary || item.content_text || "")}</p>
        <div class="feed-card-meta">
          <span class="feed-card-source">${escapeHtml(ext.source_nom || "")}</span>
          <time class="feed-card-date">${dateStr}</time>
        </div>
        <div class="feed-card-tags">
          ${(item.tags || []).slice(0, 4).map((t) => `<span class="feed-card-tag">${t}</span>`).join("")}
        </div>
        <div class="feed-card-formats">
          ${(ext.formats_disponibles || []).map((f) => `<span class="feed-card-format">${f}</span>`).join("")}
        </div>
      </article>
    `;
  }

  // ─── Modal ──────────────────────────────────────────────────────────────────
  function openModal(itemId) {
    const item = feedData.items.find((i) => i.id === itemId);
    if (!item) return;

    const ext = item._quebec_emploi || {};
    const overlay = document.getElementById("modalOverlay");
    const content = document.getElementById("modalContent");

    content.innerHTML = `
      <button class="feed-modal-close" id="modalClose">&times;</button>
      <div class="feed-modal-header">
        <span class="feed-card-type" style="background:${TYPE_COLORS[ext.type_source] || '#64748b'}">
          ${TYPE_LABELS[ext.type_source] || ext.type_source}
        </span>
        <span class="feed-modal-categorie">${CATEGORIE_ICONS[ext.categorie] || ""} ${ext.categorie || ""}</span>
      </div>
      <h2 class="feed-modal-title">${escapeHtml(item.title)}</h2>
      <p class="feed-modal-content">${escapeHtml(item.content_text || "")}</p>

      <div class="feed-modal-details">
        <div class="feed-modal-row">
          <strong>Source :</strong>
          <a href="${escapeAttr(ext.source_url || item.url || "#")}" target="_blank" rel="noopener">
            ${escapeHtml(ext.source_nom || "")} ↗
          </a>
        </div>
        <div class="feed-modal-row">
          <strong>Identifiant :</strong>
          <code>${escapeHtml(item.id)}</code>
        </div>
        <div class="feed-modal-row">
          <strong>Région :</strong> ${escapeHtml(ext.region || "Quebec")}
        </div>
        <div class="feed-modal-row">
          <strong>API :</strong>
          ${ext.api_disponible ? '<span class="feed-badge feed-badge--api">⚡ Disponible</span>' : '<span class="feed-badge feed-badge--noapi">Non disponible</span>'}
        </div>
        <div class="feed-modal-row">
          <strong>Formats :</strong>
          ${(ext.formats_disponibles || []).map((f) => `<span class="feed-card-format">${f}</span>`).join(" ")}
        </div>
        <div class="feed-modal-row">
          <strong>Tags :</strong>
          ${(item.tags || []).map((t) => `<span class="feed-card-tag">${t}</span>`).join(" ")}
        </div>
        <div class="feed-modal-row">
          <strong>Dernière MAJ :</strong>
          ${ext.derniere_mise_a_jour ? new Date(ext.derniere_mise_a_jour).toLocaleDateString("fr-CA", { year: "numeric", month: "long", day: "numeric" }) : "—"}
        </div>
      </div>

      <div class="feed-modal-actions">
        <a href="${escapeAttr(item.url || "#")}" class="feed-btn feed-btn--primary" target="_blank" rel="noopener">
          Ouvrir la source ↗
        </a>
        <button class="feed-btn feed-btn--secondary" onclick="navigator.clipboard.writeText('${escapeAttr(item.id)}')">
          Copier l'ID
        </button>
      </div>
    `;

    overlay.classList.add("open");
    document.getElementById("modalClose").addEventListener("click", closeModal);
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeModal();
    });
  }

  function closeModal() {
    document.getElementById("modalOverlay").classList.remove("open");
  }

  // ─── Filtering ──────────────────────────────────────────────────────────────
  function applyFilters() {
    const root = document.getElementById("feed-root");
    if (!feedData) return;

    filteredItems = feedData.items.filter((item) => {
      const ext = item._quebec_emploi || {};
      if (activeFilters.type !== "all" && ext.type_source !== activeFilters.type) return false;
      if (activeFilters.categorie !== "all" && ext.categorie !== activeFilters.categorie) return false;
      if (activeFilters.tag !== "all" && !(item.tags || []).includes(activeFilters.tag)) return false;

      // Search filter
      const searchInput = document.getElementById("feedSearch");
      if (searchInput) {
        const q = searchInput.value.toLowerCase().trim();
        if (q) {
          const haystack = [
            item.title,
            item.summary,
            item.content_text,
            ext.source_nom,
            ext.categorie,
            ...(item.tags || []),
          ]
            .join(" ")
            .toLowerCase();
          if (!haystack.includes(q)) return false;
        }
      }

      return true;
    });

    renderFeed(root);
  }

  // ─── Events ─────────────────────────────────────────────────────────────────
  function bindEvents(root) {
    // Filter buttons
    root.querySelectorAll(".feed-filter-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.dataset.filter;
        const value = btn.dataset.value;
        activeFilters[filter] = value;
        applyFilters();
      });
    });

    // Tag buttons
    root.querySelectorAll(".feed-tag").forEach((btn) => {
      btn.addEventListener("click", () => {
        const value = btn.dataset.value;
        activeFilters.tag = activeFilters.tag === value ? "all" : value;
        applyFilters();
      });
    });

    // Card click → modal
    root.querySelectorAll(".feed-card").forEach((card) => {
      card.addEventListener("click", () => {
        openModal(card.dataset.id);
      });
      card.style.cursor = "pointer";
    });

    // Search
    const searchInput = document.getElementById("feedSearch");
    if (searchInput) {
      let debounce;
      searchInput.addEventListener("input", () => {
        clearTimeout(debounce);
        debounce = setTimeout(applyFilters, 250);
      });
    }
  }

  // ─── Helpers ────────────────────────────────────────────────────────────────
  function collectTags(items) {
    const counts = {};
    items.forEach((item) => {
      (item.tags || []).forEach((t) => {
        counts[t] = (counts[t] || 0) + 1;
      });
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([tag]) => tag);
  }

  function countBy(arr, fn) {
    const counts = {};
    arr.forEach((item) => {
      const key = fn(item) || "unknown";
      counts[key] = (counts[key] || 0) + 1;
    });
    return counts;
  }

  function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function escapeAttr(str) {
    return (str || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
  }

  // ─── Init ───────────────────────────────────────────────────────────────────
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fetchFeed);
  } else {
    fetchFeed();
  }

  // Expose for debugging
  window.EmploiFeed = { fetchFeed, applyFilters, feedData: () => feedData };
})();
