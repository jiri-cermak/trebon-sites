/* ============================================================
   main.js — shared vanilla JS for trebon-sites domains
   (penzion | thai | masaze)
   Currently: hero carousel with 8s cross-fade for .hero-slide
   ============================================================ */
(function () {
  'use strict';

  var CAROUSEL_INTERVAL_MS = 8000;

  /**
   * Hero carousel — cross-fades .hero-slide elements inside
   * .hero, builds clickable dots into #heroDots when present.
   */
  function initHeroCarousel() {
    var slides = document.querySelectorAll('.hero-slide');
    if (!slides.length) return;

    var dotsWrap = document.getElementById('heroDots');
    var dots = [];
    var current = 0;
    var timer = null;

    function show(index, focus) {
      if (index === current) return;
      slides[current].classList.remove('is-active');
      slides[current].setAttribute('aria-hidden', 'true');
      if (dots[current]) dots[current].classList.remove('is-active');

      current = (index + slides.length) % slides.length;
      slides[current].classList.add('is-active');
      slides[current].removeAttribute('aria-hidden');
      if (dots[current]) {
        dots[current].classList.add('is-active');
        if (focus) dots[current].focus();
      }
    }

    function restart() {
      if (timer) clearInterval(timer);
      timer = setInterval(function () { show(current + 1, false); }, CAROUSEL_INTERVAL_MS);
    }

    // Build dot indicators
    if (dotsWrap) {
      for (var i = 0; i < slides.length; i += 1) {
        (function (idx) {
          var dot = document.createElement('button');
          dot.type = 'button';
          dot.className = 'hero-dot' + (idx === 0 ? ' is-active' : '');
          dot.setAttribute('aria-label', 'Zobrazit fotografii ' + (idx + 1));
          dot.addEventListener('click', function () {
            show(idx, true);
            restart();
          });
          dotsWrap.appendChild(dot);
          dots.push(dot);
        })(i);
      }
    }

    restart();
  }

  document.addEventListener('DOMContentLoaded', initHeroCarousel);
})();
