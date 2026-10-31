---
name: edge-beauty
description: Edge-case motion lanes NOT covered by the mengto-* corpus — native CSS scroll-driven animations, View Transitions API (page + theme-toggle wow), GLSL transition galleries, SVG morph technique, variable-font headline animation, magnetic elements. Use when the router (mengto-motion) hits a surface these lanes serve better than GSAP/Three.js, or when the user asks for page transitions, theme toggles, icon morphs, or scroll-linked motion without libraries.
---

# Edge Beauty — the pantry

Six lanes the corpus lacks, researched 2026-09-26 (`~/Documents/research/github-edge-animation-beauty-2026-09-26.md`). All lanes obey the router's hard laws: GPU-only properties, reduced-motion = gentler-not-zero rendering final states, one lane per page, no CDN (vendor inline).

## Lane 1 — CSS scroll-driven animations (native, ZERO JS)

`animation-timeline: view()` / `scroll()` + `animation-range`. The 2026 native shift — reveal-on-scroll, progress bars, parallax-lite with no GSAP, no Lenis, no scroll listener.

- **Pick when**: simple reveals, progress indicators, sticky-section effects on content sites where adding a scroll engine is overkill.
- **Recipe**: `@supports (animation-timeline: view())` gate → `.reveal { animation: fade-rise linear both; animation-timeline: view(); animation-range: entry 0% entry 60%; }` — keys use ONLY transform/opacity.
- **Fallback**: elements are visible by default without support (progressive enhancement — never hide content behind an unsupported timeline).
- **QA**: bramus/scroll-driven-animations-debugger-extension (Chrome DevRel, 2026-09 active). Working proofs: barvian/CodropsCarousels (100★), viliket/pure-web-bottom-sheet (67★, 2026-09).
- **Rule**: this lane replaces GSAP ONLY for simple linear effects; choreographed sequences still go to ScrollTrigger.

## Lane 2 — View Transitions API (same-document FLIP, free)

`document.startViewTransition(updateCallback)` — the browser snapshots old/new states and animates the change. FLIP without writing FLIP.

- **Pick when**: state swaps that jump (theme, list reorder, card expand, tab panels), MPA navigation polish (`@view-transition { navigation: auto; }`), React/Next via `next-view-transitions` (shuding, 2.4K★; Vercel's official skill: `vercel-labs/agent-skills@vercel-react-view-transitions`, 132.9K installs).
- **Recipe**: `::view-transition-old(root)/new(root)` crossfade by default; name elements with `view-transition-name` for shared-element morphs (thumbnail → detail hero).
- **Reduced-motion**: `::view-transition-group(*) { animation: none }` under the media query — instant swap, no flash.
- **Signature move** (theme-toggle-effect pattern, 813★): circular reveal expanding from the toggle button — `clip-path: circle()` on `::view-transition-new(root)` keyed from the button's coordinates.

## Lane 3 — GLSL transition gallery

**gl-transitions** (the canonical MIT gallery, 80+ shaders — `gre/glsl-transitions` is deprecated, use gl-transitions).

- **Pick when**: canvas/image/page wipes in WebGL lanes (pairs with `mengto-vantajs`, `mengto-webgl-3d-object`, hero image crossfades).
- **Rule**: vendor the ONE shader inline; uniform-driven progress; cap ONE GLSL transition per page; DPR + dispose laws apply.

## Lane 4 — SVG morph (technique, not dependency)

Icon→icon morphs, menu/hamburger morphs, blob shapes. Reference libs (SVG-Morpheus 2.7K★, react-svg-morph 820★) are DEAD — lift the technique, never the dependency.

- **Recipe**: same point-count paths only → interpolate `d`/`points` via WAAPI `d: path("...")` (Chrome) or requestAnimationFrame lerp with a custom ease-out; `transform-box: fill-box` for origin-correct scaling.
- **Fallback**: crossfade + scale when path counts mismatch (normalize first or don't morph).

## Lane 5 — Variable-font headline animation

`font-variation-settings` animated via WAAPI/CSS — weight sweeps on load, width on hover, grade on focus. **Dead zone upstream** (nothing above 12★) — this is the house recipe.

- **Recipe**: `@keyframes wght { from { font-variation-settings: "wght" 200 } to { "wght" 800 } }` on ` .hero h1`, 800–1600ms hero token, ease-out. Axis names need the font actually loaded (variable webfont subset).
- **Reduced-motion**: static final weight. **GPU note**: text repaints (paint tier) — headlines only, never body copy, never 100+/day surfaces.

## Lane 6 — Magnetic elements + cursor (pointer:fine ONLY)

Corpus has shader trails (`mengto-shaders-cursor-ripples`) and orbit (`mengto-add-mouse-driven-orbit`); this is the plain-DOM tier.

- **Recipe**: magnetic buttons = translate element toward pointer inside a proximity radius with the house damping formula `1-(1-0.055)^(dt*60)`; custom cursor = fixed element + rAF lerp; BOTH hard-gated behind `@media (pointer: fine)` and disabled entirely on reduced-motion (cursor replacement breaks the OS contract — keep the native cursor visible, decorative ring only).
- **Cap**: magnetic + one cursor system max; never both a shader trail AND a custom cursor.

## Picking the lane

| Request | Lane |
|---|---|
| "scroll reveal, no libraries" | 1 |
| "smooth page/nav transitions" | 2 |
| "wow theme toggle" | 2 (circular reveal) |
| "cinematic image wipe" | 3 |
| "icons that morph" | 4 |
| "headline that breathes" | 5 |
| "buttons that lean into the mouse" | 6 |
| choreographed sequences, pinned scenes | NOT these lanes — GSAP/ScrollTrigger (router Step 0) |
