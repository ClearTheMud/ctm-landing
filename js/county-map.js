(function () {
  'use strict';

  var countyData;
  var tooltip;
  var isTouchDevice = false;

  function init() {
    countyData = window.CTM_COUNTY_DATA || {};
    tooltip = createTooltip();
    var counties = document.querySelectorAll('.county');

    for (var i = 0; i < counties.length; i++) {
      setupCounty(counties[i]);
    }

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.county') && !e.target.closest('#county-tooltip')) {
        hideTooltip();
      }
    });
  }

  function createTooltip() {
    var el = document.createElement('div');
    el.id = 'county-tooltip';
    el.setAttribute('role', 'tooltip');
    el.style.cssText =
      'position:fixed;padding:6px 12px;background:#1a2332;color:#fff;border-radius:4px;' +
      'font-size:14px;pointer-events:none;opacity:0;transition:opacity .15s;z-index:1000;' +
      'white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.3);';
    document.body.appendChild(el);
    return el;
  }

  function getTooltipText(name, slug, isActive) {
    if (!isActive) return name + ' — Coming soon';
    var info = countyData[slug];
    if (info && info.places > 0) {
      var p = info.places === 1 ? '1 place' : info.places + ' places';
      return name + ' — ' + p;
    }
    return name + ' — View county';
  }

  function setupCounty(el) {
    var slug = el.getAttribute('data-slug');
    var name = el.getAttribute('data-name') || el.id;
    var isActive = slug in countyData;

    el.classList.add(isActive ? 'county--active' : 'county--inactive');
    el.setAttribute('aria-label', getTooltipText(name, slug, isActive));
    el.setAttribute('tabindex', isActive ? '0' : '-1');
    el.setAttribute('role', 'link');

    var tipText = getTooltipText(name, slug, isActive);

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
      var cx = rect.left + rect.width / 2;
      var cy = rect.top;
      showTooltip(tipText, cx, cy);
      positionTooltipAbove(cx, cy);
    });
    el.addEventListener('blur', hideTooltip);

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

    el.addEventListener('touchstart', function (e) {
      isTouchDevice = true;
      var rect = el.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top;
      if (isActive && slug && tooltip.style.opacity === '1' && tooltip._currentCounty === slug) {
        navigate(slug);
      } else {
        e.preventDefault();
        showTooltip(tipText, cx, cy);
        positionTooltipAbove(cx, cy);
        tooltip._currentCounty = slug;
      }
    }, { passive: false });
  }

  function navigate(slug) {
    var statePath = window.CTM_STATE_PATH || '';
    window.location.href = statePath + slug + '/';
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
    tooltip._currentCounty = null;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
