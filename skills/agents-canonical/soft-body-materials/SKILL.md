---
name: soft-body-materials
description: Build web objects made of deformable solid material — jelly, rubber, dough, slime, gummy, foam — that squash, wobble, tear, and get cut in real time. Mechanism a coarse tetrahedral XPBD solve with a fine surface mesh skinned to it by barycentric embedding, rendered on raw WebGPU (WGSL, transmission, shadow passes) with a three.js fallback ladder, a soft-grab/twist/cut interaction grammar, honest capability fallback, and a window hook for programmatic QA. Use when a thing must squish, jiggle, deform, split into pieces, or respond to touch as a physical solid whose silhouette changes. Not for rigid hero objects, 2D rigid-body physics, surface-only water or terrain, or SVG gooey illusions.
---

# Soft-Body Materials

**The mechanism, one sentence:** a solid feels physically real when its visible surface is only skin over a coarse deformable skeleton and every motion on screen is the consequence of one constraint solve — delete the solve and the thing collapses into a morph, which is how you know this skill applied.

Minted from the Melon Jelly Knife study (WebGPU XPBD watermelon slice, ~3,100 lines, zero dependencies). Full constants, line pointers, and gotchas: [references/melon-jelly-recipe.md](references/melon-jelly-recipe.md). Proof copies at `~/Projects/melon-jelly-study/`.

## The ladder — where this skill sits

| Need | Skill |
|---|---|
| UI springs, hover micro-motion | `pop-motion` |
| Dust, sparks, cursor trails (points, no volume) | `mengto-build-interactive-particle-trail` |
| Hard bodies that stack and tumble, 2D | `mengto-matterjs` |
| Surface that ripples (ocean, terrain, touch ripples) | `mengto-3d-ultra-realistic-water`, `mengto-threejs-landscape`, `mengto-shaders-cursor-ripples` |
| Blob merge *illusion* (SVG filters, no physics) | `mengto-gooey-blob-system` |
| **Solid that bends, squashes, jiggles, and can be cut** | **this skill** |
| Journey/scroll framing around any of the above | `mengto-build-threejs-scroll-worlds` |

**The decision rule:** if the silhouette must change and volume must be roughly conserved, you need a tetrahedral solve. If a vertex-shader wobble (`sin(pos + t)`) survives your squint test, that is staging, not physics — use the cheap thing. The squint test: freeze the frame mid-deform. If a still of the *deformed* state would look wrong (bent ruler, pinched cube), you need this skill; if it would look fine, it's motion, not material.

## Architecture: two meshes, one solve

Never solve the render mesh. Never render the solve mesh.

