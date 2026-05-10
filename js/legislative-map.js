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

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.leg-district') && !e.target.closest('#leg-tooltip')) {
        hideTooltip();
      }
    });
  }

  function createTooltip() {
    var el = document.createElement('div');
    el.id = 'leg-tooltip';
    el.setAttribute('role', 'tooltip');
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
    el.setAttribute('role', 'link');

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
