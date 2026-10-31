---
name: blender-for-agents
description: Drive Blender headlessly as a 3D build/render/export engine for agents — BFA MCP (bfa_scene/bfa_build/bfa_render/bfa_io/bfa_code) over a warm JSON kernel. Use when any task needs 3D modeling, rendering images of scenes, or exporting glTF/FBX/OBJ/STL assets.
---

# Blender for Agents (BFA)

Blender 5.2.2 LTS driven headless. Warm kernel = ~3s once, then sub-second commands.
Full loop (build + render + export) in ~5s. Cycles CPU renders: 512px/48spp ≈ 6s.

## Tools (MCP server "bfa")

- **bfa_scene** — `action=overview` (all objects: name/type/loc/rot/scale/verts/mats) or `action=detail` + `name` (bbox, modifiers, material colors, custom props).
- **bfa_build** — verbs: `create` (types: cube sphere cylinder plane torus cone monkey grid circle light camera empty text; opts location, rotation (DEGREES), scale, material, color [r,g,b], metallic, roughness), `transform` (name + location/rotation/scale/parent), `delete` (name or names[]), `modifier_add` (name, type e.g. SUBSURF/MIRROR/BEVEL/SOLIDIFY, settings{}), `modifier_apply`, `material_set`, `camera_frame` (camera, target, location, lens), `reset` (empty scene).
- **bfa_render** — returns an IMAGE you can see. engine=cycles (default; `eevee` auto-falls back — EEVEE hangs headless on macOS), samples (default 32), res (default 512), camera, transparent, or `mode=file` + path to write a PNG.
- **bfa_io** — import/export gltf(glb)/obj/fbx/stl/ply/usd. direction, format, path.
- **bfa_code** — escape hatch: `mode=script` runs arbitrary Python with full bpy (set `bfa_result` to return data); `mode=ops` runs any bpy.ops op; `mode=journal` shows mutation history; `mode=asset` hits Poly Haven CC0: `action=search {query, type:hdri|texture|model}` then `action=import {id, type:hdri|model}` (imports GLB objects or sets the world HDRI — cached in assets/cache/).

## Recipe library (compose, don't hallucinate)

`~/Projects/blender-for-agents/recipes/*.py` — each recipe carries `ARGS` defaults,
`run(bpy, mu, args)` and `test(bpy)`; **canonized only after passing the harness in
Blender 5.2.2** (`blender -b --factory-startup -P tests/run_recipes.py`). Current:
14/14 canonized (bevel, array, boolean, text→mesh, mirror, screw-revolve, terrain
displace, curve pipe, glass, brushed metal, emissive neon, studio floor, 3-point
light, turntable camera). Law: read the matching recipe, adapt its args, send as
`bfa_code mode=script` — never invent Principled socket names. 5.x gotchas the
library already encodes: `Transmission Weight` (not Transmission), `Emission Color`
(RGBA), no `ScrewModifier.offset`, Vector has no `__iter__`.

## Loop that works

1. `bfa_scene overview` — see what exists (always start here in a live session).
2. Check recipes first; import CC0 assets (`bfa_code mode=asset`) for HDRIs/models.
3. `bfa_build` create primitives/camera/light — rotation is in DEGREES.
4. `bfa_build camera_frame` — one call points the camera at a target.
5. `bfa_render` — LOOK at the image, then iterate. Renders are cheap (~2-6s).
6. `bfa_io export` gltf for delivery.

## Laws

- Scene starts EMPTY (no default cube). A fresh scene has no camera — create one or renders fail with "no camera in scene".
- Light before render: `create` type=light, energy ~1000-3000, or renders come out black.
- Unknown bpy op? `bfa_code mode=ops` runs any of the 2,498 operators without new plumbing.
- Errors come back structured with a trace — never retry identical calls; fix the args.
- Kernel/server source: `~/Projects/blender-for-agents/` (kernel/, mcp/, tests/ 14+8 passing).