1. **Sim mesh** — coarse tetrahedra (~hundreds): generated from the 2D outline SDF → hex lattice interior + spaced boundary samples → Bowyer–Watson Delaunay (~45 lines, write it, don't import it) → prisms split into 4 tets each, all oriented positive volume. Mass per particle from rest tet volume × density.
2. **Render mesh** — fine surface (bevels, caps, details): every vertex stores **4 tet indices + barycentric weights**, found once at build time by locating it inside the tet grid. Each frame: skin positions on the CPU (or in a vertex shader if count demands), rebuild normals from the deformed triangles. This is cloth-style skinning pointed at solids.

Consequences worth paying for: cutting only rebuilds cheap tet meshes; detail (seeds, bubbles, engravings) rides for free; LOD = retarget the weights.

## The solve: small-steps XPBD

Fixed 60 Hz accumulator, 10 substeps, **1 iteration per substep** — small steps beat many iterations for stability per millisecond. Per substep: integrate (gravity, air drag) → grab constraint → per-tet shape match → per-tet volume → inter-piece collision (alternate substeps) → blade → floor → derive velocities with a speed clamp.

- **Elasticity** = co-rotational shape matching: pull each tet toward its rest shape *rotated* to best-fit the current one (warm-started quaternion). This one choice recovers inverted tets and removes the jelly-flip failure mode.
- **Incompressibility** = one volume constraint per tet toward rest volume.
- **The feel dial** = relative-velocity damping along tet edges (rate `2 + 40·damping²`) — this, not stiffness, is what separates syrupy from lively from trembling. Map UI firmness to compliance **logarithmically**, and give outer-material tets lower stiffness (rind 0.3×, flesh 1.0×) so the surface yields like skin.
- **Grab** = a soft attachment constraint with smoothstep falloff over a radius — never kinematic pinning, which fights the solver and explodes. Cap the reach ("a strong stretch, never an unbounded one") and never let the held patch be driven through the floor.
- **Hardening** (non-negotiable): velocity clamp; once-a-frame NaN watchdog with gentle reset; settling bleed that decays residual jitter below a kinetic-energy threshold; seeded PRNG so the specimen is identical every load.

## Cutting: planes in rest frames

A stroke becomes one vertical blade plane; each piece it crosses is split **in its own rest frame** — undo the piece's best-fit rotation, the plane becomes a straight line, clip the 2D outline polygon (rounded corners), then re-Delaunay each half into a fresh tet mesh. Never slice deforming geometry in world space; never reuse the whole-body mesh for fragments. Choreography: plan the rebuild at release (heavy work while the knife is still up), swap worlds mid-animation at the moment the edge breaks through, carry positions/velocities across by interpolating through the embed, and push the halves apart with a lateral impulse plus a small hop. Guards: max pieces (14 is a good ceiling), minimum-area per half, skip pieces lying on their side.

## Renderer ladder

1. **Raw WebGPU** when the look earns it — transmission/refraction, real shadow passes, HDR intermediates. Non-negotiables: separate textures per pass (a pass reading what it writes is a feedback loop), `rgba16float` scene targets, `getPreferredCanvasFormat`, depth-bias on shadow passes, materials computed in **rest space** so texture fields ride the deformation instead of swimming.
2. **three.js** (local r149+ UMD, never CDN — house rule) when reach matters: `MeshPhysicalMaterial` with `transmission` + `thickness` approximates the jelly look; the XPBD core and skinning are unchanged, only the upload target differs.
3. **Honest fallback** when the API is missing: a designed dark state that says plainly what's needed. Never fake the material with a lesser renderer and never show a broken canvas — the study stays dark, and says why.

## Interaction grammar

What makes it feel alive is response grammar, not FPS: grab-and-pull with visible inertia; twist while holding (wheel or second finger); a "nudge" that is a real impulse (v = v_lin + ω×r); cut as a little piece of choreography (align → press → through → hold → lift). Always ship: ¼-speed toggle, show-mesh/wireframe toggle, pause, keyboard shortcuts, toasts instead of alerts, reduced-motion honored (render the resting pose, allow direct interaction only).

## Presentation: the specimen plate

Frame the object as a study, not a demo: title, figure number, material palette, live readouts with **real unit math** (declare the scale — "1 unit ≈ 3.5 cm, 1.3 g/cm³" — and derive mass/volume/energy from the actual solve, never animate fake numbers). This costs one overlay and buys the "went to school" register. Taste stays with `frontend-design`; tokens stay Kage (ink/bone/vermilion overrides, no new hex).

## QA gates (all required before claiming it works)

1. `node --check` on every JS chunk before any browser work.
2. Serve over `http.server` — module scripts and UMD workers die on `file://`.
3. Screenshot gate per chunk at 1440px + 390px via local headless Chrome (`visual-self-review-loop`). WebGPU builds need `--enable-unsafe-webgpu --use-angle=metal`; `--disable-gpu` silently drops to fallback. Open every WebGL QA with a mean-brightness probe (house rule — a black canvas is the #1 silent failure).
4. Programmatic sim checks through a page hook (`window.__thing = { sim, advance(sec), compStats(), pieces }`): advance N seconds, assert piece count after a scripted cut, assert energy decays (KE trending down at rest), assert no NaN.
5. Force the fallback path (`navigator.gpu` blocked) and verify the dark state renders and reads well.
6. Final acceptance via `mengto-iterate-until-verified`.
