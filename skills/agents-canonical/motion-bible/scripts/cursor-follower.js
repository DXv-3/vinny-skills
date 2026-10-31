/* =====================================================================
   CURSOR FOLLOWER — Motion Bible entry 002
   A spring-lagged follower that trails the pointer. Drop-in,
   framework-free.

   The law (bible law #2): followers may lag, drivers may not. The
   follower is the canonical follower — it chases the pointer with a
   per-frame ease, never covering it (offset), and it can be grabbed,
   parked, and tapped.

   Usage:
     <div id="orb"></div>
     <script src="cursor-follower.js"></script>
     <script>
       var f = Follower.mount(document.getElementById('orb'), {
         onTap: function(){ // open something
         }
       });
       // f.pause() / f.resume() / f.park(x, y) / f.destroy()
     </script>

   The element is positioned with transform translate; give it
   position:fixed (or absolute) and left/top 0 in your CSS.
   ===================================================================== */
(function (global) {
  'use strict';

  var DEFAULTS = {
    offset: { x: 34, y: 40 }, // follower target = pointer + offset: never covers the cursor
    ease: 0.14,               // per-frame chase factor (0..1); higher = tighter
    draggable: true,           // pointerdown + move re-parks it; release resumes following
    tapSlop: 6,                // px of movement before a press stops counting as a tap
    parkOnReducedMotion: true, // reduced-motion: park in corner, still tappable
    parkCorner: null,          // {x,y} override; default = bottom-right inset
    onTap: null,               // fn(el) — fired on tap / Enter / Space
    startX: null, startY: null // initial position override
  };

  function assign(t, s) { for (var k in s) if (s.hasOwnProperty(k)) t[k] = s[k]; return t; }

  function mount(el, opts) {
    var o = assign(assign({}, DEFAULTS), opts || {});
    o.offset = assign({ x: 34, y: 40 }, (opts && opts.offset) || {});

    var reduceMotion = !!(window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches);

    el.style.position = el.style.position || 'fixed';
    el.style.left = '0px'; el.style.top = '0px';
    el.style.willChange = 'transform';
    el.setAttribute('tabindex', '0');
    el.setAttribute('role', 'button');

    var pos = { x: o.startX != null ? o.startX : innerWidth - 70,
                y: o.startY != null ? o.startY : innerHeight - 120 };
    var target = { x: pos.x, y: pos.y };
    var following = true, dragging = false, dragMoved = false;
    var dragGrab = { x: 0, y: 0 };
    var paused = false, destroyed = false;
    var rafId = 0, idleFrames = 0;

    function render() {
      el.style.transform = 'translate(' + pos.x.toFixed(1) + 'px,' + pos.y.toFixed(1) + 'px)';
    }

    function frame() {
      rafId = 0;
      if (destroyed || document.hidden) return;
      if (!dragging) {
        var dx = target.x - pos.x, dy = target.y - pos.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 0.5) { pos.x = target.x; pos.y = target.y; idleFrames++; }
        else {
          pos.x += dx * o.ease; pos.y += dy * o.ease;
          idleFrames = 0;
        }
        render();
        // settle to sleep: stop burning frames once parked
        if (idleFrames < 90) rafId = requestAnimationFrame(frame);
      }
    }
    function kick() {
      idleFrames = 0;
      if (!rafId && !destroyed && !document.hidden) rafId = requestAnimationFrame(frame);
    }

    function targetFromPointer(x, y) {
      target.x = x + o.offset.x;
      target.y = y + o.offset.y;
    }

    function onPointerMove(e) {
      if (following && !paused && !dragging) { targetFromPointer(e.clientX, e.clientY); kick(); }
    }
    function onTouchMove(e) {
      var t = e.touches[0];
      if (t && following && !paused && !dragging) { targetFromPointer(t.clientX, t.clientY); kick(); }
    }

    function fireTap() { if (typeof o.onTap === 'function') o.onTap(el); }

    function onPointerDown(e) {
      if (!o.draggable) return;
      dragging = true; dragMoved = false;
      dragGrab.x = e.clientX - pos.x; dragGrab.y = e.clientY - pos.y;
      if (el.setPointerCapture) { try { el.setPointerCapture(e.pointerId); } catch (err) {} }
      if (rafId) { cancelAnimationFrame(rafId); rafId = 0; }
      e.preventDefault();
    }
    function onPointerMoveDrag(e) {
      if (!dragging) return;
      var nx = e.clientX - dragGrab.x, ny = e.clientY - dragGrab.y;
      if (Math.abs(nx - pos.x) + Math.abs(ny - pos.y) > o.tapSlop) dragMoved = true;
      pos.x = nx; pos.y = ny; target.x = nx; target.y = ny;
      render();
    }
    function onPointerUp() {
      if (!dragging) return;
      dragging = false;
      if (!dragMoved) fireTap();
      else kick(); // dropped: resume following from the new spot
    }
    function onKey(e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fireTap(); }
    }
    function onResize() {
      // keep it on-screen after rotation/resize
      pos.x = Math.min(pos.x, innerWidth - 40); pos.y = Math.min(pos.y, innerHeight - 40);
      target.x = Math.min(target.x, innerWidth - 40); target.y = Math.min(target.y, innerHeight - 40);
      render();
    }

    var api = {
      pause: function () { paused = true; },
      resume: function () { paused = false; kick(); },
      park: function (x, y) {
        following = false;
        target.x = x; target.y = y; kick();
      },
      follow: function () { following = true; kick(); },
      position: function () { return { x: pos.x, y: pos.y }; },
      destroy: function () {
        destroyed = true;
        if (rafId) cancelAnimationFrame(rafId);
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('touchmove', onTouchMove);
        window.removeEventListener('resize', onResize);
        el.removeEventListener('pointerdown', onPointerDown);
        el.removeEventListener('pointermove', onPointerMoveDrag);
        el.removeEventListener('pointerup', onPointerUp);
        el.removeEventListener('pointercancel', onPointerUp);
        el.removeEventListener('keydown', onKey);
      }
    };

    if (reduceMotion && o.parkOnReducedMotion) {
      var c = o.parkCorner || { x: innerWidth - 70, y: innerHeight - 120 };
      pos.x = c.x; pos.y = c.y; target.x = c.x; target.y = c.y;
      following = false; // parked in the corner, still tappable
      render();
    } else {
      render();
    }

    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: true });
    window.addEventListener('resize', onResize);
    el.addEventListener('pointerdown', onPointerDown);
    el.addEventListener('pointermove', onPointerMoveDrag);
    el.addEventListener('pointerup', onPointerUp);
    el.addEventListener('pointercancel', onPointerUp);
    el.addEventListener('keydown', onKey);

    return api;
  }

  global.Follower = { mount: mount, defaults: DEFAULTS };
})(typeof window !== 'undefined' ? window : this);
