---
name: walkable-architecture-storytelling
description: "Turn a portfolio, brand story, or long-form narrative into a continuous walk through architectural space — scroll drives a camera along one path from entrance to finale, and each room carries one story beat. Use when the user asks for a walkable site, room-to-room journey, architectural fly-through, house/building portfolio, garden-to-courtyard story, seasons-of-a-place narrative, or a portfolio you walk through instead of scroll past."
---

# Walkable Architecture Storytelling

Build a place, not a page. The visitor scrolls to walk; rooms deliver meaning;
one continuous camera path stitches it into a single journey.

Reference class: continuous camera path through entrance garden → rooms →
courtyard → water. Learn the pattern from sites like that; **never republish
their artwork, geometry, textures, or copy** — license terms on those repos
explicitly require it. This skill builds original places only.

## The contract

Write these before building.

### Goal

> Turn the supplied story into one walkable space with 5–8 rooms, one path, one
> finale. A first-time visitor should finish the walk able to retell the story
> in three sentences.

### House rules

- One continuous path. The camera never cuts; it eases.
- One room, one idea. A room that says two things is two rooms.
- Original geometry, original copy, original palette. Reference mechanics, not artifacts.
- Motion carries transitions; copy explains meaning (house standard: additive
  motion, staggered fade-rise, reduced-motion honored, no CDN dependencies).

## Mode decision — pick one, don't mix

1. **Three.js world** — real 3D (local three r149+ UMD, never CDN). Full
   camera freedom, lighting, seasons. Costs: draw-call budget, mobile GPU.
2. **CSS/DOM corridor** — perspective-transformed planes, zero dependencies,
   opens from file://. Cheaper, robust on old phones, less spatial freedom.

Choose 2 whenever the story fits boxes and thresholds; choose 1 when light,
water, or atmosphere is the story.

## The five mechanics

### 1 · Chapter path (the spine)
A waypoints array is the whole skeleton:
`[{at: 0.0, pos:[x,y,z], look:[x,y,z], chapter: "entrance"}, …]`
Scroll position maps to path-time `t` (eased between waypoints — never linear;
use easeInOut per segment). The active chapter is whichever segment contains
`t`. Everything else (copy state, lights, audio) derives from `t` — one source
of truth, no per-element scroll listeners.

### 2 · Rooms as beats
Each room fires exactly one threshold event: crossing the doorframe reveals
that room's copy (staggered fade-rise), leaving it fades it. Thresholds live
in the same waypoints array (`at:` boundaries). Copy is positioned in the
layout *outside* the path math — never pinned to world coordinates, so it
survives viewport changes.

### 3 · Atmosphere before detail
Fog + ground plane + a bounded palette (one wood, one paper, one accent)
reads as architecture with almost no geometry. Spend the budget on the two
hero rooms; corridors can be fog and floor.

### 4 · Seasonal states
One world, N appearances: a state object (leaf color, particle type, light
temperature) that every material reads. Switching season is one object swap —
no reload, no duplicate scene. Ship one season by default; gate the rest.

### 5 · The budget
- Instanced meshes for every repeated element (posts, lanterns, plants).
- Baked canvas textures over downloaded assets (paint tatami/cedar/paper grain
  on a 2D canvas at boot).
- Clamp devicePixelRatio to 2; cap draw calls (~40 mobile / ~120 desktop).
- `prefers-reduced-motion`: kill the scrub, chapter-jump navigation instead
  (dots jump the camera to each waypoint with a single ease).

## Verify (the minting contract)

1. Demo runs from a single local file (or `python3 -m http.server` for three.js).
2. Two viewports: 390×844 (iPhone) and 1440×900. Walk must complete in both.
3. Reduced-motion pass: nothing scrubs; chapter jumps work.
4. Fallback: no WebGL / JS disabled → the copy stack still reads top-to-bottom.
5. `grep` the demo for external URLs — there must be none.

## Pairs with

`mengto-scroll-world-storytelling` (the story-beat layer),
`mengto-cinematic-gsap-lenis-motion-system` (smooth scrub),
`mengto-atmosphere-background` (fog/palette), `mengto-3d-sky-background`.
