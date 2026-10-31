# Motion Bible — Complete Handoff for a Clueless LLM

*Written 2026-09-24. Everything another LLM needs to understand this motion system, use it, and propose new entries. Nothing held back.*

---

## PART 1 — CONTEXT (read this first)

### What this is

The **Motion Bible** is the authority on how things move in Vinny's builds. It is not a library and not a framework — it is a *canon*: every entry is a motion pattern he personally blessed, stripped down to its mechanism, ready to drop into the next build. An effect graduates into this bible the day he says "keep that" — not before.

### How entries get in (the blessing protocol)

1. Ship the toy (a prototype page, a sketch, a demo).
2. He points at the part that isn't stupid.
3. That part gets extracted here as a drop-in JS module + its laws + tuning notes.
4. The toy stays where it was. The bible is what's reused.

You do not add entries on your own authority. You propose; he blesses.

### The house animation language (the bigger picture)

The Motion Bible sits inside a committed house animation language with two halves:

- **Visual half — Kage Kit:** ink/bone/vermilion palette, kicker-title-lede component order, glass cards. Every web UI build starts from the Kage Kit component tokens. No new hex codes, no ad-hoc component styles.
- **Motion half — the Kowalski register:** durations **150ms / 220ms / 400ms**, **60ms stagger** between sequenced items, three named easing curves, and a hard rule: **transform + opacity only, never `scale(0)`** (scaling to zero breaks compositing and looks cheap; fade + slight translate instead).

The register values, as CSS custom properties:

```css
--duration-fast: 150ms;
--duration-normal: 220ms;
--duration-slow: 400ms;
--stagger: 60ms;
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

Use the Motion Bible entries for *pointer-driven and ambient motion*; use the Kowalski register for *UI transitions* (hovers, reveals, drawers, sequenced entrances). They are complementary, not competing.

### Where everything lives

- `motion-bible/MOTION-BIBLE.md` — the bible itself (this document's Part 2, verbatim).
- `motion-bible/feel-type.js` — Entry 001 module (~7 KB, framework-free).
- `motion-bible/cursor-follower.js` — Entry 002 module (~7 KB, framework-free).
- `motion-bible/magnetic.js` — Entry 003 module (~4 KB, framework-free).
- `motion-bible/fonts/RobotoFlex-Variable.woff2` — full variable font for Entry 001.
- `your_files/mouse-type-hub.html` — the original prototype sketch all three entries were extracted from.
- `your_files/motion-bible-viewer.html` — self-contained viewer (~360 KB): live interactive demos of all three entries, each with a tap-to-try demo, the six laws, options tables, tuning notes, and a floating "fix it" bug-report loop (tap broken element → describe → copies a structured bug report to paste back into chat).

### The taste, in one paragraph

Motion here is *physical and honest*. The pointer is a hand, not a trigger. Things the hand drives respond with zero lag; things that follow earn their spring. Nothing pops, nothing snaps between states, nothing moves without a reason. Rest states are designed, not defaulted — the page must look good frozen, because reduced-motion users and first paint both see the rest state. The iPhone is the terminal: every pointer-driven entry listens to touchmove too.

---

## PART 2 — THE MOTION BIBLE (verbatim)

### The Laws (apply to every entry)

1. **Direct linkage.** The input (pointer, scroll) IS the animation state. No easing, lerp, or tween sits between the input and the thing it drives. Easing there is stupid — his word, and he's right: lag between hand and response reads as broken, not smooth.
2. **Followers may lag, drivers may not.** Objects that *follow* (a hub, a parallax layer) earn their spring. Things the pointer *drives* (glyphs, scrub states) get the raw value, every frame.
3. **Measure once, never per frame.** Cache geometry on load / resize / font-ready. Per-frame work is arithmetic on cached numbers only.
4. **Falloff, not cliff.** Influence decays across a radius (linear or smoothstep). Nothing pops between two states at a boundary.
5. **Rest state must look good static.** Reduced-motion, no-JS, and first paint all show the rest state — it has to stand on its own.
6. **Touch is a pointer.** Every pointer-driven entry also listens to touchmove. The iPhone is the terminal.

---

### Entry 001 — Feel Type

*Cursor-reactive variable-font typography. Blessed 2026-09-21.*
*Prototype: `your_files/mouse-type-hub.html` (the page was the sketch; this entry is the keeper).*

Each glyph's variable-font axes are a direct function of its distance to the pointer. Inside the radius, letters go heavy, wide, and slanted as the cursor approaches; outside it they rest light and narrow. A small repel push (a few px, away from the pointer) sells the physicality.

**Module:** `feel-type.js` — `FeelType.mount(container, options)`. Framework-free, ~7 KB. Returns `{ measure, refresh, destroy }`.

```html
<div id="hero"></div>
<script src="feel-type.js"></script>
<script>
  FeelType.mount(document.getElementById('hero'), {
    lines: ['TYPE THAT', 'FEELS YOU']
  });
