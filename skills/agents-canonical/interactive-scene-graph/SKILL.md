---
name: interactive-scene-graph
description: "Build data-driven interactive visual scenes: JSON nodes/edges/status → layout → SVG or Canvas/WebGL render → inertial pan/zoom/focus camera → hit-testing → live data binding → ⌘K jump-to-node palette. Use when building a node graph, dependency map, network explorer, infinite canvas, live-status diagram, or any 'render this JSON as an interactive scene' ask. Includes the SVG-vs-Canvas/WebGL decision rule (object count, shaders, post-processing)."
---

# Interactive Scene Graph

One pipeline, one direction of truth: **scene JSON → layout → render → camera → interaction**. The scene is data, the camera is runtime state, and the render is a pure function of both. This is the shared structure layer for data-driven visual scenes — SVG diagrams, 2D canvas maps, and WebGL universes reuse the same spine and swap only the renderer.

Delegation: taste and atmosphere → `frontend-design`; CSS micro-interaction mechanics → `pop-motion`; a11y/touch/contrast rules → `ui-ux-pro-max` (query its `--domain` DB, never copy checklist items). This skill owns the graph spine: schema, layout, renderer choice, camera, hit-testing, binding, palette.

## When to Use

- "Build an interactive node graph / dependency map / network explorer / org chart from this data"
- "Render this JSON as an interactive scene" — clickable nodes, live status colors
- Infinite-canvas surface: drag with snap, marquee select, undo/redo, serialize
- A dashboard that needs ⌘K jump-to-node with a camera fly-to
- Skip: scroll-told pages → `mengto-cinematic-gsap-lenis-motion-system`; persistent 3D worlds → `mengto-build-threejs-scroll-worlds`; level semantics → `mengto-author-game-levels`; pure CSS motion → `pop-motion`.

## Mandatory Rules

### 1. The scene is JSON — single source of truth

```json
{
  "nodes": [
    { "id": "web", "type": "client", "label": "Web", "w": 140, "h": 48, "status": "ok" },
    { "id": "api", "type": "service", "label": "API", "x": 320, "y": 120, "w": 140, "h": 48,
      "status": "degraded", "data": { "rps": 812 } }
  ],
  "edges": [ { "id": "e1", "from": "web", "to": "api", "kind": "calls" } ],
  "meta": { "seed": 0, "version": 1 }
}
```

`x`/`y` are **optional seeds**, never authoritative positions: present → the force pass starts there and grid/rank treat them as pins; absent → the seeded PRNG places the node (rule 2). `z` optional (default 0) = draw/hit order. Camera, selection, and hover are **runtime state, never scene data**. Same JSON in → same scene out, every load.

### 2. Layout is a pure function with a fixed seed contract

`(scene, viewport) → positioned scene`. Deterministic: topological ranks for DAGs and grid/radial are coordinate-free except for pins; the one-shot force pass (<500 nodes only) seeds `meta.seed` (default 0) into mulberry32 — **never `Math.random()`** — and runs a fixed iteration count. That seed contract is what makes the "identical coordinates on reload" QA gate checkable. **NEVER run layout per frame** — re-layout only when nodes or edges change. Rebuild the hit-grid here: insert every node into every cell its bounds overlap.

### 3. Render is a pure function of (scene, camera, viewport)

SVG: keep elements keyed by `data-id` and update in place — creation is for new ids only. Canvas: set `canvas.width = cssW · devicePixelRatio` and `ctx.scale(dpr, dpr)` once per resize; all camera math stays in CSS pixels. Edges render in a layer **under** nodes: cubic bezier between the nearest ports, control points offset by half the dx (half the dy for vertical flow); arrowhead at the target port; `kind` as the midpoint label on a bone chip, hidden when `k < 0.6`; self-loops as a 24-world-unit loop off the node's side.

### 4. Renderer: the decision rule

