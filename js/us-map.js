/**
 * us-map.js — Interactive US states SVG map for clearthemud.org
 *
 * Expects window.CTM_STATE_DATA: { "ME": { dossiers: 3, races: 1, senate: true }, ... }
 * Falls back to window.CTM_ACTIVE_STATES: ["ME"] for backward compatibility.
 */
(function () {
  'use strict';

  var stateData;
  var tooltip;
  var isTouchDevice = false;

  function init() {
    stateData = {};
    if (window.CTM_STATE_DATA) {
      stateData = window.CTM_STATE_DATA;
    } else if (window.CTM_ACTIVE_STATES) {
      (window.CTM_ACTIVE_STATES || []).forEach(function (s) {
        stateData[s.toUpperCase()] = { dossiers: 0, races: 0 };
      });
    }
    tooltip = createTooltip();
    var states = document.querySelectorAll('.state');

    for (var i = 0; i < states.length; i++) {
      setupState(states[i]);
    }
    setupRoving(states);
    setupMapGroup(states);

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.state') && !e.target.closest('#map-tooltip')) {
        hideTooltip();
      }
    });
  }

  // One tab stop per map (WCAG 2.4.3, 2.4.1): the shapes are a single widget.
  // Exactly one clickable shape has tabindex 0; arrow keys, Home and End move
  // between the clickable shapes, so every destination stays reachable
  // without ~100 Tab presses. Shapes that go nowhere are not focusable.
  function setupRoving(shapes) {
    var stops = [];
    for (var i = 0; i < shapes.length; i++) {
      if (shapes[i].getAttribute('tabindex') === '0') stops.push(shapes[i]);
    }
    if (!stops.length) return;
    var current = stops[0];
    function setCurrent(next) {
      current.setAttribute('tabindex', '-1');
      current = next;
      current.setAttribute('tabindex', '0');
    }
    stops.forEach(function (el, index) {
      if (index > 0) el.setAttribute('tabindex', '-1');
      el.addEventListener('focus', function () {
        if (current !== el) setCurrent(el);
      });
      el.addEventListener('keydown', function (e) {
        var at = stops.indexOf(el);
        var next = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = stops[(at + 1) % stops.length];
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = stops[(at - 1 + stops.length) % stops.length];
        else if (e.key === 'Home') next = stops[0];
        else if (e.key === 'End') next = stops[stops.length - 1];
        if (next) {
          e.preventDefault();
          setCurrent(next);
          next.focus();
        }
      });
    });
  }

  // role="img" makes its descendants presentational, which breaks the
  // focusable shapes inside it. A group keeps the name and the children.
  function setupMapGroup(shapes) {
    var svg = shapes.length ? shapes[0].ownerSVGElement : null;
    if (!svg) return;
    if (svg.getAttribute('role') === 'img') svg.setAttribute('role', 'group');
    var helpId = tooltip.id + '-keys';
    if (document.getElementById(helpId)) return;
    var help = document.createElement('p');
    help.id = helpId;
    help.className = 'sr-only';
    help.textContent = 'Use the arrow keys to move between areas on this map, and Enter to open one.';
    svg.parentNode.insertBefore(help, svg);
    svg.setAttribute('aria-describedby', helpId);
  }

  function createTooltip() {
    var el = document.createElement('div');
    el.id = 'map-tooltip';
    el.setAttribute('aria-hidden', 'true');
    el.style.cssText =
      'position:fixed;padding:6px 12px;background:#1a2332;color:#fff;border-radius:4px;' +
      'font-size:14px;pointer-events:none;opacity:0;transition:opacity .15s;z-index:1000;' +
      'white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.3);';
    document.body.appendChild(el);
    return el;
  }

  function getStateClass(abbr) {
    var info = stateData[abbr];
    if (!info) return 'inactive';
    if (info.dossiers > 0 || info.races > 0) return 'active';
    if (info.senate) return 'senate';
    return 'inactive';
  }

  function getTooltipText(name, abbr) {
    var info = stateData[abbr];
    var stateClass = getStateClass(abbr);
    if (stateClass === 'active') {
      if (info && info.dossiers > 0) {
        var d = info.dossiers === 1 ? '1 candidate dossier' : info.dossiers + ' candidate dossiers';
        return name + ' — ' + d;
      }
      return name + ' — Research available';
    }
    if (stateClass === 'senate') {
      return name + ' — 2026 U.S. Senate race';
    }
    return name + ' — No published dossiers yet';
  }

  function setupState(el) {
    var abbr = el.id.toUpperCase();
    var name = el.getAttribute('data-name') || abbr;
    var slug = el.getAttribute('data-slug');
    var stateClass = getStateClass(abbr);
    var isClickable = stateClass === 'active' || stateClass === 'senate';

    var classMap = { active: 'state--active', senate: 'state--senate', inactive: 'state--inactive' };
    el.classList.add(classMap[stateClass] || 'state--inactive');
    var tipText = getTooltipText(name, abbr);
    el.setAttribute('aria-label', tipText);
    el.setAttribute('tabindex', isClickable ? '0' : '-1');
    el.setAttribute('role', el.getAttribute('tabindex') === '0' ? 'link' : 'img');

    // Hover
    el.addEventListener('mouseenter', function (e) {
      isTouchDevice = false;
      showTooltip(tipText, e.clientX, e.clientY);
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
      showTooltip(tipText, cx, cy);
      positionTooltipAbove(cx, cy);
    });
    el.addEventListener('blur', hideTooltip);

    // Click / keyboard
    if (isClickable && slug) {
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
      var rect = el.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top;
      if (isClickable && slug && tooltip.style.opacity === '1' && tooltip._currentState === abbr) {
        navigate(slug);
      } else {
        e.preventDefault();
        showTooltip(tipText, cx, cy);
        positionTooltipAbove(cx, cy);
        tooltip._currentState = abbr;
      }
    }, { passive: false });
  }

  function navigate(slug) {
    window.location.href = '/states/' + slug + '/';
  }

  function showTooltip(text, x, y) {
    tooltip.textContent = text;
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
