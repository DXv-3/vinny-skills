---
name: website-builder
description: Use when Vinny asks to build a client website, landing page, portfolio, or corporate site from a brief, prices a site job ($1k-5k tiers or monthly maintenance), or runs the site pipeline (brief -> build -> film -> export -> deliver) with Flute and the motion spec.
---

# Website Builder (core-adapted)

Turn a client brief into a shipped, filmed, verified website. Adapted 2026-10-16 from
Vinny's attached "website-builder" skill (verbatim Japanese source of record:
`tmp/wb-core-20261016/source-website-builder.skill.md`, rev `sha256:c092a96b...`) and
re-based on the motion spec (`docs/specs/motion-design-assistant-spec.md`) and the
Koerner money doctrine (`docs/money-brain/koerner-doctrine.md`).

## Money frame

Pricing is an anchor menu, never a promise (doctrine honesty law):

- Basic $1,000 - one-page landing, responsive, contact form, 1 revision
- Standard $2,500 - up to 5 pages, custom design, motion, basic SEO, 2 revisions
- Premium $5,000 - up to 10 pages, CMS wiring, unlimited revisions, 1 month support
- Maintenance $50-100/mo - content updates, patches, backups, monitoring (the retainer)

Site classes are a scoping menu: landing / portfolio / corporate. E-commerce and bundled
backends (Stripe, Supabase/Firebase, email) are OUT of default scope - every one touches
credentials, accounts, or recurring cost, so they run only as a gated mode after approval.

## Intake

Business, industry, audience, pages, colors, tier - plus the journey fields the motion
spec mandates per chapter: visual job, dominant effect, reading state, motion-off state.
Style presets (modern/minimalist/corporate/creative) are banned as slop vectors; derive a
per-client visual language instead.

## Stack law

- Default: Vite + TypeScript + theme tokens (+ three.js / Remotion only when the job needs them).
- Next.js is a per-project, gated target only when the client host requires it - pin the
  current major and use React-19-era APIs. The source skill's "Next 14+" floor is stale
  (React 19 support starts at Next 15 with breaking async-params/caching changes).
- Motion: Kowalski register only - 150/220/400 ms, 60 ms stagger, named easings,
  transform/opacity first. Framer Motion or any new library needs explicit justification
  and approval.
- Reading modes are designed, never retrofitted: a labeled motion toggle plus
  `prefers-reduced-motion` support ship with the components (flattened flow, ambient
  movement stopped, controls kept, no strobing, no autoplay).

## Workflow (journey-first, per the motion spec)

1. Read before replacing - audit what exists at the target before writing anything.
2. Design the journey - chapter map with the four intake journey fields per chapter.
3. Choose the engine - simplest suitable technology; deviations need a stated reason.
4. Prove one slice - build the hero plus the hardest scene first; checkpoint with Vinny.
5. Finish pages, tokens from commit 1.
6. Inspect actual pixels - screenshots, forward and reverse, after the last material change.
7. Package for reuse - Block Card for any reusable motion block.

## Film stage (Flute)

The site's real React UI is the film set. On a dedicated branch (`git switch -c flute-scenes`):

```sh
npm install @webprodigies/flute && npx flute init     # automatic for Vite/Next
npx flute scenes                                       # catalog
npx flute open --url http://127.0.0.1:5173
npx flute snapshot --scene <shot> --url http://127.0.0.1:5173
```

One scene pair per shot: `src/flute/scenes/<shot>.scene.json` (camera, focus, motion
keyframes) + `<shot>.tsx` (imports the host's real components, returns `Surface` elements).
Export needs FFmpeg plus one-time `npx playwright install chromium`, Node 22.12+, and the
dev server running:

```sh
npx flute export --url "http://127.0.0.1:5173/?flute-preview=1&flute-scene=<shot>" --output <shot>.mp4 --fps 60
```

Honesty: depth-of-field is DOM blur, not ray-traced bokeh; snapshots may contain visible
app data - no client secrets or private data in pitch films. Flute films real UI; Remotion
(kinetic-forge) stays the engine for titles/stingers/non-DOM assets.

## Verification gates (fill before any handoff)

Statuses: Verified / Partial / Blocked; integration rows use Installed / Preview only / Not
tested. Full table: `docs/specs/website-builder-core-integration.md` Gates.

1. Journey + reading modes designed (brief.md evidence)
2. Motion-off mode (toggle, normal flow, controls kept)
3. `prefers-reduced-motion` honored, incl. live change; no autoplay
4. Scroll forward/reverse, fast jumps, clamped progress
5. Actual-pixel inspection after last change (screenshots)
6. Keyboard + focus, ~44 px targets, no traps
7. Performance + cleanup (listeners/observers/loops released)
8. Film export integrity (controls excluded, MP4 plays, deterministic)
9. Film reading state (poster frame, no autoplay, captions when narrated)
10. Motion token audit (150/220/400 ms only; deviations listed with reasons)
11. Rights + cost recorded (free/paid/recurring stated)
12. Typecheck + build clean; preview vs production stated honestly

## Deliver

Default deliverable is a PRIVATE PREVIEW; publishing or changing a live site is an
approval gate. Ship site + film together with setup/env/deploy docs, rights and cost
notes, the filled gate table, and the maintenance-lane offer. Money framing follows the
Koerner same-day output contract; every dollar figure is a corpus claim, not a guarantee.

## Run + selftest

```sh
bash scripts/selftest.sh    # must exit 0 before packaging
```

Selftest is offline: frontmatter shape (exactly `name` + `description`), required
sections present, provenance revision marker present. Live smoke (optional, needs the
demo up): `npx flute scenes` lists scenes and `curl` on the preview URL returns 200.