| Renderer | Choose when | Hit-testing | Cost watch |
|---|---|---|---|
| SVG | ≤1,000 visible elements; crisp text, CSS hover, a11y | DOM events per element | DOM churn past ~2k nodes → jank |
| Canvas 2D | 1k–20k objects, no shaders, zero deps | Manual: invert camera + spatial grid | Full repaint each frame; DPR per rule 3 |
| WebGL (PixiJS v8 / three.js) | >20k objects, custom shaders, post-processing | Raycast / GPU pick + spatial grid | `webglcontextlost` → preventDefault, rebuild GPU resources on restore — PixiJS v8 recovers only some texture types internally, so wire the listener yourself |

**Default SVG.** Escalate to Canvas 2D on count, to WebGL only when you need shaders or post-processing (bloom / depth-of-field / god rays via pmndrs/postprocessing) — never for vibes. PixiJS v8 (WebGPU→WebGL) is the right 2D scale before three.js; three.js only for true 3D, CinematicCamera DOF, or CatmullRomCurve3 rigs.

### 5. The camera owns every pixel move

Camera = `{ x, y, k }`; `screen = world · k + (x, y)`; inverse `world = (screen − (x, y)) / k`. Input mutates **only** the camera, and any pointer/wheel input must first set `cam.target = null` — otherwise a stale focus tween drags the camera back mid-pan. d3-zoom (ISC) gives wheel/pinch + programmatic focus transitions but ships **no inertia** (open request: d3/d3-zoom#67) — add it yourself: track pointer velocity during pan; on release keep moving with `v *= Math.exp(-5·dt)` (frame-rate independent) until speed <0.01px/s. pixi-viewport is the PixiJS-side equivalent. Zoom at the cursor — the world point under it stays fixed:

```js
const k2 = Math.min(4, Math.max(0.25, cam.k * factor));
cam.x = sx - (sx - cam.x) * (k2 / cam.k);   // x' = sx − (sx − x)·k′/k
cam.y = sy - (sy - cam.y) * (k2 / cam.k);
cam.k = k2;
```

Focus is an ease through the same API:

```js
function focusNode(id, targetK = 1.25) {
  const n = byId(id);
  cam.target = { x: vw / 2 - n.x * targetK, y: vh / 2 - n.y * targetK, k: targetK };
}
// in the one rAF loop; settled = |Δ| < 0.5px → snap exactly, clear cam.target:
if (cam.target) {
  const s = 1 - Math.exp(-dt * 10);   // rate 10/s: 95% closed in 0.3s, 99.3% in 0.5s
  cam.x += (cam.target.x - cam.x) * s;
  cam.y += (cam.target.y - cam.y) * s;
  cam.k += (cam.target.k - cam.k) * s;
}
```

Exp ease is the camera mechanism — pop-motion's CSS tokens (incl. `--motion-ease-spring`) cannot drive a rAF loop. Under `prefers-reduced-motion`, snap instead of tween (pop-motion's a11y lock).

### 6. Hit-test through the camera inverse

SVG: plain DOM listeners. Canvas/WebGL: invert the transform, query the layout-built grid (rule 2: cell + 8 neighbors), take the max by `z ?? 0`, ties broken by insertion order:

```js
const toWorld = (sx, sy) => [(sx - cam.x) / cam.k, (sy - cam.y) / cam.k];
const [wx, wy] = toWorld(e.offsetX, e.offsetY);
const hit = grid.query(wx, wy)[0];
```

**NEVER** attach per-element listeners in canvas mode and **NEVER** hit-test against raw screen coords.

### 7. Live data binds by diff

`applyData(patch)` mutates node `status`/`data`, marks layout dirty only if structure changed, and coalesces a single rAF flush. New data never re-creates elements (rule 3). A 10 Hz feed must hold 60 fps. Status vocabulary is `ok / degraded / down / idle`, mapped to Kage Kit tokens by opacity only — **no new hex codes** (house doctrine):

