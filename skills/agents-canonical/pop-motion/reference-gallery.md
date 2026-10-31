# Pop Motion — Reference Gallery

A composable CSS animation system. Single source of truth. GPU-accelerated, stagger-native, accessible.

---

## 1. Motion Tokens

```css
:root {
  --motion-ease-out: cubic-bezier(0.22, 1, 0.36, 1);    /* slam — fast deceleration */
  --motion-ease-spring: cubic-bezier(0.34, 1.24, 0.64, 1); /* bounce — overshoot settle */
  --motion-duration-sm: 0.38s;
  --motion-duration-md: 0.48s;
  --motion-duration-lg: 0.62s;
  --motion-stagger: 0.05s;
}
```

## 2. GPU Hinting (Core Layer)

Only hint GPU during active motion. Never leak `will-change` permanently.

```css
/* Activate hints */
.pop-animating .animate-surface,
.pop-boot-active .animate-surface {
  backface-visibility: hidden;
  will-change: transform, opacity;
}

/* Release when done */
:not(.pop-animating):not(.pop-boot-active) .animate-surface {
  will-change: auto;
}
```

## 3. Keyframes — Boot Sequence

### App Shell Slam (full viewport)
```css
@keyframes appSlamIn {
  0%   { opacity: 0; transform: scale3d(1.04, 1.04, 1) translate3d(0, -12px, 0); }
  55%  { opacity: 1; transform: scale3d(0.99, 0.99, 1) translate3d(0, 2px, 0); }
  100% { opacity: 1; transform: scale3d(1, 1, 1) translate3d(0, 0, 0); }
}
```

### Header Stamp (top bar)
```css
@keyframes headerStamp {
  0%   { opacity: 0; transform: translate3d(0, -28px, 0) rotate(-2deg); }
  65%  { opacity: 1; transform: translate3d(0, 3px, 0) rotate(0.5deg); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) rotate(0deg); }
}
```

### Title Pop (brand name)
```css
@keyframes titlePop {
  0%   { opacity: 0; transform: scale3d(1.08, 1.08, 1) rotate(-4deg); }
  65%  { opacity: 1; transform: scale3d(0.98, 0.98, 1) rotate(1deg); }
  100% { opacity: 1; transform: scale3d(1, 1, 1) rotate(0deg); }
}
```

## 4. Keyframes — Panel Entrances

### 3-Panel Layout (left / center / right)
```css
@keyframes panelLeft {
  0%   { opacity: 0; transform: translate3d(-32px, 0, 0) rotate(-2deg) scale3d(1.02, 1.02, 1); }
  60%  { opacity: 1; transform: translate3d(4px, 0, 0) rotate(0.5deg) scale3d(1, 1, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) rotate(0deg) scale3d(1, 1, 1); }
}

@keyframes panelCenter {
  0%   { opacity: 0; transform: translate3d(0, 24px, 0) scale3d(0.94, 0.94, 1); }
  60%  { opacity: 1; transform: translate3d(0, -3px, 0) scale3d(1.01, 1.01, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) scale3d(1, 1, 1); }
}

@keyframes panelRight {
  0%   { opacity: 0; transform: translate3d(32px, 0, 0) rotate(2deg) scale3d(1.02, 1.02, 1); }
  60%  { opacity: 1; transform: translate3d(-4px, 0, 0) rotate(-0.5deg) scale3d(1, 1, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) rotate(0deg) scale3d(1, 1, 1); }
}
```

### Comic Panel Slam (cards, glass surfaces)
```css
@keyframes comicPanelSlam {
  0%   { opacity: 0; transform: scale3d(1.06, 1.06, 1) rotate(-3deg) translate3d(0, -16px, 0); }
  65%  { opacity: 1; transform: scale3d(0.98, 0.98, 1) rotate(1deg) translate3d(0, 2px, 0); }
  100% { opacity: 1; transform: scale3d(1, 1, 1) rotate(0deg) translate3d(0, 0, 0); }
}
```

### Main Content Slam
```css
@keyframes mainSlam {
  0%   { opacity: 0; transform: translate3d(0, 24px, 0) scale3d(0.94, 0.94, 1); }
  60%  { opacity: 1; transform: translate3d(0, -3px, 0) scale3d(1.01, 1.01, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) scale3d(1, 1, 1); }
}
```

