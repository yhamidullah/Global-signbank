(function () {
  'use strict';

  var THEME_DEFAULTS = {
    global: { color_primary: '', color_primary_text: '', color_accent: '', color_inst_bar_bg: '' },
    uzh:    { color_primary: '#0028a5', color_primary_text: '#ffffff', color_accent: '#0028a5', color_inst_bar_bg: '#f0f2f7' },
    modern: { color_primary: '#0f172a', color_primary_text: '#f1f5f9', color_accent: '#3b82f6', color_inst_bar_bg: '#0d1117' },
    aurora: { color_primary: '#4f46e5', color_primary_text: '#ffffff', color_accent: '#06b6d4', color_inst_bar_bg: '#3730a3' },
  };

  var COLOR_FIELDS = ['color_primary', 'color_primary_text', 'color_accent', 'color_inst_bar_bg'];

  function applyDefaults(theme) {
    var defs = THEME_DEFAULTS[theme] || {};
    COLOR_FIELDS.forEach(function (f) {
      var el = document.getElementById('id_' + f);
      if (!el) return;
      var val = defs[f] || '';
      /* color inputs require a valid hex; fall back to black when theme has no default */
      el.value = val || '#000000';
      /* also clear the hidden text so it saves as '' for global (no override) */
      el.dataset.themeDefault = val;
    });
  }

  function currentTheme() {
    var checked = document.querySelector('input[name="theme"]:checked');
    return checked ? checked.value : 'global';
  }

  document.addEventListener('DOMContentLoaded', function () {

    /* ── 1. Theme radio → auto-fill colors ── */
    document.querySelectorAll('input[name="theme"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        applyDefaults(this.value);
      });
    });

    /* ── 2. Inject "Reset" button above the first color field ── */
    var firstColorRow = document.querySelector('.field-color_primary');
    if (firstColorRow) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = '↺  Reset colors to theme defaults';
      btn.style.cssText = [
        'display:inline-block',
        'margin:0 0 14px 170px',
        'padding:5px 14px',
        'background:#417690',
        'color:#fff',
        'border:none',
        'border-radius:4px',
        'cursor:pointer',
        'font-size:12px',
        'font-weight:500',
      ].join(';');
      btn.addEventListener('mouseenter', function () { this.style.background = '#2b5b77'; });
      btn.addEventListener('mouseleave', function () { this.style.background = '#417690'; });
      btn.addEventListener('click', function () { applyDefaults(currentTheme()); });

      firstColorRow.parentNode.insertBefore(btn, firstColorRow);
    }

    /* ── 3. Expand the Colors fieldset if a non-default color is already set ── */
    var hasCustomColor = COLOR_FIELDS.some(function (f) {
      var el = document.getElementById('id_' + f);
      return el && el.value && el.value !== '#000000';
    });

    if (hasCustomColor) {
      /* find the collapse toggle for the Colors section and open it */
      var collapseLinks = document.querySelectorAll('fieldset.collapse');
      collapseLinks.forEach(function (fs) {
        var legend = fs.querySelector('h2');
        if (legend && legend.textContent.toLowerCase().includes('color')) {
          fs.classList.remove('collapse');
          fs.classList.add('open');
        }
      });
    }
  });
})();