| status | node fill | dot / accent |
|---|---|---|
| ok | `--bone` | `--ink` @ 60% |
| degraded | `--bone` | `--vermilion` @ 55% |
| down | `--vermilion` @ 15% | `--vermilion` @ 100% |
| idle | `--bone` @ 55% | `--ink` @ 35% |

### 8. ⌘K jumps through the same camera API

```js
// ⌘K → input → fuzzy match on id + label → Enter:
palette.onSelect = (id) => { focusNode(id); pulse(id); };   // pulse = pop-motion overshoot arc, CSS layer
```

The palette is a client of the camera, never a second mover. Keyboard-only: `/` opens, arrows move selection, `Esc` returns to the previous camera position (keep a 1-deep camera history).

## Infinite-canvas extras (borrow, don't reinvent)

- Pointer-capture drag with 32px snap; marquee multi-select on empty-space drag; orthogonal connector routing in editable mode (read-only scenes keep rule 3 beziers).
- Bounded undo/redo (50 steps) over inverse patches; serialize with JSON Canvas (obsidianmd/jsoncanvas, MIT).
- Study Excalidraw (MIT) and xyflow (MIT) for interaction patterns; tldraw carries a custom source-available watermark license (non-commercial without payment) — reference-only, study don't copy.
- Physics-playful objects: matterjs (`mengto-matterjs`); GPU particles: three.quarks (MIT).

## Perf pass

- One rAF loop drains camera easing, binding flushes, and repaints. stats.js FPS panel + Spector.js GPU capture while tuning.
- Tune rig numbers live with lil-gui (MIT) during development, then bake final values; never ship the GUI.
- Authored camera paths: theatre.js keyframes offline → export JSON → bake; never a runtime dependency.

## QA Checklist

- [ ] Same scene JSON → identical layout coordinates on every reload (seeded PRNG per rule 2)
- [ ] Wheel-zoom keeps the world point under the cursor fixed (rule 5 math); zoom clamped to [0.25, 4]
- [ ] Pan during a focus tween cancels it (`cam.target = null`); camera never pulls back mid-pan
- [ ] ⌘K → Enter lands the node at viewport center at target zoom: residual <1% of initial camera distance at 500ms (rate 10/s ⇒ ~0.7%), then snaps <0.5px
- [ ] Hit-test correct at 0.5× and 2× zoom; returns the topmost node by z
- [ ] Edges render under nodes with arrowheads; edge labels hidden at k < 0.6
- [ ] 10 Hz data feed for 60s: 60 fps, flat heap (diffed, not re-created)
- [ ] Reduced-motion: camera snaps, no tween (pop-motion lock)
- [ ] Browser-verified at 1440px + 390px per `mengto-iterate-until-verified`

## Boundaries & References

Packaged per the `mengto-web-technique-to-skill` constitution: mechanism-not-adjectives, real numbers, declared boundaries, browser-verified before "done".

- Taste/direction: `frontend-design` · UX/a11y rulebook + `--domain` search: `ui-ux-pro-max` · CSS motion: `pop-motion` (read its reference gallery first)
- Scroll-driven motion language: `mengto-cinematic-gsap-lenis-motion-system` — this skill is camera-driven, not scroll-driven
- Three.js API/library knowledge: `mengto-threejs`; physics: `mengto-matterjs`; components/shaders to lift: `threeui-reference`
- Scene-graph neighbours this skill underpins: `mengto-build-threejs-scroll-worlds` (persistent worlds), `mengto-author-game-levels` (deterministic level data feeds in as scene JSON), plus game systems riding the same graph: `mengto-build-game-camera-controls`, `mengto-build-game-map-editor`, `mengto-implement-fog-of-war`, `mengto-design-game-encounters`, `mengto-build-threejs-enemy-systems`
- Orbit/tour/globe specifics: `mengto-add-mouse-driven-orbit`, `mengto-3d-virtual-tour`, `mengto-globe-gl`; procedural assets: `img2threejs`
- Apple-native equivalents: `scenekit`, `realitykit`, `spritekit`