</script>
```

**Options** (defaults shown):

| option | default | notes |
|---|---|---|
| `lines` | `['FEEL TYPE']` | one string per line |
| `radius` | `260` | px influence radius |
| `falloff` | `'linear'` | `'linear'` or `'smooth'` (smoothstep) |
| `repel` | `14` | max px push away from pointer; `0` disables |
| `rest` | wght 160, wdth 100, slnt 0, opsz 40 | the far-away look |
| `peak` | wght 900, wdth 151, slnt −10, opsz 120 | the under-cursor look |
| `staticState` | wght 420, wdth 100, slnt 0, opsz 60 | reduced-motion / first paint |
| `fontFamily` | Roboto Flex stack | needs a variable font with these axes |

**Font:** `fonts/RobotoFlex-Variable.woff2` (250 KB, full variable). Wire it up:

```css
@font-face {
  font-family: 'Roboto Flex';
  src: url('fonts/RobotoFlex-Variable.woff2') format('woff2');
  font-weight: 100 1000;
  font-stretch: 25% 151%;
}
```

Any variable font with `wght` works; `wdth`/`slnt`/`opsz` degrade gracefully if the font lacks the axis (the browser just ignores it).

**Tuning notes from the prototype:**
- 260px radius reads well on desktop; on phones it wants ~180px — pass a smaller radius when `matchMedia('(pointer: coarse)')` matches.
- The repel push past ~20px starts to look seasick. 10–14 is the zone.
- Peak slant beyond −12° hurts legibility on caps. −8 to −10 is safe.
- rAF runs only on demand (pointermove / scroll / resize kick a frame), not on a perpetual loop — the prototype ran hot, this doesn't.

---

### Entry 002 — Cursor Follower

*A spring-lagged follower that trails the pointer. Blessed 2026-09-21.*
*Prototype: the red-glow hub orb in `your_files/mouse-type-hub.html`.*

The canonical follower (bible law #2 in action). It chases the pointer with a per-frame ease, targeted at pointer + offset so it never covers the cursor. It can be grabbed and re-parked; on release it resumes following from the new spot. A press without movement counts as a tap. Reduced-motion parks it in a corner — still tappable, just not following.

**Module:** `cursor-follower.js` — `Follower.mount(el, options)`. Returns `{ pause, resume, park(x, y), follow, position, destroy }`.

```html
<div id="orb"></div>
<script src="cursor-follower.js"></script>
<script>
  Follower.mount(document.getElementById('orb'), {
    onTap: function(el){ /* open the card */ }
  });
