(function () {
  'use strict';

  var legData;
  var tooltip;
  var isTouchDevice = false;

  function init() {
    legData = window.CTM_LEG_DATA || {};
    tooltip = createTooltip();
    var districts = document.querySelectorAll('.leg-district');

    for (var i = 0; i < districts.length; i++) {
      setupDistrict(districts[i]);
    }
    // Each SVG is its own widget with its own single tab stop: the main map and the Puget Sound
    // inset do not share a roving group, so Tab visits the map, then the inset, then the table.
    var groups = groupBySvg(districts);
    for (var g = 0; g < groups.length; g++) {
      var group = groups[g];
      setupRoving(group);
      setupMapGroup(group, g);
    }

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.leg-district') && !e.target.closest('#leg-tooltip')) {
        hideTooltip();
      }
    });
  }

  function groupBySvg(shapes) {
    var svgs = [];
    var groups = [];
    for (var i = 0; i < shapes.length; i++) {
      var svg = shapes[i].ownerSVGElement;
      var at = svgs.indexOf(svg);
      if (at < 0) {
        svgs.push(svg);
        groups.push([]);
        at = svgs.length - 1;
      }
      groups[at].push(shapes[i]);
    }
    return groups;
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
  function setupMapGroup(shapes, index) {
    var svg = shapes.length ? shapes[0].ownerSVGElement : null;
    if (!svg) return;
    if (svg.getAttribute('role') === 'img') svg.setAttribute('role', 'group');
    var helpId = tooltip.id + '-keys' + (index ? '-' + index : '');
    if (document.getElementById(helpId)) return;
    var help = document.createElement('p');
    help.id = helpId;
    help.className = 'sr-only';
    help.textContent = 'Use the arrow keys to move between areas on this map, and Enter to open one.';
    svg.parentNode.insertBefore(help, svg);
    var existing = svg.getAttribute('aria-describedby');
    svg.setAttribute('aria-describedby', existing ? existing + ' ' + helpId : helpId);
  }

  function createTooltip() {
    var el = document.createElement('div');
    el.id = 'leg-tooltip';
    el.setAttribute('aria-hidden', 'true');
    el.style.cssText =
      'position:fixed;padding:6px 12px;background:#1a2332;color:#fff;border-radius:4px;' +
      'font-size:14px;pointer-events:none;opacity:0;transition:opacity .15s;z-index:1000;' +
      'white-space:normal;max-width:min(26rem,calc(100vw - 16px));line-height:1.35;box-shadow:0 2px 8px rgba(0,0,0,.3);';
    document.body.appendChild(el);
    return el;
  }

  // data-tip, when the page supplies it, is the full sentence in words: district,
  // delegation, and each seat's leader and party preference.
  function getTooltipText(num, isActive, el) {
    var tip = el && el.getAttribute('data-tip');
    if (tip) return tip;
    if (!isActive) return 'LD-' + num + ' — No races tracked';
    var info = legData[num];
    var races = info ? info.races : 0;
    var cands = info ? info.candidates : 0;
    return 'LD-' + num + ' — ' + races + (races === 1 ? ' race' : ' races') +
      ', ' + cands + ' candidates';
  }

  function setupDistrict(el) {
    var num = el.getAttribute('data-district');
    // data-clickable marks a shape that goes to a row in the page's own table (the
    // colored results map), so it needs no CTM_LEG_DATA entry.
    var isActive = num in legData || el.getAttribute('data-clickable') === 'true';

    el.classList.add(isActive ? 'leg-district--active' : 'leg-district--inactive');
    el.setAttribute('aria-label', getTooltipText(num, isActive, el));
    el.setAttribute('tabindex', isActive ? '0' : '-1');
    el.setAttribute('role', el.getAttribute('tabindex') === '0' ? 'link' : 'img');

    var tipText = getTooltipText(num, isActive, el);

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

    el.addEventListener('focus', function () {
      var rect = el.getBoundingClientRect();
      showTooltip(tipText, rect.left + rect.width / 2, rect.top);
      positionTooltipAbove(rect.left + rect.width / 2, rect.top);
    });
    el.addEventListener('blur', hideTooltip);

    if (isActive) {
      el.style.cursor = 'pointer';
      el.addEventListener('click', function () { scrollToDistrict(num); });
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          scrollToDistrict(num);
        }
      });
    }

    bindCallouts(el, num, tipText, isActive);

    el.addEventListener('touchstart', function (e) {
      isTouchDevice = true;
      var rect = el.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top;
      if (isActive && tooltip.style.opacity === '1' && tooltip._currentDistrict === num) {
        scrollToDistrict(num);
      } else {
        e.preventDefault();
        showTooltip(tipText, cx, cy);
        positionTooltipAbove(cx, cy);
        tooltip._currentDistrict = num;
      }
    }, { passive: false });
  }

  // The Puget Sound inset joins each tiny district to a numbered chip by a line. The chip is a larger
  // pointer target for the same district: hover shows the same tooltip, a click goes to the same row.
  // Keyboard users use the district shape itself (the chips are hidden from assistive technology),
  // and focusing or hovering a shape marks its chip so the connection is visible.
  function bindCallouts(el, num, tipText, isActive) {
    var svg = el.ownerSVGElement;
    if (!svg) return;
    var callouts = svg.querySelectorAll('.gr-in-callout[data-district="' + num + '"]');
    function mark(on) {
      for (var i = 0; i < callouts.length; i++) callouts[i].classList.toggle('gr-in-callout--on', on);
    }
    el.addEventListener('focus', function () { mark(true); });
    el.addEventListener('blur', function () { mark(false); });
    el.addEventListener('mouseenter', function () { mark(true); });
    el.addEventListener('mouseleave', function () { mark(false); });
    for (var i = 0; i < callouts.length; i++) {
      (function (callout) {
        callout.addEventListener('mouseenter', function (e) {
          isTouchDevice = false;
          mark(true);
          showTooltip(tipText, e.clientX, e.clientY);
        });
        callout.addEventListener('mousemove', function (e) {
          if (!isTouchDevice) positionTooltipAtCursor(e.clientX, e.clientY);
        });
        callout.addEventListener('mouseleave', function () {
          mark(false);
          if (!isTouchDevice) hideTooltip();
        });
        if (isActive) callout.addEventListener('click', function () { scrollToDistrict(num); });
      })(callouts[i]);
    }
  }

  // Scroll to the district's row in the table and move focus there, so a keyboard or
  // screen reader user lands on the row the map pointed at. Smooth scrolling is skipped
  // for people who ask for reduced motion.
  function scrollToDistrict(num) {
    var row = document.getElementById('ld-' + num);
    if (!row) return;
    var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    row.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'center' });
    if (!row.hasAttribute('tabindex')) row.setAttribute('tabindex', '-1');
    row.focus({ preventScroll: true });
    row.classList.add('gr-ld-row--hit');
    setTimeout(function () { row.classList.remove('gr-ld-row--hit'); }, 2000);
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
    tooltip._currentDistrict = null;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
