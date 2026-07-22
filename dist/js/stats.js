/**
 * stats.js — Rendu des graphiques interactifs pour la page Statistiques.
 * Utilise Chart.js v4.5 (chargé via CDN dans stats/index.html).
 */

(function () {
  'use strict';

  var COLORS = {
    primary: '#1e40af',
    primaryLight: '#3b82f6',
    success: '#059669',
    successLight: '#10b981',
    warning: '#d97706',
    warningLight: '#f59e0b',
    danger: '#dc2626',
    dangerLight: '#ef4444',
    purple: '#7c3aed',
    pink: '#ec4899',
    teal: '#14b8a6',
    orange: '#f97316',
    gray: '#6b7280',
    grayLight: '#e5e7eb',
    grayDark: '#374151',
  };

  var SECTOR_COLORS = [
    '#1e40af', '#059669', '#d97706', '#dc2626', '#7c3aed',
    '#ec4899', '#14b8a6', '#f97316', '#2563eb', '#16a34a',
    '#ca8a04', '#b91c1c', '#9333ea', '#db2777', '#0d9488',
    '#ea580c', '#3b82f6', '#22c55e', '#eab308', '#ef4444',
    '#a855f7', '#f472b6',
  ];

  var SLUG_MAP = {
    'Santé': 'sante',
    'Services sociaux et juridiques': 'sociaux',
    'Administration, secrétariat et informatique': 'administration',
    'Arts appliquées et d\'expression': 'arts',
    'Restauration, hôtellerie et tourisme': 'restau_tourisme',
    'Chimie et biologie': 'chimie',
    'Bâtiment et construction': 'batiment',
    'Sciences naturelles': 'nature',
    'Éducation, enseignement et services de garde': 'enseignement',
    'Agriculture, agroalimentaire et pêcheries': 'agriculture',
    'Électrotechnique': 'electrotechnique',
    'Métallurgie': 'metallurgie',
    'Communications graphiques, multimédia et imprimerie': 'graphique',
    'Mode et production textile': 'mode',
    'Protection publique': 'protection',
    'Transport': 'transport',
    'Entretien d\'équipements motorisés': 'motorises',
    'Bois (meubles) et matériaux connexes': 'bois',
    'Sciences physiques et mathématiques': 'physique',
    'Foresterie et papier': 'foresterie',
    'Aérospatial': 'aerospatial',
    'Armée': 'armee',
    'Environnement et aménagement du territoire': 'environnement',
    'Communication, documentation et médias': 'communication',
    'Dessin et fabrication mécanique': 'fabric_mec',
    'Lettres et langues': 'lettres',
    'Mines, pétrole et travaux de génie': 'mines',
    'Sciences et techniques humaines': 'humaines',
    'Mécanique d\'entretien': 'mecanique_entr',
    'Soins esthétiques et beauté': 'beaute',
  };

  function init() {
    fetch('/data/stats.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        renderKPIs(data.kpis);
        renderSectorChart(data.sector_distribution);
        renderEducationChart(data.education_levels);
        renderMarketChart(data.market_indicators);
        renderCoverageChart(data.section_coverage);
        renderTopSectorsChart(data.top_sectors);
      })
      .catch(function (err) {
        console.error('Erreur chargement stats:', err);
      });
  }

  function renderKPIs(kpis) {
    setText('kpiProfessions', kpis.total_professions);
    setText('kpiSectors', kpis.total_sectors);
    setText('kpiDetails', kpis.total_with_details);
    setText('kpiPerspectives', kpis.total_with_perspectives);
  }

  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function findSectorSlug(name) {
    return SLUG_MAP[name] || null;
  }

  var tooltipConfig = {
    backgroundColor: COLORS.grayDark,
    titleFont: { size: 13 },
    bodyFont: { size: 12 },
    padding: 10,
    cornerRadius: 6,
  };

  // ─── Chart 1: Horizontal Bar — Secteurs ──────────────────────
  function renderSectorChart(data) {
    var ctx = document.getElementById('chartSectors');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(function (d) { return d.label; }),
        datasets: [{
          label: 'Nombre de métiers',
          data: data.map(function (d) { return d.value; }),
          backgroundColor: data.map(function (_, i) { return SECTOR_COLORS[i % SECTOR_COLORS.length]; }),
          borderColor: 'transparent',
          borderRadius: 4,
          borderWidth: 0,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: Object.assign({}, tooltipConfig, {
            callbacks: {
              label: function (ctx) { return ctx.parsed.x + ' métiers'; },
            },
          }),
        },
        scales: {
          x: { grid: { color: COLORS.grayLight }, ticks: { font: { size: 11 } } },
          y: { grid: { display: false }, ticks: { font: { size: 11 }, autoSkip: false } },
        },
        onClick: function (event, elements) {
          if (elements.length > 0) {
            var slug = findSectorSlug(data[elements[0].index].label);
            if (slug) window.location.href = '/secteur/' + slug + '/';
          }
        },
        onHover: function (event, elements) {
          event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
        },
      },
    });
  }

  // ─── Chart 2: Doughnut — Niveaux d'études ────────────────────
  function renderEducationChart(data) {
    var ctx = document.getElementById('chartEducation');
    if (!ctx) return;

    var colors = [COLORS.primary, COLORS.success, COLORS.warning, COLORS.purple, COLORS.gray];

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.map(function (d) { return d.label; }),
        datasets: [{
          data: data.map(function (d) { return d.value; }),
          backgroundColor: colors.slice(0, data.length),
          borderColor: '#ffffff',
          borderWidth: 3,
          hoverBorderWidth: 0,
          hoverOffset: 8,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '55%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { padding: 16, usePointStyle: true, pointStyle: 'circle', font: { size: 12 } },
          },
          tooltip: Object.assign({}, tooltipConfig, {
            callbacks: {
              label: function (ctx) {
                var total = ctx.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                var pct = Math.round((ctx.parsed / total) * 100);
                return ctx.label + ': ' + ctx.parsed + ' (' + pct + '%)';
              },
            },
          }),
        },
      },
    });
  }

  // ─── Chart 3: Bar — Marché du travail ─────────────────────────
  function renderMarketChart(data) {
    var ctx = document.getElementById('chartMarket');
    if (!ctx) return;

    var barColors = [COLORS.danger, COLORS.warning, COLORS.success, COLORS.purple, COLORS.primary];

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(function (d) { return d.label; }),
        datasets: [{
          label: 'Métiers concernés',
          data: data.map(function (d) { return d.value; }),
          backgroundColor: barColors.slice(0, data.length),
          borderRadius: 6,
          borderWidth: 0,
          barPercentage: 0.7,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: Object.assign({}, tooltipConfig, {
            callbacks: {
              label: function (ctx) { return ctx.parsed.y + ' métiers'; },
            },
          }),
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 }, maxRotation: 45, minRotation: 25 } },
          y: { grid: { color: COLORS.grayLight }, ticks: { font: { size: 11 } } },
        },
      },
    });
  }

  // ─── Chart 4: Horizontal Bar — Complétude ─────────────────────
  function renderCoverageChart(data) {
    var ctx = document.getElementById('chartCoverage');
    if (!ctx) return;

    var total = 413;
    var barColors = data.map(function (d) {
      var pct = d.value / total;
      if (pct > 0.8) return COLORS.success;
      if (pct > 0.5) return COLORS.primary;
      if (pct > 0.2) return COLORS.warning;
      return COLORS.danger;
    });

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(function (d) { return d.label; }),
        datasets: [{
          label: 'Nombre de métiers',
          data: data.map(function (d) { return d.value; }),
          backgroundColor: barColors,
          borderRadius: 4,
          borderWidth: 0,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: Object.assign({}, tooltipConfig, {
            callbacks: {
              label: function (ctx) {
                var pct = Math.round((ctx.parsed.x / total) * 100);
                return ctx.parsed.x + ' / ' + total + ' métiers (' + pct + '%)';
              },
            },
          }),
        },
        scales: {
          x: { max: total, grid: { color: COLORS.grayLight }, ticks: { font: { size: 11 } } },
          y: { grid: { display: false }, ticks: { font: { size: 11 }, autoSkip: false } },
        },
      },
    });
  }

  // ─── Chart 5: Bar — Top secteurs ──────────────────────────────
  function renderTopSectorsChart(data) {
    var ctx = document.getElementById('chartTopSectors');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(function (d) { return d.label; }),
        datasets: [{
          label: 'Métiers récupérés',
          data: data.map(function (d) { return d.value; }),
          backgroundColor: data.map(function (_, i) { return SECTOR_COLORS[i % SECTOR_COLORS.length]; }),
          borderRadius: 4,
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: Object.assign({}, tooltipConfig, {
            callbacks: {
              label: function (ctx) { return ctx.parsed.y + ' métiers récupérés'; },
            },
          }),
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 }, maxRotation: 45, minRotation: 30, autoSkip: false } },
          y: { grid: { color: COLORS.grayLight }, ticks: { font: { size: 11 } } },
        },
        onClick: function (event, elements) {
          if (elements.length > 0) {
            var slug = findSectorSlug(data[elements[0].index].label);
            if (slug) window.location.href = '/secteur/' + slug + '/';
          }
        },
        onHover: function (event, elements) {
          event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
        },
      },
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
