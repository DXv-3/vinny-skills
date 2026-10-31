# The Melon-Jelly Recipe — stealable constants and line pointers

Proof artifact: **Melon Jelly Knife** (claude.ai artifact `RiTbBMEqgfNwgMHMTAhf5P`,
"Material Studies / No. 009") — a WebGPU XPBD soft-body watermelon slice you can
grab, stretch, twist, and cut. It is the reference implementation this skill was
minted from: ~3,100 lines, zero dependencies, hand-rolled Delaunay + XPBD + WGSL.

Local copies (read these, never re-fetch the artifact):
- `~/Projects/melon-jelly-study/melon-jelly-module.js` — the whole engine (153 KB, readable, commented)
- `~/Projects/melon-jelly-study/melon-jelly-artifact-full.html` — original frame HTML (has Claude frame preamble; module code has **zero** frame dependencies)

Line numbers refer to `melon-jelly-module.js`.

## Map of the file

| Lines | System |
|---|---|
| 9–93 | `SHAPE` constants, seeded PRNG, iq pie SDF, offset outline samples |
| 96–139 | Bowyer–Watson Delaunay (convex sets, few thousand points) |
| 141–211 | `hexLattice` + `buildSimMesh`: 2D Delaunay → prism extrusion → 4 tets/prism, orient positive, material regions |
| 223–330 | `buildRenderMesh`: beveled wall rings, Delaunay caps, seed ellipsoids, bubble spheres |
| 372–429 | `embed`: render-vertex → tet barycentric weights (the skinning contract) |
| 596–710 | `clipHalf` / `splitPiece` / `sdInner` / `pieceSamples` / `buildPieceSim` — the cutting geometry kit |
| 887–1194 | `SoftBody` — XPBD core (see constants below) |
| 1974–2364 | `Renderer` — WebGPU pipelines, shadow passes, post |
| 2365–2460 | palettes, honest no-WebGPU fallback, reduced-motion |
| 2461–2510 | `skin()` CPU skinning + per-frame normal rebuild; camera safe-rect |
| 2628–2800 | `planCut` / `performCut` / `installWorld` / knife poses / cut choreography |
| 3040–3080 | `window.__melon` test hook + fixed-step accumulator loop |

## The numbers that make it feel right

Physics (SoftBody, L.975–984, 1020–1024):
- `stepDt = 1/60`, `substeps = 10`, **1 iteration per substep** ("small steps" XPBD)
- gravity −9.81, friction 0.55, max speed 12 (velocity clamp)
- firmness 0..1 → edge compliance: `exp(ln 3.0 + (ln 0.05 − ln 3.0) · f)` (log scale)
- volume compliance: `1e-4 · (1 − 0.7·f)`
- damping 0..1 → edge relative-velocity decay rate: `2 + 40 · d²` (syrupy ⇄ lively)
- rind tets 0.3× firmness of flesh, pale 0.5× (region-based, L.971–972)
- air drag `exp(−0.08·dt)` free, `exp(−2.5·dt)` while held (the hand steadies it)
- settling bleed: KE < 2e-3 → velocity × ≥0.86 per step; NaN watchdog samples every 97th float → gentle reset (L.1098–1107)

Grab (L.1048–1090):
- pick radius 0.4, weight = smoothstep falloff `f²(3−2f)`
- bounded reach 2.2 units — "a strong stretch, never an unbounded one"
- while held, the grabbed patch is never driven below the floor: lift the whole patch (`grabTarget.y ≥ floor − lowest rotated offset`)

Cut (L.2628–2742):
- stroke sampled 49× by raycast → one vertical blade plane
- world plane → each piece's **rest frame** (undo best-fit rotation R) → 2D line `a·u + b·w = c` → polygon clip with a rounded-corner offset RC
- guards: `MAX_PIECES = 14`, `MIN_INNER_AREA` on both halves, pieces lying on their side (plane nearly parallel to thickness) are skipped
- plan on release → `buildWorld` while the knife is in the air → swap mid-stroke "when the edge breaks through"
- state carried across worlds by interpolating old positions/velocities through the barycentric embed; separated halves get lateral impulse + 0.35 hop
- choreography timings (L.2801): align 0.16s → press 0.42 → through 0.6 → hold 0.7 → lift 1.08

Rendering (WGSL_MAIN etc.):
- transmission: refract view ray at IOR **1.42**, march exit point, **7-tap** blurred scene sample behind, each tap absorbed by Beer–Lambert `exp(−σ·path)` with per-material σ; thickness along view ray from a back-face depth pass
- wrap diffuse `(NdL + 0.6)/1.6`; two depth passes: key 1024² + top fill 512², PCF comparison sampler, HDR `rgba16float` intermediates, MSAA 4
- materials (stripes, flesh gradient, speckle, grain) computed in **rest space** `i.rest` so they ride the deformation instead of swimming
- fbm/vnoise in-shader; stripe field `sin(th·34 + fbm·7 + …)` with smoothstep masks

Presentation:
- 1 sim unit ≈ 3.5 cm, density 1.3 g/cm³ → live mass/volume/µJ readouts with real unit math
- seeded PRNG (mulberry-style) → specimen identical on every load
- no WebGPU → dark plate + plain-language explanation, never a fake lesser render
- `window.__melon` exposes `performCut/advance/compStats/pieces/fps` for automated checks

## Gotchas that cost the author real time

- Edge list is shuffled once (L.943–948) — kills Gauss–Seidel directional bias (visible as directional stretching).
- Grab stiffness, not kinematics: an attachment constraint inside the solver, not `x = target` — kinematic pinning fights the solver and explodes.
- Re-delaunay **per cut piece**; never reuse the whole-slice mesh for fragments.
- Cut planes must be carried into each piece's rest frame — a world-space plane slices deformed pieces into garbage.
- If a render pass reads a texture it also writes, that's a feedback loop — this artifact uses separate scene/back/depth textures for exactly that reason.
- This Mac: in-app-browser webview exposes no `navigator.gpu` (verified 9/28 — the artifact correctly showed its dark fallback). Headless Chrome needs `--enable-unsafe-webgpu --use-angle=metal` for WebGPU QA; plain `--disable-gpu` kills it.
