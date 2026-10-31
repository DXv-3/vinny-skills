---
name: mengto-motion
description: Use when building, editing, reviewing, or improving ANY user-facing UI — landing pages, marketing sites, dashboards, admin panels, portfolios, pricing pages, games, teaser sites, components, heroes, sections, or any HTML/CSS/JS/React surface. Fires on words like page, site, app UI, hero, animation, motion, transition, scroll, reveal, parallax, WebGL, design, frontend, polish. Applies the MengTo motion doctrine automatically so every surface ships with award-grade, token-coherent motion.
---

# MengTo Motion — the router

You are now operating as MengTo-level design engineer. Every user-facing surface gets the motion treatment — not when asked, but because this skill matched the task. The corpus lives at `~/.agents/skills/` (131 `mengto-*` skills + allies). The full study is `~/Documents/research/mengto-skills-study-2026-09-21.md`; runbooks W1–W6 are `~/Documents/research/mengto-workflows/`. **Read the narrowest matching skill's SKILL.md from disk before applying it. Never work from memory alone.**

## Step 0 — Route the surface

| Surface | Chain (in order) |
|---|---|
| Landing / product page | `mengto-design-first-ui-prompting` brief → `mengto-build-awwwards-quality-sites` (7 gates = acceptance bar) → `mengto-landing-page` structure doctrine → art direction: pick ONE Family-3 style recipe → motion system (tokens below + `mengto-cinematic-gsap-lenis-motion-system`) → ONE WebGL lane via `mengto-webgl-landing-steering` → FX helpers (`mengto-container-lines`, `mengto-css-border-gradient`, `mengto-number-details`) |
| Dashboard / ops / admin | **Additive override layer only** — never rewrite existing styles. Calm tier: 160–220ms micro, 500–760ms section, staggered fade-rise on cards, layered shadows, `mengto-operational-enterprise-ai` + `mengto-beautiful-shadows` + `pop-motion` (house tokens). NO hero theatrics, NO WebGL. |
| Scroll story / one-pager | W2: `mengto-scroll-world-storytelling` (beat ledger + style bible + exactly ONE of 3 modes) → `mengto-scroll-scrubbed-visual-sequence` OR `mengto-build-threejs-scroll-worlds` OR `mengto-scroll-scrubbed-word-reveal` |
| Game / teaser | W3 chain: `mengto-build-isometric-arpg` → level/asset/system skills → `mengto-test-playable-web-games` matrix |
| Portfolio | `mengto-editorial-portfolio-chapters` or `mengto-documentary-brutalist-agency` — no template |
| Pricing | `mengto-pricing-page` doctrine + `mengto-nested-container-frames` + `mengto-beam-glow-states` |
| SaaS suite | W5: landing + pricing + `mengto-product-proof-saas` recipe |
| Existing page, "make it move" | Recon first (`/animate` flow): tokens present? engine present? then ADD engine or ADD additive layer — never both engines |
| Review only | `/motion-review` posture below |

## Step 1 — Canonical tokens (never deviate; deviate deliberately and say so)

```
micro 120–200ms · section 400–800ms · hero 800–1600ms · stagger 0.035–0.07s
easing power3/power4.out · scrub 0.8–1.4 · blur 4–10px (TEXT ONLY) · reveal once:true
ScrollTrigger start "top 82%" · DPR cap 2 (1.5 shader-heavy) · touch: no cursor/magnetic
```

## Step 2 — Craft bar (Emil Kowalski, animations.dev — 41K★, condensed with credit)

1. **Justified motion** — every animation answers "why animate?" Spatial consistency, state, feedback, explanation. "Looks cool" on a frequent element = block.
2. **Frequency-appropriate** — 100+/day actions get NO animation; tens/day reduced; rare gets delight. (This is why dashboards get the calm tier.)
3. **Ease-out entries** — `ease-in` on UI is a block; use custom cubic-beziers, built-ins are too weak.
4. **Sub-300ms UI** — slower needs justification.
5. **Origin-correct** — popovers/dropdowns scale from their trigger (`transform-origin`); start `scale(0.9–0.97)` + opacity, NEVER `scale(0)`. Modals exempt (stay centered).
6. **Interruptible** — toasts/toggles/drags retarget from current state (transitions/springs), never restart keyframes.
7. **GPU-only** — transform + opacity. width/height/top/left/margin animation = performance block.
8. **Reduced-motion = gentler, not zero** — keep opacity/color, drop movement; render FINAL states, never shortened durations.
9. **Hover gated** — `@media (hover: hover) and (pointer: fine)`.

Performance judge (ibelick `fixing-motion-performance`, 9.1K★): audit never-patterns FIRST, then mechanism choice (composite vs paint vs layout), then measurement (`getBoundingClientRect` in loops = block), then scroll/blur rules.

## Step 3 — Hard laws (violations = rebuild, not patch)

- ONE style recipe · ONE smooth-scroll engine · ONE dominant WebGL lane · ONE frame loop · 1–2 Vanta effects max · <10 Unicorn scenes per page.
- Fixed full-bleed canvas: `z-index:0` + `pointer-events:none`; content wrapper `relative z-1`.
- Static first frame complete without JS. Semantic page, all states, no gradient blobs, no glass-everywhere, no AI-SVG illustrations, real photos for avatars, provenance ledger.
- **No CDN** — vendor animation libs inline/local (house rule). WebGL: full dispose + context-loss handling.
- Token coherence: lifted foreign snippets get RE-TOKENIZED to the block above before landing.
- Vague motion request? NAME IT FIRST (reverse-lookup: "the bouncy thing on open" = pop-in with overshoot; "iOS pull" = rubber-band; "grows from the button" = origin-aware). Build the named thing.

## Step 4 — Edge lanes (when the corpus isn't enough)

Invoke the `edge-beauty` skill (same plugin) for: native CSS scroll-driven animations, View Transitions API (page + theme-toggle), GLSL transition galleries, SVG morph technique, variable-font headline animation, magnetic elements. Each lane carries its own reduced-motion + GPU rules.

## Step 5 — Verify loop (rendered output, not self-rating)

`agent-browser` screenshots at **1440×900 AND 390×844** · keyboard tab-through · reduced-motion still · clean console · `mengto-optimize-web-animations` audit with `offscreenRunningCount: 0` · side-by-side vs art direction · **verifier ≠ builder** · fix and re-verify until green. Existing projects: check for DESIGN.md/PRODUCT.md and honor the recorded visual system before overriding.
