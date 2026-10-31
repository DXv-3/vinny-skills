---
name: motion-bible
description: "Apply the Motion Bible — the blessed canon of pointer-driven motion — to any web build. Use whenever building, editing, or reviewing any web page, hero, landing page, dashboard, or component that moves: cursor-reactive typography, cursor followers, magnetic/parallax elements, pointer effects, kinetic variable-font type, motion polish, 'make it feel alive', 'add motion', 'cursor effect'. Carries the six laws, the Kowalski 150/220/400ms register, and three drop-in framework-free modules (FeelType, Follower, Magnetic) ready to copy into any project. Also use to PROPOSE new entries and to audit existing motion against the laws."
version: 1.0.0
---

# Motion Bible

The canon of how things move in Vinny's builds. Not a library, not a framework — a set of blessed mechanisms, each stripped to a drop-in module. An effect is only in the bible if he blessed it; you propose, he blesses (see the protocol at the bottom).

**Full canon** — options tables, tuning notes, complete module source, and the original handoff: read `references/handoff.md` before wiring any entry into a real build. The modules live in this skill's `scripts/` — copy them verbatim into the project, never re-type them.

## The six laws (apply to every entry)

1. **Direct linkage.** The input (pointer, scroll) IS the animation state. No easing, lerp, or tween between the input and the thing it drives — lag between hand and response reads as broken, not smooth.
2. **Followers may lag, drivers may not.** Things the pointer *follows* (hub orb, parallax layer) earn their spring. Things the pointer *drives* (glyphs, scrub states) get the raw value every frame.
3. **Measure once, never per frame.** Cache geometry on load / resize / font-ready; per-frame work is arithmetic on cached numbers only.
4. **Falloff, not cliff.** Influence decays across a radius (linear or smoothstep). Nothing pops between two states at a boundary.
5. **Rest state must look good static.** Reduced-motion, no-JS, and first paint all show the rest state — it has to stand on its own.
6. **Touch is a pointer.** Every pointer-driven entry also listens to `touchmove`. The iPhone is the terminal.

If a build under review violates a law, that's a finding: name the law, name the fix.

## The Kowalski register (UI transitions)

Use the bible entries for *pointer-driven and ambient motion*. Use the register for *UI transitions* — hovers, reveals, drawers, sequenced entrances:

```css
--duration-fast: 150ms;
--duration-normal: 220ms;
--duration-slow: 400ms;
--stagger: 60ms;
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

Hard rule: **transform + opacity only, never `scale(0)`** — fade + slight translate instead.

Boundary with neighbors: `pop-motion` owns CSS entrance keyframes and stagger galleries; Kage Kit owns the palette/components. This skill owns pointer physics and ambient motion. They layer — don't double-source one effect.

## Entry 001 — FeelType (cursor-reactive kinetic type)

Each glyph's variable-font axes are a direct function of distance to pointer: inside the radius letters go heavy, wide, slanted; outside they rest light. Small repel push sells physicality. This is a **driver** — no easing between pointer and glyph (law 1).

```html
<div id="hero"></div>
<script src="feel-type.js"></script>
<script>
  FeelType.mount(document.getElementById('hero'), { lines: ['TYPE THAT', 'FEELS YOU'] });
</script>
```

Needs a variable font with `wght` (+ `wdth`/`slnt`/`opsz` degrade gracefully). Verified font link:

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wdth,wght@8..144,25..151,100..1000&display=swap" rel="stylesheet" />
```

Tuning: radius 260 desktop / ~180 on `pointer: coarse`; repel 10–14px (past 20 reads seasick); peak slant −8 to −10 on caps.

## Entry 002 — Follower (spring-lagged cursor chaser)

The canonical follower (law 2). Chases the pointer per-frame ease, offset so it never covers the cursor. Draggable — grab re-parks, release resumes from the new spot. Press without movement = tap. Reduced-motion parks it in a corner, still tappable.

```js
const f = Follower.mount(document.getElementById('orb'), {
  onTap: (el) => { /* open the card */ },
});
// f.pause() / f.resume() / f.park(x, y) / f.follow() / f.destroy()
```

Tuning: ease 0.14 ("close but alive"; <0.08 drunk, >0.25 hard-attach). The offset (34, 40) is the personality — sidekick down-right; flip signs to move it. While dragging it hard-tracks (a held thing isn't followed). Settles to sleep ~1.5s after parking — rAF must never run perpetually.

Element needs `position: fixed` (or absolute), `left/top: 0`; it moves by transform.

## Entry 003 — Magnetic (eased magnetic parallax)

An element with weight leans toward the pointer: target = (pointer − stage center) × strength, clamped to a short leash, then eased (it's a follower — law 2). The shipped module caches stage geometry and remeasures on resize/scroll/ResizeObserver/font-ready (law 3).

```js
const m = Magnetic.mount(document.getElementById('hero'), document.getElementById('stage'));
// m.retarget() / m.measure() / m.destroy()
```

Tuning: strength 0.045, max 16px (a whisper; past ~30px it fights the layout), ease 0.07 — deliberately heavier than Follower's: a big image has mass. **Clamp before easing** (on the target, not the render) — clamping the render stutters at the leash end.

## Install recipe

1. Copy `scripts/feel-type.js`, `scripts/cursor-follower.js`, `scripts/magnetic.js` into the project (e.g. `public/motion-bible/`), unmodified.
2. Load them with plain `<script src="..." defer>` before the app script — each exposes one global (`FeelType`, `Follower`, `Magnetic`).
3. Add the font link (above) for FeelType; the other two need nothing.
4. Mount on load; call `.destroy()` on teardown. In a framework app, wrap mount/destroy in the component's mount/unmount lifecycle — but prefer keeping the page framework-free, matching the modules.

Worked example with all three wired into one app (load order, register tokens beside Kage tokens, draggable floating shortcut): `~/Projects/opendots-strip/opendots/`.

## Non-negotiables when building with the bible

- Every mount sets a designed static/reduced-motion state — never `if (reduceMotion) return;` with no rest styling.
- rAF on demand (pointermove/scroll/resize kick a frame), never a perpetual loop; loops settle to sleep when parked.
- All pointer listeners `passive: true`; resize/scroll handlers remeasure cached geometry.
- Nothing new gets invented for a one-off build if a blessed entry covers it — reach for the module first.

## Proposing Entry 004+

1. Build the toy — a small standalone page showing the effect in isolation.
2. Strip to the mechanism: one module, one `mount`, options object with blessed defaults, tuning notes.
3. Check all six laws; name any violation and the fix.
4. Spec reduced-motion + touch behavior before proposing — they are not optional.
5. Present the proposal. **He blesses; you canonize.** Never self-insert an entry.
