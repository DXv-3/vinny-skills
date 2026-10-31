---
name: flood-animation
description: Use when the user wants a "flood", "flooded", "flooding", "liquid rise", "water fill", "tide", "submerge", "overflow", or "drench" animation on any web page, hero, or component — liquid rising from the bottom of the viewport that ripples under the cursor and submerges the content. Also fires for water/liquid page transitions. Ships the zero-dependency flood.js spring-surface engine plus drop-in recipes and a CSS mini-flood tier for dashboards. NOT a general motion router (that is mengto-motion) — only flood/liquid/water language triggers this.
---

# Flood Animation — liquid tide engine

A self-contained Canvas-2D engine (`assets/flood.js` in this plugin) that floods any page
with rising water: a spring-simulated surface, cursor ripples, caustic light bands, rising
bubbles, and `[data-float]` content that bobs once submerged. Zero dependencies, one script
tag, reduced-motion safe.

## Fast path — 3 steps

1. Vendor the engine next to the target page. Find the installed copy (newest cached
   version by mtime — the cache keeps old versions after updates, never take the first
   match):
   `ls -td ~/.zcode/cli/plugins/cache/*/*/flood-motion/*/assets/flood.js 2>/dev/null | head -1`
   (fall back to this plugin's source dir). Copy — never move it.
2. Add before `</body>`:
   ```html
   <script src="flood.js" data-flood data-auto="3000" data-palette="tide"></script>
   ```
3. Mark 1–3 hero elements that should bob when submerged: add the `data-float` attribute.

## Engine API

| Call | Effect |
|---|---|
| `Flood.mount({palette, toggleKey, clickToggle})` | manual mount → controller |
| `ctrl.flood() / ctrl.drain() / ctrl.toggle()` | drive the water |
| `ctrl.setPalette(Flood.palettes.sunset)` | recolor live |
| `ctrl.destroy()` | remove canvas + all listeners |

Script-tag attributes: `data-flood` (auto-mount) · `data-auto="ms"` (flood after N ms) ·
`data-palette="tide|sunset|toxic|royal"` · `data-color`/`data-deep` (custom hexes) ·
`data-key="f"` (toggle key) · `data-click="off"` (disable click-to-flood).

## Tiers — pick by surface

- **Full canvas flood (this engine)** — heroes, marketing pages, teasers, demos, portfolio
  covers. Anywhere a dramatic moment is justified.
- **CSS mini-flood** for dashboards and dense UI (the calm tier): a bottom-anchored
  `::after` with an SVG wave data-URI rising via `transform: translateY()` on hover or
  scroll-trigger, 500–760ms ease-out. NEVER run the full canvas engine behind dense ops UI.
- **WebGL water** — only if the user explicitly asks for refraction/3D. Reuse the
  kyoto-night-walk lessons: three r149 UMD, emissive (not lit) colors, serve over http.

## House rules (mengto-motion doctrine)

- Reduced-motion: the engine auto-detects — linear ramp, no waves/bubbles/bob. Never strip
  this. It is the price of admission.
- transform/opacity only · DPR capped at 2 · pauses on hidden tab · `pointer-events: none`
  · canvas is `aria-hidden` (decorative; content stays readable underneath).
- No CDN. The engine is vendored beside the page. Keyboard `F` never hijacks Cmd/Ctrl+F.
- Click-to-flood ignores links, buttons, and form fields — real UI keeps working.

## Verify before reporting done

1. Serve, never open `file://` — `python3 -m http.server 8123` in the page's directory.
2. agent-browser screenshots at ~1s (dry) and ~6s (flooded): water must be visibly higher
   in the second frame.
3. Click toggles drain; `F` toggles; cursor dragged through the water changes the surface
   shape between frames.
4. Console clean.

## Pitfalls (learned the hard way)

- `document.currentScript` is null inside DOMContentLoaded — the engine captures it at
  parse time; don't "simplify" that.
- Surface velocities are per-1/60s-step on a fixed-step accumulator. naive dt-scaling
  makes springs explode on 120Hz displays.
- `getBoundingClientRect` includes transforms — floater rects are cached before any bob
  transform is applied; don't re-read them after.
- z-index is 2147483000: nothing draws above the water. That is the point. Pages needing
  an always-on-top layer (toasts) should call `destroy()`/`flood()` deliberately.
