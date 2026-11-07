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
    setupRoving(districts);
    setupMapGroup(districts);

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.leg-district') && !e.target.closest('#leg-tooltip')) {
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
    el.id = 'leg-tooltip';
    el.setAttribute('aria-hidden', 'true');
    el.style.cssText =
      'position:fixed;padding:6px 12px;background:#1a2332;color:#fff;border-radius:4px;' +
      'font-size:14px;pointer-events:none;opacity:0;transition:opacity .15s;z-index:1000;' +
      'white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.3);';
    document.body.appendChild(el);
    return el;
  }

  function getTooltipText(num, isActive) {
    if (!isActive) return 'LD-' + num + ' — No races tracked';
    var info = legData[num];
    var races = info ? info.races : 0;
    var cands = info ? info.candidates : 0;
    return 'LD-' + num + ' — ' + races + (races === 1 ? ' race' : ' races') +
      ', ' + cands + ' candidates';
  }

  function setupDistrict(el) {
    var num = el.getAttribute('data-district');
    var isActive = num in legData;

    el.classList.add(isActive ? 'leg-district--active' : 'leg-district--inactive');
    el.setAttribute('aria-label', getTooltipText(num, isActive));
    el.setAttribute('tabindex', isActive ? '0' : '-1');
    el.setAttribute('role', el.getAttribute('tabindex') === '0' ? 'link' : 'img');

    var tipText = getTooltipText(num, isActive);

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

  function scrollToDistrict(num) {
    var row = document.getElementById('ld-' + num);
    if (row) {
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      row.style.background = '#2a4a6a';
      setTimeout(function () { row.style.background = ''; }, 2000);
    }
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
