/**
 * us-map.js — Interactive US states SVG map for clearthemud.org
 *
 * Expects:
 *   - window.CTM_ACTIVE_STATES: string[] of 2-letter state abbreviations with published data
 *   - SVG inline on the page with path.state elements, each having:
 *       id="XX" (state abbr), data-slug="state-name", data-name="State Name"
 */
(function () {
  'use strict';

  var activeSet;
  var tooltip;
  var isTouchDevice = false;

  function init() {
    activeSet = new Set((window.CTM_ACTIVE_STATES || []).map(function (s) { return s.toUpperCase(); }));
    tooltip = createTooltip();
    var states = document.querySelectorAll('.state');

    for (var i = 0; i < states.length; i++) {
      setupState(states[i]);
    }

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.state') && !e.target.closest('#map-tooltip')) {
        hideTooltip();
      }
    });
  }

  function createTooltip() {
    var el = document.createElement('div');
    el.id = 'map-tooltip';
    el.setAttribute('role', 'tooltip');
    el.style.cssText =
      'position:fixed;padding:6px 12px;background:#1a1a2e;color:#fff;border-radius:4px;' +
      'font-size:14px;pointer-events:none;opacity:0;transition:opacity .15s;z-index:1000;' +
      'white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.3);';
    document.body.appendChild(el);
    return el;
  }

  function setupState(el) {
    var abbr = el.id.toUpperCase();
    var name = el.getAttribute('data-name') || abbr;
    var slug = el.getAttribute('data-slug');
    var isActive = activeSet.has(abbr);

    el.classList.add(isActive ? 'state--active' : 'state--inactive');
    el.setAttribute('aria-label', name + (isActive ? '' : ' — Research coming soon'));
    el.setAttribute('tabindex', isActive ? '0' : '-1');
    el.setAttribute('role', 'link');

    // Hover
    el.addEventListener('mouseenter', function (e) {
      isTouchDevice = false;
      showTooltip(name, isActive, e.clientX, e.clientY);
    });
    el.addEventListener('mousemove', function (e) {
      if (!isTouchDevice) positionTooltipAtCursor(e.clientX, e.clientY);
    });
    el.addEventListener('mouseleave', function () {
      if (!isTouchDevice) hideTooltip();
    });

    // Focus
    el.addEventListener('focus', function () {
      var rect = el.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top;
      showTooltip(name, isActive, cx, cy);
      positionTooltipAbove(cx, cy);
    });
    el.addEventListener('blur', hideTooltip);

    // Click / keyboard
    if (isActive && slug) {
      el.style.cursor = 'pointer';
      el.addEventListener('click', function () { navigate(slug); });
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          navigate(slug);
        }
      });
    }

    // Touch
    el.addEventListener('touchstart', function (e) {
      isTouchDevice = true;
      if (isActive && slug) {
        // First tap shows tooltip, second tap navigates
        if (tooltip.style.opacity === '1' && tooltip._currentState === abbr) {
          navigate(slug);
        } else {
          e.preventDefault();
          var rect = el.getBoundingClientRect();
          showTooltip(name, isActive, rect.left + rect.width / 2, rect.top);
          positionTooltipAbove(rect.left + rect.width / 2, rect.top);
          tooltip._currentState = abbr;
        }
      } else {
        e.preventDefault();
        var rect = el.getBoundingClientRect();
        showTooltip(name, isActive, rect.left + rect.width / 2, rect.top);
        positionTooltipAbove(rect.left + rect.width / 2, rect.top);
        tooltip._currentState = abbr;
      }
    }, { passive: false });
  }

  function navigate(slug) {
    window.location.href = '/states/' + slug + '/';
  }

  function showTooltip(name, isActive, x, y) {
    tooltip.textContent = name + (isActive ? '' : ' — Research coming soon');
    tooltip.style.opacity = '1';
    positionTooltipAtCursor(x, y);
  }

  function positionTooltipAtCursor(x, y) {
    var tw = tooltip.offsetWidth;
    var left = x - tw / 2;
    left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
    tooltip.style.left = left + 'px';
    tooltip.style.top = (y - tooltip.offsetHeight - 10) + 'px';
  }

  function positionTooltipAbove(cx, cy) {
    var tw = tooltip.offsetWidth;
    var left = cx - tw / 2;
    left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
    tooltip.style.left = left + 'px';
    tooltip.style.top = (cy - tooltip.offsetHeight - 10) + 'px';
  }

  function hideTooltip() {
    tooltip.style.opacity = '0';
    tooltip._currentState = null;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
