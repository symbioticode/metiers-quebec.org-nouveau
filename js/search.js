(function() {
  var SEARCH_INDEX_URL = '/data/search.json';
  var searchIndexPromise = null;

  function loadSearchIndex() {
    if (!searchIndexPromise) {
      searchIndexPromise = fetch(SEARCH_INDEX_URL)
        .then(function(res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        });
    }
    return searchIndexPromise;
  }

  function fuzzyMatch(query, text) {
    query = query.toLowerCase();
    text = text.toLowerCase();
    if (text.includes(query)) return true;
    let qi = 0;
    for (let ti = 0; ti < text.length && qi < query.length; ti++) {
      if (text[ti] === query[qi]) qi++;
    }
    return qi === query.length;
  }

  function search(query, entries) {
    if (!query || query.length < 2) return [];
    var results = [];
    var seenSecteurs = {};

    entries.forEach(function(e) {
      if (!seenSecteurs[e.secteur] && fuzzyMatch(query, e.secteur_nom)) {
        seenSecteurs[e.secteur] = true;
        results.push({ type: 'secteur', name: e.secteur_nom, url: '/secteur/' + e.secteur + '/' });
      }
    });

    entries.forEach(function(e) {
      if (fuzzyMatch(query, e.nom)) {
        results.push({ type: 'metier', name: e.nom, desc: e.secteur_nom, url: '/metier/' + e.slug + '/' });
      }
    });

    return results.slice(0, 15);
  }

  function renderResults(container, results) {
    if (results.length === 0) {
      container.innerHTML = '<div class="search-results__empty">Aucun résultat trouvé</div>';
      return;
    }
    var html = '';
    results.forEach(function(r) {
      var tagClass = r.type === 'secteur' ? 'search-results__item-tag--secteur' : 'search-results__item-tag--metier';
      var tagLabel = r.type === 'secteur' ? 'Secteur' : 'Métier';
      html += '<a href="' + r.url + '" class="search-results__item">';
      html += '<span class="search-results__item-tag ' + tagClass + '">' + tagLabel + '</span>';
      html += '<div><div class="search-results__item-name">' + r.name + '</div>';
      if (r.desc) html += '<div class="search-results__item-desc">' + r.desc + '</div>';
      html += '</div></a>';
    });
    container.innerHTML = html;
  }

  function renderError(container) {
    container.innerHTML = '<div class="search-results__empty">Recherche indisponible pour le moment. Veuillez réessayer plus tard.</div>';
  }

  function setupSearch(inputId, resultsId) {
    var input = document.getElementById(inputId);
    var results = document.getElementById(resultsId);
    if (!input || !results) return;
    input.addEventListener('input', function() {
      var q = this.value.trim();
      if (q.length < 2) {
        results.classList.remove('active');
        return;
      }
      loadSearchIndex().then(function(entries) {
        var found = search(q, entries);
        renderResults(results, found);
        results.classList.add('active');
      }).catch(function() {
        renderError(results);
        results.classList.add('active');
      });
    });
    input.addEventListener('focus', function() {
      if (this.value.trim().length >= 2) {
        results.classList.add('active');
      }
    });
    document.addEventListener('click', function(e) {
      if (!input.contains(e.target) && !results.contains(e.target)) {
        results.classList.remove('active');
      }
    });
  }

  setupSearch('headerSearch', 'headerSearchResults');
  setupSearch('heroSearch', 'heroSearchResults');

  var menuBtn = document.getElementById('menuBtn');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', function() {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', function() {
      if (sidebar) sidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  }

  var backToTop = document.getElementById('backToTop');
  if (backToTop) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 300) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    });
    backToTop.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();