### Footer Slam
```css
@keyframes footerSlam {
  0%   { opacity: 0; transform: translate3d(0, 16px, 0) skewX(-2deg); }
  65%  { opacity: 1; transform: translate3d(0, 2px, 0) skewX(0.5deg); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) skewX(0deg); }
}
```

## 5. Keyframes — Micro-Interactions

### Button Wiggle (hover)
```css
@keyframes btnWiggle {
  0%, 100% { transform: translate3d(-1px, -1px, 0); }
  50%      { transform: translate3d(-2px, 0, 0) rotate(-1deg); }
}
```

### Primary Button Pulse (infinite idle)
```css
@keyframes primaryPulse {
  0%, 100% { transform: scale3d(1, 1, 1); }
  50%      { transform: scale3d(1.02, 1.02, 1); }
}
```

### Accent Button Pulse (opacity-based)
```css
@keyframes accentPulse {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.88; }
}
```

### Logo Wiggle (idle personality)
```css
@keyframes logoWiggle {
  0%, 88%, 100% { transform: rotate(0deg) scale3d(1, 1, 1); }
  92%           { transform: rotate(-1.5deg) scale3d(1.02, 1.02, 1); }
  96%           { transform: rotate(1.5deg) scale3d(1.02, 1.02, 1); }
}
```

### Nav Tab Stamp (active state)
```css
@keyframes navStamp {
  0%   { transform: scale3d(1.08, 1.08, 1) rotate(-2deg); }
  65%  { transform: scale3d(0.98, 0.98, 1) rotate(1deg); }
  100% { transform: scale3d(1, 1, 1) rotate(0deg); }
}
```

### Tree Row Hover (subtle nudge)
```css
@keyframes treeFlick {
  0%   { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(3px, 0, 0); }
}
```

### Toast Slam (notification slide-in)
```css
@keyframes toastSlam {
  0%   { opacity: 0; transform: translate3d(80px, 0, 0) rotate(3deg) scale3d(0.92, 0.92, 1); }
  65%  { opacity: 1; transform: translate3d(-4px, 0, 0) rotate(-1deg) scale3d(1.02, 1.02, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) rotate(0deg) scale3d(1, 1, 1); }
}
```

### Rerender Flash
```css
@keyframes rerenderFlash {
  0%   { opacity: 0.7; }
  100% { opacity: 1; }
}
```

### Rescan Spinner
```css
@keyframes rescanSpin {
  to { transform: rotate(360deg); }
}
```

### Disk Critical Alarm (breathing opacity)
```css
@keyframes diskCriticalAlarm {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.88; }
}
```

## 6. Keyframes — Chat & Messaging

### Message In (assistant, from left)
```css
@keyframes msgIn {
  0%   { opacity: 0; transform: translate3d(-24px, 0, 0) rotate(-3deg) scale3d(0.94, 0.94, 1); }
  65%  { opacity: 1; transform: translate3d(3px, 0, 0) rotate(1deg) scale3d(1.01, 1.01, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) rotate(0deg) scale3d(1, 1, 1); }
}
```

### Message In (user, from right)
```css
@keyframes msgInRight {
  0%   { opacity: 0; transform: translate3d(24px, 0, 0) rotate(3deg) scale3d(0.94, 0.94, 1); }
  65%  { opacity: 1; transform: translate3d(-3px, 0, 0) rotate(-1deg) scale3d(1.01, 1.01, 1); }
  100% { opacity: 1; transform: translate3d(0, 0, 0) rotate(0deg) scale3d(1, 1, 1); }
}
```

### Typing Dots
```css
@keyframes dotBounce {
  0%, 80%, 100% { transform: translate3d(0, 0, 0); }
  40%           { transform: translate3d(0, -5px, 0) scale3d(1.15, 1.15, 1); }
}
```

## 7. Keyframes — Comic Accent Layer