</script>
```

**Options** (defaults shown):

| option | default | notes |
|---|---|---|
| `offset` | x 34, y 40 | target = pointer + offset; keeps it off the cursor |
| `ease` | `0.14` | per-frame chase; higher = tighter, lower = dreamier |
| `draggable` | `true` | drag re-parks; release resumes following |
| `tapSlop` | `6` | px of movement before a press stops being a tap |
| `parkOnReducedMotion` | `true` | reduced-motion: corner-parked, still tappable |
| `onTap` | `null` | fired on tap, Enter, or Space |
| `startX` / `startY` | bottom-right | initial position |

**Tuning notes from the prototype:**
- Ease 0.14 reads "close but alive." Below 0.08 it feels drunk; above 0.25 the lag is imperceptible and you may as well hard-attach.
- The offset is the personality: (34, 40) sits down-right of the cursor like a sidekick. Flip the sign to sit it elsewhere.
- While dragging, the loop sleeps and the element hard-tracks the pointer — a dragged thing is *held*, not followed (law #2 again).
- Settles to sleep: the rAF loop stops ~1.5s after parking instead of burning frames forever. The prototype ran hot; this doesn't.

---

### Entry 003 — Magnetic

*Eased magnetic parallax: an element leans toward the pointer. Blessed 2026-09-21.*
*Prototype: the hero-image drift in `your_files/mouse-type-hub.html`.*

An object with weight. The pull is the pointer's offset from the stage center times a strength, clamped to a short leash — the element leans but never chases the cursor off-stage. Eased, because it's a follower.

**Module:** `magnetic.js` — `Magnetic.mount(el, stage, options)`. Stage defaults to the element's parent. Returns `{ retarget, destroy }`.

```html
<div id="stage"><img id="hero" src="..."></div>
<script src="magnetic.js"></script>
<script>
  Magnetic.mount(document.getElementById('hero'),
                 document.getElementById('stage'));
</script>
```

**Options** (defaults shown):

| option | default | notes |
|---|---|---|
| `strength` | `0.045` | fraction of (pointer − center) applied |
| `max` | `16` | px clamp — the leash length |
| `ease` | `0.07` | per-frame chase; lower = heavier |
| `disableOnTouch` | `false` | true: no pull on coarse pointers |

**Tuning notes from the prototype:**
- Strength 0.045 with a 16px clamp is a whisper — visible, never seasick. Past ~30px max it starts fighting the layout.
- Ease 0.07 is deliberately heavier than the follower's 0.14: a big image should feel like it has mass.
- Clamp *before* easing (on the target, not the render) — clamping the render fights the ease and stutters at the leash end.

---

### Entry 004 — (open)

Nothing waiting. The next blessed effect takes this slot.

---

## PART 3 — THE MODULES (full source, drop-in)

Framework-free, no dependencies, no build step. Copy any file as-is; each exposes one global (`FeelType`, `Follower`, `Magnetic`).
### feel-type.js (Entry 001)

```js
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
```

### cursor-follower.js (Entry 002)

```js
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
```

### magnetic.js (Entry 003)

```js
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

    function retarget() {
      if (!active) return;
      var r = stage.getBoundingClientRect();
      var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      var tx = (mouse.x - cx) * o.strength;
      var ty = (mouse.y - cy) * o.strength;
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

    window.addEventListener('pointermove', onPointerMove, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: true });

    return {
      retarget: retarget,
      destroy: function () {
        destroyed = true;
        if (rafId) cancelAnimationFrame(rafId);
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('touchmove', onTouchMove);
        el.style.transform = '';
      }
    };
  }

  global.Magnetic = { mount: mount, defaults: DEFAULTS };
})(typeof window !== 'undefined' ? window : this);
```

---

## PART 4 — HOW TO PROPOSE ENTRY 004 (or any new entry)

1. Build the toy first — a small standalone page that shows the effect in isolation, the way `mouse-type-hub.html` did.
2. Strip it to the mechanism: one module, one mount function, an options object with blessed defaults, tuning notes from the prototype.
3. Check it against all six laws. If it violates one, say which and why it still deserves the slot — or fix it.
4. Reduced-motion and touch behavior are not optional — spec them before proposing.
5. Present the proposal. He blesses; you canonize.

*End of handoff.*
