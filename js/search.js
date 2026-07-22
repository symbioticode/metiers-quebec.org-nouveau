(function() {
  const METIERS = [
    { name: "Infirmière ou Infirmier", secteur: "Santé", url: "profession.html" },
    { name: "Infirmier auxiliaire", secteur: "Santé", url: "profession.html" },
    { name: "Médecin", secteur: "Santé", url: "profession.html" },
    { name: "Pharmacien", secteur: "Santé", url: "profession.html" },
    { name: "Dentiste", secteur: "Santé", url: "profession.html" },
    { name: "Physiothérapeute", secteur: "Santé", url: "profession.html" },
    { name: "Ergothérapeute", secteur: "Santé", url: "profession.html" },
    { name: "Audiologiste", secteur: "Santé", url: "profession.html" },
    { name: "Optométriste", secteur: "Santé", url: "profession.html" },
    { name: "Chiropraticien", secteur: "Santé", url: "profession.html" },
    { name: "Podiatre", secteur: "Santé", url: "profession.html" },
    { name: "Diététiste", secteur: "Santé", url: "profession.html" },
    { name: "Sage-femme", secteur: "Santé", url: "profession.html" },
    { name: "Vétérinaire", secteur: "Santé", url: "profession.html" },
    { name: "Massothérapeute", secteur: "Santé", url: "profession.html" },
    { name: "Technicien en laboratoire médical", secteur: "Santé", url: "profession.html" },
    { name: "Technologue en imagerie médicale", secteur: "Santé", url: "profession.html" },
    { name: "Technicien ambulancier paramédic", secteur: "Santé", url: "profession.html" },
    { name: "Préposé aux bénéficiaires", secteur: "Santé", url: "profession.html" },
    { name: "Technicien en santé animale", secteur: "Santé", url: "profession.html" },
    { name: "Informaticien", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Analyste informatique", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Développeur web", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Gestionnaire de projet informatique", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Administrateur de bases de données", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Technicien en informatique", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Administrateur réseau", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Secrétaire médical", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Comptable", secteur: "Administration & Informatique", url: "profession.html" },
    { name: "Électricien", secteur: "Électrotechnique", url: "profession.html" },
    { name: "Électromécanicien", secteur: "Électrotechnique", url: "profession.html" },
    { name: "Ingénieur électricien", secteur: "Électrotechnique", url: "profession.html" },
    { name: "Technicien en électronique", secteur: "Électrotechnique", url: "profession.html" },
    { name: "Mécanicien d'avions", secteur: "Aérospatial", url: "profession.html" },
    { name: "Technicien en aérospatiale", secteur: "Aérospatial", url: "profession.html" },
    { name: "Ingénieur aérospatial", secteur: "Aérospatial", url: "profession.html" },
    { name: "Soudeur", secteur: "Métallurgie", url: "profession.html" },
    { name: "Mécanicien industriel", secteur: "Mécanique d'entretien", url: "profession.html" },
    { name: "Mécanicien d'automobiles", secteur: "Mécanique d'entretien", url: "profession.html" },
    { name: "Plombier", secteur: "Bâtiment & Construction", url: "profession.html" },
    { name: "Menuisier", secteur: "Bâtiment & Construction", url: "profession.html" },
    { name: "Maçon", secteur: "Bâtiment & Construction", url: "profession.html" },
    { name: "Couvreur", secteur: "Bâtiment & Construction", url: "profession.html" },
    { name: "Peintre en bâtiment", secteur: "Bâtiment & Construction", url: "profession.html" },
    { name: "Professeur d'école", secteur: "Éducation & Enseignement", url: "profession.html" },
    { name: "Enseignant au collégial", secteur: "Éducation & Enseignement", url: "profession.html" },
    { name: "Professeur d'université", secteur: "Éducation & Enseignement", url: "profession.html" },
    { name: "Éducateur en services de garde", secteur: "Éducation & Enseignement", url: "profession.html" },
    { name: "Technicien en chimie analytique", secteur: "Chimie & Biologie", url: "profession.html" },
    { name: "Biochimiste", secteur: "Chimie & Biologie", url: "profession.html" },
    { name: "Biologiste", secteur: "Chimie & Biologie", url: "profession.html" },
    { name: "Technicien en pharmacie", secteur: "Chimie & Biologie", url: "profession.html" },
    { name: "Policier", secteur: "Protection publique", url: "profession.html" },
    { name: "Pompier", secteur: "Protection publique", url: "profession.html" },
    { name: "Agent de la paix", secteur: "Protection publique", url: "profession.html" },
    { name: "Technicien en prévention sécurité", secteur: "Protection publique", url: "profession.html" },
    { name: "Chauffeur de camion", secteur: "Transport", url: "profession.html" },
    { name: "Technicien en transport aérien", secteur: "Transport", url: "profession.html" },
    { name: "Conducteur de train", secteur: "Transport", url: "profession.html" },
    { name: "Cuisinier", secteur: "Restauration & Tourisme", url: "profession.html" },
    { name: "Chef cuisinier", secteur: "Restauration & Tourisme", url: "profession.html" },
    { name: "Technicien en environnement", secteur: "Environnement & Aménagement", url: "profession.html" },
    { name: "Architecte paysagiste", secteur: "Environnement & Aménagement", url: "profession.html" },
    { name: "Graphiste", secteur: "Communication & Multimédia", url: "profession.html" },
    { name: "Infographiste", secteur: "Communication & Multimédia", url: "profession.html" },
    { name: "Technicien en documentation", secteur: "Communication & Multimédia", url: "profession.html" },
  ];

  const SECTEURS = [
    { name: "Santé", url: "secteur.html" },
    { name: "Administration & Informatique", url: "secteur.html" },
    { name: "Bâtiment & Construction", url: "secteur.html" },
    { name: "Électrotechnique", url: "secteur.html" },
    { name: "Aérospatial", url: "secteur.html" },
    { name: "Éducation & Enseignement", url: "secteur.html" },
    { name: "Chimie & Biologie", url: "secteur.html" },
    { name: "Protection publique", url: "secteur.html" },
    { name: "Dessin & Fabrication mécanique", url: "secteur.html" },
    { name: "Environnement & Aménagement", url: "secteur.html" },
    { name: "Communication & Multimédia", url: "secteur.html" },
    { name: "Restauration & Tourisme", url: "secteur.html" },
    { name: "Métallurgie", url: "secteur.html" },
    { name: "Mécanique d'entretien", url: "secteur.html" },
    { name: "Transport", url: "secteur.html" },
    { name: "Foresterie & Papier", url: "secteur.html" },
    { name: "Lettres & Langues", url: "secteur.html" },
    { name: "Mines & Pétrole", url: "secteur.html" },
    { name: "Mode & Textile", url: "secteur.html" },
    { name: "Sciences naturelles", url: "secteur.html" },
    { name: "Services sociaux & Juridiques", url: "secteur.html" },
    { name: "Soins esthétiques & Beauté", url: "secteur.html" },
  ];

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

  function search(query) {
    if (!query || query.length < 2) return [];
    var results = [];
    SECTEURS.forEach(function(s) {
      if (fuzzyMatch(query, s.name)) {
        results.push({ type: "secteur", name: s.name, url: s.url });
      }
    });
    METIERS.forEach(function(m) {
      if (fuzzyMatch(query, m.name)) {
        results.push({ type: "metier", name: m.name, desc: m.secteur, url: m.url });
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
      var found = search(q);
      renderResults(results, found);
      results.classList.add('active');
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
