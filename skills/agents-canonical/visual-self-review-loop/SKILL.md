---
name: visual-self-review-loop
description: "Run the render → screenshot → critique → fix loop while building visual work: render after the first vertical slice, again after every chunk, judge the pixels against a craft checklist, and fix before building on. Use when authoring any HTML/SVG/canvas page, map, poster, dashboard, or game UI — whenever 'authored' must become 'built' and one screenshot at the end is too late. Taste lives in frontend-design; final gates in mengto-iterate-until-verified — this is the in-flight loop between them."
---

# Visual Self-Review Loop

Visual verification is part of **done**. An artifact that has never rendered is not built — it is authored. The loop: build one chunk → render → screenshot → judge the pixels against the checklist → fix → only then build the next chunk.

A visual bug caught one batch after it is written is a one-line diff; four bugs caught at the end are archaeology in one undifferentiated pile. The estate park map (ESTATE-PARK-MAP-2026-09-27.html, 1,129 lines / 80,271 bytes) was authored end-to-end before the first browser render — grain darkening, two label collisions, a z-order bug, and a route fall-through all shipped together because nothing was looked at until everything was finished.

## When to Use

- Building any visual artifact: HTML/SVG pages, posters, maps, dashboards, canvases, game UI, landing pages
- Before writing chunk N+1 of visual work — the screenshot gate runs between chunks
- Adding a full-canvas overlay, filter, tint, or theme change (highest blast radius in the file)
- Hand-placing labels, tokens, or repeated geometry at any scale
- Shipping a feature whose failure mode is silent (guarded boot, server-fed UI, swallowed errors)
- Any task where the user says "render it", "screenshot", "check the pixels", "does it look right", "is it done"
- **Skip** when the ask is taste or art direction — that is `frontend-design`; when it is the final acceptance pass — that is `mengto-iterate-until-verified`; when it is motion mechanics — that is `pop-motion` (CSS), `emil-design-eng` (interaction motion), or `mengto-cinematic-gsap-lenis-motion-system` (GSAP). This skill judges rendered pixels against craft rules; it does not choose the aesthetic.

## The Loop

### 1. Render-gate at the first vertical slice
NEVER author the whole artifact before the first render. The first browser render happens after the first vertical slice — one land + one attraction + its panel on a map; one hero + one section on a page. **CRITICAL: "authored" and "built" are not the same milestone — a page that has never rendered is not built.**

### 2. Screenshot after every chunk
Screenshot at final size AND at the project's declared minimum supported viewport — a per-project design decision fixed at authoring time by the Density gate (320px is the usual floor for fluid web layouts; fixed-canvas artifacts like posters and print maps skip the second shot). Local builds are captured with **local headless Chrome** — it executes on this Mac, so it sees `file://` and this Mac's loopback (executed against the real park map while writing this skill):

```bash
timeout 45 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-sandbox --hide-scrollbars --no-first-run --user-data-dir=/tmp/vsrl-shot --virtual-time-budget=4000 \
  --window-size=1280,1000 --screenshot=/tmp/shot.png "file:///path/to/build.html"
```