### Speed Lines (burst overlay)
```css
@keyframes comicSpeedLines {
  0%   { opacity: 0; transform: scale3d(0.92, 0.92, 1); }
  35%  { opacity: 0.45; transform: scale3d(1.04, 1.04, 1); }
  100% { opacity: 0; transform: scale3d(1.08, 1.08, 1); }
}
```

### Page Settle (impact aftermath)
```css
@keyframes comicPageSettle {
  0%   { transform: translate3d(0, -2px, 0); }
  40%  { transform: translate3d(0, 1px, 0); }
  100% { transform: translate3d(0, 0, 0); }
}
```

### Impact Flash
```css
@keyframes comicImpactFlash {
  0%   { opacity: 0; }
  30%  { opacity: 0.3; }
  100% { opacity: 0; }
}
```

## 8. Keyframes — Subtle Variant (Vinny Theme)

Softer motion for professional/clean surfaces. Same structure, gentler numbers.

```css
@keyframes vinnyFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes vinnySlideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes vinnyCardIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes vinnyMsgIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes vinnyToastIn {
  from { opacity: 0; transform: translateX(12px); }
  to   { opacity: 1; transform: translateX(0); }
}
```

## 9. Stagger Patterns

Every surface uses CSS `animation-delay` cascades computed from `--motion-stagger` (0.05s).

### Stat Grid (5 items)
```css
.stat:nth-child(1) { animation-delay: 0.34s; }
.stat:nth-child(2) { animation-delay: 0.40s; }
.stat:nth-child(3) { animation-delay: 0.46s; }
.stat:nth-child(4) { animation-delay: 0.52s; }
.stat:nth-child(5) { animation-delay: 0.58s; }
```

### Rec Cards (6 items)
```css
.rec:nth-child(1) { animation-delay: 0.56s; }
.rec:nth-child(2) { animation-delay: 0.62s; }
.rec:nth-child(3) { animation-delay: 0.68s; }
.rec:nth-child(4) { animation-delay: 0.74s; }
.rec:nth-child(5) { animation-delay: 0.80s; }
.rec:nth-child(6) { animation-delay: 0.86s; }
```

### Alert Boxes (5 items)
```css
.alert-box:nth-child(1) { animation-delay: 0.40s; }
.alert-box:nth-child(2) { animation-delay: 0.46s; }
.alert-box:nth-child(3) { animation-delay: 0.52s; }
.alert-box:nth-child(4) { animation-delay: 0.58s; }
.alert-box:nth-child(5) { animation-delay: 0.64s; }
```

### Nav Tabs (5 items)
```css
.tab:nth-child(1) { animation-delay: 0.18s; }
.tab:nth-child(2) { animation-delay: 0.23s; }
.tab:nth-child(3) { animation-delay: 0.28s; }
.tab:nth-child(4) { animation-delay: 0.33s; }
.tab:nth-child(5) { animation-delay: 0.38s; }
```

### Card Grid (glass panels)
```css
.glass:nth-child(1) { animation-delay: 0.36s; }
.glass:nth-child(2) { animation-delay: 0.42s; }
.glass:nth-child(3) { animation-delay: 0.48s; }
```

### Sidebar Items
```css
.del-item:nth-child(1) { animation-delay: 0.32s; }
.del-item:nth-child(2) { animation-delay: 0.38s; }
.del-item:nth-child(3) { animation-delay: 0.44s; }
.del-item:nth-child(4) { animation-delay: 0.50s; }
.del-item:nth-child(5) { animation-delay: 0.56s; }
```

## 10. Hover Patterns

```css
/* Card/Rec hover — subtle lift */
.rec:hover {
  animation: recHoverPop 0.28s var(--motion-ease-spring) forwards;
}
@keyframes recHoverPop {
  0%   { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(0, -3px, 0) scale3d(1.01, 1.01, 1); }
}

/* Button hover — directional wiggle */
.btn:hover {
  animation: btnWiggle 0.28s var(--motion-ease-spring);
}

/* Row hover — lateral nudge */
.tree-item:hover {
  animation: treeFlick 0.24s var(--motion-ease-spring);
}
```

## 11. Entrance Orchestration (JS)

