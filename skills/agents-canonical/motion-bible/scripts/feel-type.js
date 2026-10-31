/* =====================================================================
   FEEL TYPE — Motion Bible entry 001
   Cursor-reactive variable-font typography. Drop-in, framework-free.

   The law: pointer position IS the animation state. Each glyph's
   variable-font axes are a direct function of its distance to the
   pointer. No easing, no lerp, no tween between pointer and glyph —
   easing there is stupid (his words).

   Usage:
     <div id="hero"></div>
     <script src="feel-type.js"></script>
     <script>
       var ft = FeelType.mount(document.getElementById('hero'), {
         lines: ['TYPE THAT', 'FEELS YOU'],
         fontFamily: '"Roboto Flex", system-ui, sans-serif'
       });
       // ft.destroy() to tear down.
     </script>

   Needs a variable font with the axes you map (wght/wdth/slnt/opsz).
   A copy of Roboto Flex full-variable lives at fonts/RobotoFlex-Variable.woff2:
     @font-face {
       font-family: 'Roboto Flex';
       src: url('fonts/RobotoFlex-Variable.woff2') format('woff2');
       font-weight: 100 1000; font-stretch: 25% 151%;
     }
   ===================================================================== */
(function (global) {
  'use strict';

  var DEFAULTS = {
    lines: ['FEEL TYPE'],
    radius: 260,            // px — influence radius around the pointer
    falloff: 'linear',      // 'linear' | 'smooth' (smoothstep)
    repel: 14,              // max px push away from pointer; 0 disables
    rest:  { wght: 160, wdth: 100, slnt: 0,   opsz: 40  },  // far from pointer
    peak:  { wght: 900, wdth: 151, slnt: -10, opsz: 120 },  // under the pointer
    staticState: { wght: 420, wdth: 100, slnt: 0, opsz: 60 }, // reduced-motion
    fontFamily: '"Roboto Flex", system-ui, sans-serif',
    lineClass: 'ft-line',
    letterClass: 'ft-letter',
    spaceClass: 'ft-space'
  };

  function assign(target, src) {
    for (var k in src) if (src.hasOwnProperty(k)) target[k] = src[k];
    return target;
  }

  function smooth(t) { return t * t * (3 - 2 * t); }

  function mount(container, opts) {
    var o = assign(assign({}, DEFAULTS), opts || {});
    o.rest = assign(assign({}, DEFAULTS.rest), (opts && opts.rest) || {});
    o.peak = assign(assign({}, DEFAULTS.peak), (opts && opts.peak) || {});
    o.staticState = assign(assign({}, DEFAULTS.staticState), (opts && opts.staticState) || {});

    var reduceMotion = !!(window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches);

    // ---- build letters ----
    var letters = [];
    container.setAttribute('aria-label', o.lines.join(' '));
    o.lines.forEach(function (line) {
      var div = document.createElement('span');
      div.className = o.lineClass;
      div.style.display = 'block';
      div.setAttribute('aria-hidden', 'true');
      line.split('').forEach(function (ch) {
        var s = document.createElement('span');
        if (ch === ' ') { s.className = o.spaceClass; s.innerHTML = '&nbsp;'; }
        else {
          s.className = o.letterClass;
          s.textContent = ch;
          s.style.display = 'inline-block';
          s.style.fontFamily = o.fontFamily;
          s.style.willChange = 'font-variation-settings, transform';
          letters.push(s);
        }
        div.appendChild(s);
      });
      container.appendChild(div);
    });

    // ---- measure once, never per frame ----
    var centers = []; // document-relative
    function measure() {
      centers = [];
      var sy = window.scrollY || window.pageYOffset || 0;
      for (var i = 0; i < letters.length; i++) {
        var r = letters[i].getBoundingClientRect();
        centers.push({ x: r.left + r.width / 2, y: r.top + sy + r.height / 2 });
      }
    }

    var mouse = { x: -9999, y: -9999 }; // viewport-relative
    var rafId = 0, destroyed = false;

    function applyStatic() {
      var st = o.staticState;
      var fvs = '"wght" ' + st.wght + ',"wdth" ' + st.wdth +
                ',"slnt" ' + st.slnt + ',"opsz" ' + st.opsz;
      for (var i = 0; i < letters.length; i++) {
        letters[i].style.fontVariationSettings = fvs;
        letters[i].style.transform = 'translate(0px,0px)';
      }
    }

    function frame() {
      rafId = 0;
      if (destroyed) return;
      var sy = window.scrollY || window.pageYOffset || 0;
      var R = o.radius, useSmooth = o.falloff === 'smooth';
      for (var i = 0; i < letters.length; i++) {
        var c = centers[i]; if (!c) continue;
        var dx = c.x - mouse.x, dy = (c.y - sy) - mouse.y;
        var d = Math.sqrt(dx * dx + dy * dy);
        var inf = d >= R ? 0 : 1 - d / R;
        if (useSmooth) inf = smooth(inf);
        var el = letters[i];
        el.style.fontVariationSettings =
          '"wght" ' + Math.round(o.rest.wght + inf * (o.peak.wght - o.rest.wght)) +
          ',"wdth" ' + Math.round(o.rest.wdth + inf * (o.peak.wdth - o.rest.wdth)) +
          ',"slnt" ' + (o.rest.slnt + inf * (o.peak.slnt - o.rest.slnt)).toFixed(1) +
          ',"opsz" ' + Math.round(o.rest.opsz + inf * (o.peak.opsz - o.rest.opsz));
        if (o.repel > 0 && d > 1 && inf > 0) {
          var push = inf * o.repel;
          el.style.transform = 'translate(' + ((dx / d) * push).toFixed(1) + 'px,' +
                                                ((dy / d) * push).toFixed(1) + 'px)';
        } else {
          el.style.transform = 'translate(0px,0px)';
        }
      }
    }
    function kick() {
      if (!rafId && !destroyed) rafId = requestAnimationFrame(frame);
    }

    function onPoint(x, y) { mouse.x = x; mouse.y = y; kick(); }
    function onPointerMove(e) { onPoint(e.clientX, e.clientY); }
    function onTouchMove(e) {
      var t = e.touches[0]; if (t) onPoint(t.clientX, t.clientY);
    }
    function onScroll() { kick(); }
    var onResize = function () { measure(); kick(); };

    if (reduceMotion) {
      applyStatic();
    } else {
      window.addEventListener('pointermove', onPointerMove, { passive: true });
      window.addEventListener('touchmove', onTouchMove, { passive: true });
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onResize);
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(function () { measure(); kick(); });
      }
      measure();
      kick(); // paint the rest state on load
    }

    return {
      measure: measure,
      refresh: kick,
      destroy: function () {
        destroyed = true;
        if (rafId) cancelAnimationFrame(rafId);
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('touchmove', onTouchMove);
        window.removeEventListener('scroll', onScroll);
        window.removeEventListener('resize', onResize);
        container.innerHTML = '';
        container.removeAttribute('aria-label');
      }
    };
  }

  global.FeelType = { mount: mount, defaults: DEFAULTS };
})(typeof window !== 'undefined' ? window : this);