(The `infsh` browser executes remotely — its `file://` and `127.0.0.1` are not this machine's. Reserve the qualified `infsh/agent-browser` for public-URL checks, and always end those sessions with `--function close`.) Stitched full-page shots: `mengto-stitched-full-page-capture`. Judge pixels before building the next chunk — never one screenshot at the end.

### 3. Critique against the checklist
Run the craft checklist below against the screenshot. Every item is pass/fail on pixels, not on source. Reading source is not a check: emoji glyph rendering, label overlap, and filter darkness are invisible in source and obvious in a screenshot.

### 4. Fix before proceeding
A failed checklist item blocks the next chunk. Fix → re-render → re-screenshot → re-judge.

### 5. Run the render gates
Each gate in the table below is tied to the moment its bug class becomes writable — not to an end-of-day hardening pass.

### 6. Done = rendered + green
A chunk is done only when: it rendered, its screenshot passes the checklist, its render gates passed, and the happy path was clicked through live once (local: `browser-use:control-browser` / `browser-use:web-gui-tester`; public URLs: qualified `infsh/agent-browser` — open → interact → **close**; or a real hand on a real browser).

## The Screenshot Gate — Craft Checklist

Judge every item on the screenshot, at final size and at the declared minimum viewport:

- [ ] Screenshot taken after every visual chunk — never one screenshot at the end
- [ ] No two labels, and no label against a marker or card edge, overlap at any viewport width or interaction state
- [ ] Every text reads against the exact background it crosses — halo/stroke (`paint-order`) or scrim per surface; contrast checked per background, not once globally
- [ ] Interactive marks paint above surrounding shapes; hover, focus, and selected layers sit topmost
- [ ] One filter, overlay, or state change never restyles or darkens unrelated areas of the page
- [ ] Icons come from one coherent drawn system — no emoji glyphs standing in for icons
- [ ] One glance gives one hierarchy: a single focal point, size/weight/color ranked to importance, secondary text quieter
- [ ] Every animation is justified; actions used 100+ times a day get no animation at all (source: emil-design-eng)
- [ ] UI motion finishes under 300ms, ease-out; entrances scale 0.9–0.97 from their own origin with a fade — never `scale(0)` (source: emil-design-eng)
- [ ] Only `transform` and `opacity` animate; scrolling and hovering cause no jank, layout shift, or full-page repaint (source: pop-motion)
- [ ] Toggle `prefers-reduced-motion` and watch the screen: decorative loops stop, remaining motion is gentler-not-zero, and no animation or transition in the file escapes the media query
- [ ] Hover effects fire only under `(hover:hover)` and `(pointer:fine)`; every `outline:none` is paid for with a visible `:focus-visible` ring
- [ ] Animations are interruptible: re-triggering mid-flight retargets from the current position instead of snapping back to the start
- [ ] Empty, loading, error, and off/disabled states are designed and rendered on screen — never blank rectangles
- [ ] Declared smallest supported viewport honored (Density gate): no horizontal overflow, no clipped or broken labels, all controls reachable
- [ ] Ambient/idle motion is slow and subtle — the page reads calm until touched; nothing loops fast enough to distract or drain battery
- [ ] State changes morph in place (View Transitions/FLIP) instead of vanish-then-appear
- [ ] Sound is off by default with a visible in-page toggle; motion and sound follow one consistent identity
- [ ] Every interactive mark has a hit target big enough to actually hit; small SVG tokens get an invisible enlarged hit circle
- [ ] Positions snap cleanly to the declared grid increment — nothing drifts 1–2px off its snap row or neighbor alignment

## Render Gates

Each gate exists because that exact bug shipped in the park-map build.

| Gate | When it runs | Check |
| --- | --- | --- |
| Render gate | First vertical slice, then every batch | First browser render happens here. NEVER author-then-render. |
| Overlay gate | Before any full-canvas overlay (grain, vignette, tint) | Add overlays LAST, after the content beneath is verified, and build each behind a body-class kill switch so on/off is one toggle — for SVG filter/overlay elements, toggle the referencing element (e.g. the `<rect filter="url(#grain)">`), not a class that doesn't exist. Check = render with the overlay on AND off, compare — not "does the page still load". One bad alpha touches every pixel. |
| Collision gate | After each district/section batch | Generate labels from a data table so one layout function owns offsets, OR write a ~30-line AABB-overlap lint over the extracted coordinates and run it after every batch, plus a final-size screenshot sweep. Hand-eyeballing 150+ magic numbers in source is not a check. |
| Layer gate | After every mid-file insertion | Keep an explicit bottom→top paint order (paper → water → lands → roads/rails → decorations → tokens → labels → overlays); verify the file top-to-bottom against it. In positional formats (SVG paints in document order), inserting mid-file silently repaints everything after — ask "where did I paste this?" |
| Click-through gate | When each route, string transform, or server-fed feature is written | Server and string-transform bugs are invisible in source and in screenshots — they surface only when the served artifact is used. Default branch after any prefix match = 404, never the homepage; run the feature's hostile row now (no token→403, evil Origin→403, `..`→404, oversized body→413); after any placeholder transform, count sentinel occurrences before/after and grep the served output — never one literal as both injection point and guard sentinel (an uncounted `str.replace` killed the park-map console with zero console errors); a feature that can die silently surfaces "X offline: \<reason\>" and its test proves the feature turns ON (bar activates, rows render), never merely that the page isn't broken. Proof = one live click-through (local: browser-use drivers; public: `infsh/agent-browser`, session closed). |
| Density gate | At authoring time when there is no camera | With no zoom to recover legibility, density and text size are structural: declare a minimum supported viewport in the build notes, require a screenshot at that width every pass, and give dense districts zoom or inset panels as a design step. Scale-only rendering converts every spacing error into unreadable text. |

## Worked Example — the build that skipped the loop

ESTATE-PARK-MAP-2026-09-27.html: one hand-written file (CSS + full SVG map + console JS + server integration) authored before any render. What shipped together: a grain filter (`feTurbulence` → `feColorMatrix`, full-canvas `<rect>`) that darkened the whole poster; two label collisions from ~30 hand-placed dot+label clusters with no computed bounding boxes; a z-order bug in an SVG with no declared layer order; a `/kept/..` route that failed its regex and fell through into the catch-all handler; and an uncounted `str.replace` that rewrote both the ops-console injection point AND its guard literal — the console died with zero console errors, found only in live testing. The end-of-build hardening review (HARDENING-REVIEW-2026-09-27.md — 13-issue table at :8-20, test matrix at :22-24) found 13 issues; every one was a gate in the table above, run one build too late.

The loop as it should have run — local capture via headless Chrome (every mechanism here executed against the real build while writing this skill):

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # local capture: executes on this Mac
shot() { timeout 45 "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars --no-first-run \
  --user-data-dir=/tmp/vsrl-shot --virtual-time-budget=4000 --window-size=1280,1000 \
  --screenshot="$2" "$1"; }

shot "file:///Users/vinnygilberti/Projects/ESTATE-PARK-MAP-2026-09-27.html" /tmp/park-chunk.png
# render gate: judge the pixels before writing chunk 2

# collision gate — labels emitted from the data table, or your ~30-line bbox-overlap lint, then re-shoot

# overlay gate — two shots (on AND off), compare. Rule: build overlays behind a kill-switch class so
# on/off is one toggle; for an existing SVG filter rect, execute the toggle through a JS-capable local
# driver (browser-use:control-browser) — this selector matches the park map's real markup at html:322:
#   document.querySelector('[filter="url(#grain)"]').style.display = 'none'   // '' restores

grep -c '__ESTATEOPS_TOKEN__' ESTATE-PARK-MAP-2026-09-27.html   # sentinel gate: source count (2, not 1)
curl -s --max-time 5 http://127.0.0.1:8125/ | grep -c '__ESTATEOPS_TOKEN__'  # served output: guard literal survived
curl -s --max-time 5 --path-as-is -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8125/kept/.."   # 404, never homepage

# click-through gate — local: browser-use:control-browser / browser-use:web-gui-tester;
# public URL only: infsh app run infsh/agent-browser (qualified name): open → interact → close
```

Each command costs seconds; each bug it catches cost a ship cycle.

## References

- `frontend-design` — aesthetic direction and the NEVER-generic-AI-slop rules; this skill judges pixels against craft, it does not pick the taste
- `ui-ux-pro-max` — UX/a11y rulebook + searchable design-system DB (`scripts/search.py --domain`); checklist items above enforce its rules at render time without restating them
- `pop-motion` — CSS motion mechanics the checklist enforces: transform+opacity only (pop-motion/SKILL.md:34-39) and the prefers-reduced-motion lock (:68-70)
- `~/.config/opencode/skills/emil-design-eng/SKILL.md` — source of the timing/entrance rules: under 300ms (:135), ease-out (:121), entrances from scale(0.95) never scale(0) (:44-47, :215), 100+ times/day gets no animation (:70-72)
- `mengto-cinematic-gsap-lenis-motion-system` — GSAP/ScrollTrigger/Lenis motion language and its QA checklist
- `mengto-iterate-until-verified` — the end-of-task acceptance gate (contract → gates → evidence → honest stop); its §5 requires rendered output at relevant sizes for visual work (:89). The 1440px + 390px browser-check belongs to the orchestrator's Lane B chain (skill-orchestrator/SKILL.md:128, INDEX.md:64-65), not to this loop — per-chunk shots use final size + the declared minimum. Also `mengto-audit-verify-explain-grade-5`
- `mengto-audit-ai-design-slop`, `mengto-no-ai-design-slop` — audit passes that consume the final screenshots this loop produces
- `mengto-web-technique-to-skill` — packaging standard followed here: mechanism over adjectives, real numbers, declared boundaries, browser verification
- Capture & click-through stack: local headless Chrome (`file://` + localhost), `browser-use:control-browser` / `browser-use:web-gui-tester` (local interaction), `infsh/agent-browser` (public URLs only — its remote sandbox cannot see this Mac's files or loopback; always `close`), `mengto-stitched-full-page-capture` (full-page stills)
- Source record: `~/Projects/ESTATE-PARK-MAP-2026-09-27.html` (1,129 lines / 80,271 bytes) and `~/Projects/estate-ops/HARDENING-REVIEW-2026-09-27.md` (13-issue table :8-20, test matrix :22-24) — the failure evidence behind every gate above
