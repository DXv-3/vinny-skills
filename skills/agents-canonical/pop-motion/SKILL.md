---
name: pop-motion
description: "Enforce VinnyOS Pop Motion animation style on any project. Use when building or reviewing UI that needs GPU-accelerated entrance sequences, staggered micro-interactions, comic/slam personality animations, or professional subtle motion. Applies motion tokens, keyframes, hover patterns, and accessibility handling from a battle-tested CSS animation system. Triggers: add animations, animate this UI, make it pop, add motion, entrance animation, page load animation, micro-interactions, make it feel alive."
version: 1.0.0
---

# Pop Motion

A composable, GPU-accelerated CSS animation system with two themes: **Pop** (comic/slam, aggressive overshoot) and **Vinny** (clean/subtle, professional).

This skill injects the full Pop Motion reference into context and forces adherence to its patterns. No generic CSS transitions. No AI slop animations. Every surface gets a purpose-built keyframe with stagger, GPU hinting, and accessibility fallback.

## Load the Reference

Before writing any code, read the reference gallery:
```
references/reference-gallery.md
```

The reference contains every token, keyframe, stagger pattern, hover state, background visual, and orchestration rule the system uses.

## When to Use

Invoke this skill when:
- Building a new UI surface that needs entrance animations
- Adding hover/micro-interaction personality to an existing interface
- Building a dashboard, admin panel, chat interface, or card grid
- Replacing generic `transition: all 0.3s ease` with real motion design
- Reviewing UI code for animation quality (audit mode)
- Any task where the user says "animate", "motion", "pop", "make it alive", "entrance", "page load"

## Mandatory Rules

### 1. Transform + opacity only
Never animate layout-triggering properties (width, height, top, left, margin, padding, border-width). Only:
- `transform` (translate3d, scale3d, rotate, skewX)
- `opacity`

If you must animate color, use `filter` or overlay techniques. Layout changes must be instant.

### 2. 3D transforms everywhere
Use `translate3d()`, `scale3d()` instead of `translate()`, `scale()`. This forces GPU compositing at zero cost.

### 3. Overshoot then settle
Every entrance keyframe follows a 3-keyframe arc:
- **0%**: Off-screen / scaled up / rotated, opacity 0
- **~60%**: Past the target (slightly scaled down, rotated opposite, offset reversed)
- **100%**: At rest (identity transform, opacity 1)

The bounce lives in the keyframe, not in the easing curve.

### 4. Stagger everything
Every list, grid, or collection of surfaces must use `animation-delay` cascades. Base stagger increment: `0.05s`. Compute delays so the last item enters within the boot window.

### 5. GPU hints are temporary
```css
.pop-animating .surface { will-change: transform, opacity; }
:not(.pop-animating) .surface { will-change: auto; }
```
Never leave `will-change` permanently. It only lives while `pop-animating` or `pop-boot-active` class is present.

### 6. Two themes, one system
- **Pop**: Aggressive overshoot (scale 1.04-1.08, translate -12 to -28px, rotate 2-4deg), comic timing
- **Vinny**: Subtle (scale 1.02 max, translate 6-12px, rotate 0-1deg, gentle fade)

Choose based on context. Pop for creative tools, dashboards, playful apps. Vinny for professional tools, admin panels, data-heavy surfaces.

### 7. Accessibility lock
Every file with animations must include `@media (prefers-reduced-motion: reduce)`. All infinite/idle animations must be disabled. All entrance animations must be frozen at their final frame (opacity: 1, transform: none).

### 8. Boot coordination via class
Page load animation is triggered by adding `.loaded` class to the root element. CSS waits for this class. JS adds it after mount. The boot window is 880ms. After boot, remove `.pop-animating` to release GPU hints.

### 9. No CSS-only approach for full sequences
For complex entrance sequences with coordinated timing, use JS to add/remove state classes. CSS handles the visual keyframes and stagger delays. JS handles the lifecycle (boot start, boot end, replay debouncing).

### 10. No generic easings
Never use `ease`, `ease-in-out`, or `linear` for entrance animations. Always use the system tokens:
```css
animation-timing-function: var(--motion-ease-out);     /* slam */
animation-timing-function: var(--motion-ease-spring);   /* bounce */
```

## File Structure Pattern

When adding motion to a project, create this structure:

```
project/
├── motion/
│   ├── tokens.css          # --motion-ease-out, --motion-ease-spring, durations, stagger
│   ├── core.css            # GPU hints, will-change management, reduced-motion base
│   ├── keyframes.css       # All @keyframes (from reference gallery, pick what you need)
│   ├── surfaces.css        # Surface → keyframe mappings with stagger delays
│   └── entrance.js         # Boot coordinator (add/remove .loaded, .pop-animating)
```

Or inline into existing CSS — but always comment the sections clearly:
```
/* ── motion tokens ── */
/* ── GPU hints ── */
/* ── keyframes ── */
/* ── surface mappings + stagger ── */
/* ── hover patterns ── */
/* ── reduced motion ── */
```

## Quick Start

1. Copy the motion tokens from the reference into your CSS root.
2. Copy the GPU hinting rules.
3. Pick the keyframes you need from the reference (minimum: one shell, one panel, one card, one message).
4. Map surfaces to keyframes with stagger delays.
5. Add the hover patterns.
6. Add the `prefers-reduced-motion` block.
7. Wire `entrance.js` or inline the boot class toggling.

## Audit Mode

When asked to audit existing animations, check against each mandatory rule. Report violations with exact line references. Rank severity:
- **BLOCKER**: Animates layout property, no reduced-motion fallback, permanent will-change
- **HIGH**: Uses generic easing, no stagger, missing GPU compositing
- **MEDIUM**: Inconsistent timing, wrong theme for context, orphaned keyframes
- **LOW**: Token naming divergence, missing comments

## References

- Full keyframe gallery: `references/reference-gallery.md`
- Source: `~/Projects/VinnyOS/surfaces/disk-hub/` (pop-animations.css, vinny-motion.css, pop-motion-pro.css, comic-live.css, pop-entrance.js)
- Source: `~/Projects/MATRIX/matrix/web/static/` (pop-animations.css, vinny-motion.css, pop-motion-pro.css, comic-live.css)