```js
/*
  Boot sequence: add .pop-loaded class, then:
  1. Mark body as .pop-animating + .pop-boot-active (GPU hints active)
  2. CSS keyframes fire on all surfaces (staggered via animation-delay)
  3. Comic accent fires (speed lines + page settle)
  4. After bootMs (880ms): remove .pop-animating + .pop-boot-active (GPU hints released)

  Variant system: each surface gets a random variant from [stamp, slam, deal, snap, wham]
  Debounce: 3.2s between replays
  Impact cooldown: 1.4s between comic accents
  prefers-reduced-motion: skip all animations, just set .pop-loaded
*/
```

### Core timing constants
| Constant | Value | Purpose |
|----------|-------|---------|
| bootMs | 880ms | Full entrance window |
| accentDelayMs | 540ms | When comic accents start |
| debounceMs | 3200ms | Minimum time between replays |
| impactCooldownMs | 1400ms | Minimum time between comic impacts |
| accentStaggerMs | 45ms | Delay between accent items |
| accentCleanupMs | 700ms | How long accents stay before cleanup |

## 12. Background Visuals

### Living Background (subtle hue rotation)
```css
@keyframes bgShift {
  0%   { filter: hue-rotate(0deg) saturate(1.05); }
  50%  { filter: hue-rotate(10deg) saturate(1.12); }
  100% { filter: hue-rotate(-6deg) saturate(1.08); }
}
.pop-bg {
  animation: bgShift 16s ease-in-out infinite alternate;
}
```

### Halftone March (texture scrolling)
```css
@keyframes halftoneMarch {
  to { background-position: 14px 14px; }
}
.pop-halftone-bg {
  animation: halftoneMarch 10s linear infinite;
}
```

## 13. Full Accessibility Compliance

```css
@media (prefers-reduced-motion: reduce) {
  /* Disable all infinite/idle animations */
  .pop-bg,
  .pop-halftone-bg,
  .logo,
  .btn.primary,
  .btn.accent,
  .alert-box.critical,
  .disk-viz.critical,
  .comic-star,
  .comic-flash,
  #rescanBtn:disabled {
    animation: none !important;
  }
  .comic-speed-lines {
    display: none;
  }

  /* Freeze all entrance animations at final frame */
  .pop-loaded .app,
  .pop-loaded .header,
  .pop-loaded .main,
  .pop-loaded .chat,
  .pop-loaded .rpanel,
  .pop-loaded .canvas > .glass,
  .pop-loaded .rec,
  .pop-loaded .del-item,
  .pop-loaded .rpanel .mini,
  .pop-loaded .mx-shell,
  .pop-loaded .topbar,
  .pop-loaded main,
  .pop-loaded footer,
  .pop-loaded #statsGrid .stat,
  .pop-loaded #panel-dashboard .card,
  .pop-loaded .tabs .tab,
  .pop-loaded .brand h1 {
    opacity: 1 !important;
    transform: none !important;
    animation: none !important;
  }
}
```

## 14. Design Principles

1. **Transform + opacity only.** Never animate width, height, top, left, or color. GPU can composite transform/opacity at zero cost; layout-triggering properties force repaint.

2. **3D transforms even in 2D.** Use `scale3d()` / `translate3d()` / `rotate3d()` to force GPU compositing. This is a free optimization with no visual difference.

3. **Overshoot then settle.** Every entrance goes past the target (scale 1.04, rotate 2deg) then snaps back. This creates the "slam" feel — the bounce is in the keyframe, not the easing curve.

4. **Stagger everything.** Nothing enters at the same time. 50-60ms gaps create visual rhythm without feeling slow.

5. **GPU hints are temporary.** Set `will-change` only during `pop-animating` / `pop-boot-active`. Remove it when done. Permanent `will-change` eats GPU memory.

6. **Infinite animations are idle-only.** Only backgrounds, logos, and pulse buttons animate perpetually. All entrance keyframes fire once with `forwards` fill mode.

7. **Two themes, one system.** Pop (comic, aggressive, overshoot-heavy) and Vinny (clean, subtle, small transforms). Both use the same token set — just different keyframe amplitude.

8. **Accessibility is not optional.** `prefers-reduced-motion: reduce` strips all animations to instant renders. JS must respect it before adding CSS classes.
