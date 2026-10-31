/* =====================================================================
   MAGNETIC — Motion Bible entry 003
   Eased magnetic parallax: an element leans toward the pointer, as if
   pulled by it. Drop-in, framework-free.

   The law (bible law #2 again): this is a follower — the element is an
   object with weight, so it earns its ease. The pull is computed from
   the pointer's offset from the stage center, then clamped: the element
   can only wander a few px from home, never chase the cursor off-stage.

   Usage:
     <div id="stage"><img id="hero" src="..."></div>
     <script src="magnetic.js"></script>
     <script>
       var m = Magnetic.mount(document.getElementById('hero'),
                              document.getElementById('stage'));
       // m.destroy()
     </script>

   The element is moved with transform translate; it must not already
   use transform for layout. The stage defaults to the element's parent.
   ===================================================================== */
(function (global) {
  'use strict';

  var DEFAULTS = {
    strength: 0.045, // fraction of (pointer - stageCenter) applied as target
    max: 16,         // px clamp on the target — the leash length
    ease: 0.07,      // per-frame chase factor; lower = heavier
    disableOnTouch: false // true: no magnetic pull on coarse pointers
  };

  function assign(t, s) { for (var k in s) if (s.hasOwnProperty(k)) t[k] = s[k]; return t; }

  function mount(el, stage, opts) {
    var o = assign(assign({}, DEFAULTS), opts || {});
    stage = stage || el.parentElement;

    var reduceMotion = !!(window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    var coarse = !!(window.matchMedia && window.matchMedia('(pointer: coarse)').matches);

    var cur = { x: 0, y: 0 }, tgt = { x: 0, y: 0 };
    var mouse = { x: -9999, y: -9999 };
    var center = { x: 0, y: 0 }, measured = false;
    var rafId = 0, idleFrames = 0, destroyed = false, active = true;

    if (reduceMotion || (o.disableOnTouch && coarse)) active = false;

    function render() {
      el.style.transform = 'translate(' + cur.x.toFixed(1) + 'px,' + cur.y.toFixed(1) + 'px)';
    }

    function frame() {
      rafId = 0;
      if (destroyed || document.hidden) return;
      var dx = tgt.x - cur.x, dy = tgt.y - cur.y;
      if (Math.abs(dx) < 0.1 && Math.abs(dy) < 0.1) {
        cur.x = tgt.x; cur.y = tgt.y; idleFrames++;
      } else {
        cur.x += dx * o.ease; cur.y += dy * o.ease;
        idleFrames = 0;
      }
      render();
      if (idleFrames < 90) rafId = requestAnimationFrame(frame); // settle to sleep
    }
    function kick() {
      idleFrames = 0;
      if (active && !rafId && !destroyed && !document.hidden) rafId = requestAnimationFrame(frame);
    }

    function measure() {
      if (!stage) return;
      var r = stage.getBoundingClientRect();
      center.x = r.left + r.width / 2;
      center.y = r.top + r.height / 2;
      measured = true;
    }

    function retarget() {
      if (!active || !measured) return;
      var tx = (mouse.x - center.x) * o.strength;
      var ty = (mouse.y - center.y) * o.strength;
      var len = Math.sqrt(tx * tx + ty * ty);
      if (len > o.max) { tx = tx / len * o.max; ty = ty / len * o.max; }
      tgt.x = tx; tgt.y = ty;
      kick();
    }

    function onPoint(x, y) { mouse.x = x; mouse.y = y; retarget(); }
    function onPointerMove(e) { onPoint(e.clientX, e.clientY); }
    function onTouchMove(e) {
      var t = e.touches[0]; if (t) onPoint(t.clientX, t.clientY);
    }

    function onGeometryChange() { measure(); retarget(); }
    measure();
    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: true });
    window.addEventListener('resize', onGeometryChange, { passive: true });
    window.addEventListener('scroll', onGeometryChange, { passive: true });
    var resizeObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(onGeometryChange) : null;
    if (resizeObserver) resizeObserver.observe(stage);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(onGeometryChange);

    return {
      retarget: retarget,
      measure: measure,
      destroy: function () {
        destroyed = true;
        if (rafId) cancelAnimationFrame(rafId);
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('touchmove', onTouchMove);
        window.removeEventListener('resize', onGeometryChange);
        window.removeEventListener('scroll', onGeometryChange);
        if (resizeObserver) resizeObserver.disconnect();
        el.style.transform = '';
      }
    };
  }

  global.Magnetic = { mount: mount, defaults: DEFAULTS };
})(typeof window !== 'undefined' ? window : this);
