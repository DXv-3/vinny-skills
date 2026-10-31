---
name: skill-orchestrator
description: "Skill Orchestrator"
---

# Skill Orchestrator

The library at `~/.agents/skills/` holds **296 skills** — a live corpus that keeps growing without notice (14 additions surfaced during the 2026-09-26 upgrade). No agent holds them all in mind.
This skill is the router: it classifies the task into a lane, runs the fixed pipeline,
and names the exact skills for each stage. `COVERAGE.md` next to this file is the
complete per-skill index (generated from the library, one line per skill).

Invocation rule (from `using-superpowers`): if there is even a 1% chance a skill applies,
invoke it with the Skill tool. Wrong skill? Drop it and move on. Process skills come
before implementation skills. The 1% rule never overrides the human-only register below —
for a marked skill, "invoke" means naming its explicit `/command` for the user, never
auto-firing it.

## The operating contract (non-negotiable)

1. Identify the repository/project root. **The repo root is the default write boundary.** Outside it: read-only unless the user explicitly authorizes a path.
2. Never move, delete, rename, or bulk-reformat anything during recon. Creating new files is fine only where the task requires it.
3. Never read, print, upload, or index secret values (`.env`, keys, certs, cookies, personal docs). Record only that a sensitive item exists and where.
4. Keep an evidence log: path inspected → tool → finding → confidence → next action.
5. Never claim to have inspected something you did not inspect. Say what you could not access.
6. Before any destructive or hard-to-reverse operation, stop and show the exact operation, paths, reason, rollback plan.
7. Small reversible batches. Build and test after every batch before continuing.
8. Ask only when a missing choice would materially change architecture, data safety, permissions, or cost; otherwise pick a sensible default and document it.

## Step 0 — Orient on the machine

- Read `~/SYSTEM-STATE.md` — authoritative machine state. `~/SYSTEM-RULES.md` for product/ship work. Never redo indexed work.
- Skill lookup: `cat ~/.agents/SKILLS-CATALOG.json` (or `.tsv`), or `~/bin/skills-indexer --query <term>`. Do **not** `find` over the library (0.003s vs 120s).
- Xcode 27 beta builds may need the `DEVELOPER_DIR` trick — check SYSTEM-STATE.md notes.
- ZCode plugins are also skills: `documents:docx`, `presentations:pptx`, `spreadsheets:xlsx`, `pdf:pdf`, `browser-use:control-browser`, `browser-use:web-gui-tester`, `skill-creator`, `plugin-creator`, `zcode-guide:*`.

## The pipeline

| Stage | Gate/exit criteria | Always invoke | Lane skills (see routers) |
|---|---|---|---|
| 1. Contract | Boundaries stated; no writes yet | — (restate contract) | — |
| 2. Orient | SYSTEM-STATE read; catalog queried | `skill-dashboard` (catalog) | lane recon skills |
| 3. Recon | Read-only audit artifacts written to `docs/agent-audit/` in the target repo (inventory, architecture map, priority backlog) | — | Lane recon skills |
| 4. Design & plan | Design approved by user; plan written; `AGENT-BRIEF.md` written to project root | `brainstorming` → `writing-plans` (hard gate: no code before approved design) | lane build skills previewed, not run |
| 5. Build in batches | Each batch: files+tests declared → edit → build → test | `test-driven-development`, `executing-plans` (if a plan file exists); the executing agent follows `AGENT-BRIEF.md` | lane build skills |
| 6. Verify | All green; claims evidence-backed | `systematic-debugging` (any failure) | lane verify skills |
| 7. Adversarial review | Findings fixed or logged; re-tested | — | lane audit skills |
| 8. Ship | Deployed/submitted; state recorded | — | lane ship skills |
| 9. Handoff | Report card + next 3 actions; SYSTEM-STATE updated; outcome appended to `AGENT-BRIEF.md` | `progress-report` | `continue-claude-work`, `chat-archaeologist` (later resumption) |

Batch discipline (declare before editing): exact files to change, intended behavior, tests/build commands, migration/privacy/data-loss risks. Smallest coherent change. If scope expands past the declared batch, stop and propose the next batch.

## The AGENT-BRIEF — durable work order

At the end of Stage 4 — design approved, before the first build batch — write the routing outcome
to `<project-root>/AGENT-BRIEF.md`. The brief is the contract between the assigner and the
executor: any executing agent (this session later, a subagent, or a fresh session) reads the brief
instead of re-deriving the plan from chat history. Template:

```markdown
# AGENT-BRIEF — <one-line task name>
Date: YYYY-MM-DD · Orchestrator: skill-orchestrator · Lane: <A–F>

## Objective
<what "done" looks like, one paragraph — the approved design condensed>

## Constraints
- Write boundary: <repo root; plus any user-authorized paths outside it>
- Secrets: never read/print/index .env, keys, certs — record existence only
- Batches: one reversible batch at a time — declare files/behavior/tests, build, test, checkpoint
- <task-specific constraints: perf budgets, platform versions, style laws, token routing>

## Skills to load (in order)
| # | Skill | Path | Stage | Why |
|---|---|---|---|---|
| 1 | `<name>` | `~/.agents/skills/<name>/SKILL.md` | recon | <one line> |

## Verify gate
- Commands: <exact build/test/lint commands>
- PASS = <observable criteria: tests green, coverage N/N, browser-check 1440/390px, ...>
- Any red = stop → `systematic-debugging`; claims never past evidence

## Out of scope
<what this brief does NOT authorize — next-batch candidates listed, not started>
```

Brief rules: create it new or append to it — never rewrite its history. Check off the verify gate
with evidence paths as stages complete; append the outcome at Stage 9. A human-only skill that
routing surfaces goes in the skills table marked `HUMAN-ONLY — requires explicit /command` and is
never pre-invoked. When dispatching a subagent, paste the relevant brief section into its prompt —
the brief is the handoff, not the conversation.

## Lane routers

Pick the lane(s); invoke by exact name. Every library skill appears in exactly one lane below (cross-listed where noted).

**Human-only lane attribute (`disable-model-invocation`).** Some skills must never auto-fire from
description matching — they run only when the user explicitly summons them (`/command`, `$skill`,
or a direct order). Route-time rule: before invoking a skill a lane router surfaced, check its
frontmatter for `disable-model-invocation: true` and the register below. If marked: **do not
invoke** — state the exact `/command` the user can run and continue routing. This is triage's
discipline (mattpocock/skills): an assigner that auto-fires a human-summoned skill breaks its own
contract.

**Human-only register** (seeded 2026-09-26; no library skill carries the frontmatter flag yet —
these are seeded from their own documented contracts; extend as skills adopt the flag):

| Skill | Lane | Why human-only |
|---|---|---|
| `chat-pattern-miner` | E | Drafts only, never auto-installs/auto-sends; heavy batch-mining job the user schedules |
| `custom-brainstorm-storm` | C | Multi-agent deliberation — expensive and needs a research skill the user picks underneath |
| `clipboardlux-macos-debugging` | A | Single-app case history (ClipboardLUX on macOS 27 beta) — Vinny summons it for that app only |

### Lane A — Apple / iOS / macOS (103 skills)

**Recon/tooling:** `xcode-project-analyzer` (project config audit) → `xcode-build-orchestrator` for "speed up my builds" — that pipeline is `xcode-build-benchmark` (measure) + `xcode-compilation-analyzer` (type-check hotspots) + `xcode-project-analyzer` + `spm-build-analysis` (recommend-only) → user approval → `xcode-build-fixer` (the ONLY applier) → re-benchmark. Artifacts in `.build-benchmark/`. Also: `xcode-project-setup` (adds SPM packages / links plists via a bundled Swift script against real .pbxproj files — approval-gated, the only applier of project-file changes), `ios-simulator` (simctl), `debugging-instruments` (LLDB/Instruments/hangs), `ios-memgraph-analysis` (leaks/heap), `ios-ettrace-performance` (launch sampling), `ios-accessibility`, `ios-localization`, `ios-networking`, `device-integrity`, `clipboardlux-macos-debugging` (⚠️ case history for ClipboardLUX on macOS 27 beta only — never route general work here; **HUMAN-ONLY** — never auto-fire, explicit summons only).

**Unified app skills (whole-feature work; frontmatter-less, supersede kits broadly — prefer the focused kit for narrow questions):** `ios-fullstack` (new app end-to-end; also use instead of the `ios-swift-development` stub), `ios-ai-integration`, `ios-animation-master`, `ios-camera-ar-pipeline`, `ios-data-persistence`, `ios-deep-link-universal`, `ios-offline-first`, `ios-performance-debug` (triage umbrella — its CLI snippets are less accurate than the specialists), `ios-release-polish`, `ios-security-auth`, `apple-on-device-ai`.

**Swift language & SwiftUI:** `swift-language`, `swift-concurrency`, `swift-codable`, `swift-formatstyle`, `swift-api-design-guidelines`, `swift-architecture`, `swift-charts`, `swift-security`, `swift-testing`, `swiftdata`, `swiftlint`, `swiftui-animation`, `swiftui-gestures`, `swiftui-layout-components`, `swiftui-liquid-glass`, `swiftui-navigation`, `swiftui-patterns`, `swiftui-performance`, `swiftui-uikit-interop`, `swiftui-webkit`.

**Frameworks (invoke by name when the task touches it; each routes siblings via its own boundary table):** accessorysetupkit, activitykit, adattributionkit, alarmkit, app-clips, app-intents, appmigrationkit, audioaccessorykit, authentication, avkit, background-processing, browserenginekit, callkit, carplay, cloudkit, contacts-framework, core-bluetooth, core-data, core-motion, core-nfc, coreml, cryptokit, cryptotokenkit, dockkit, energykit, eventkit, financekit, focus-engine, gamekit, healthkit, homekit, mapkit, metrickit, musickit, natural-language, paperkit, passkit, pdfkit, pencilkit, permissionkit, photokit, push-notifications, realitykit, relevancekit, scenekit, sensorkit, shareplay-activities, speech-recognition, spritekit, storekit, tabletopkit, tipkit, vision-framework, weatherkit, widgetkit.

Entitlement/Apple-approval gated: browserenginekit, carplay, financekit, sensorkit, energykit, weatherkit, permissionkit, musickit app service, critical alerts. Beta-flagged (re-verify vs current docs): appmigrationkit, audioaccessorykit, energykit, relevancekit, paperkit, metrickit, Swift 6.4/Xcode 27 corners. Physical device required for: BLE, DockKit, SensorKit, push, Metal, CarPlay, AlarmKit.

### Lane B — Web build & design (156 skills: 143 mengto-* + 13 other)

**Expected chain:** `mengto-design-first-ui-prompting` (spec) → `mengto-build-awwwards-quality-sites` (master build; requires naming one theme skill + library skills) → effect/library skills → `mengto-test-playable-web-games` (games) → `mengto-iterate-until-verified` / `mengto-audit-verify-explain-grade-5` (verify; browser-check at 1440px + 390px before claiming done) → `mengto-audit-reference-originality` → `mengto-publish-project-to-github`. `mengto-web-technique-to-skill` is the family's quality constitution (mechanism-not-adjectives, demo fidelity). Browser-verify with `browser-use:web-gui-tester` before shipping.

**Method/meta (14):** coding-skill, article-prompts-to-skills, web-technique-to-skill, video-to-superprompt, html-to-interaction-prompts, design-first-ui-prompting, iterate-until-verified, build-awwwards-quality-sites, publish-project-to-github, audit-reference-originality, audit-verify-explain-grade-5, audit-ai-design-slop (evidence-backed audit for AI-design clichés), no-ai-design-slop (prevent/remove slop while building), performance-profiling (⚠️ this one is Apple Instruments/MetricKit — see Lane A verify).

**Core web (non-mengto):** `frontend-design` (aesthetic direction), `ui-ux-pro-max` (658-line rulebook + data/ CSVs + scripts/search.py, design_system.py — heaviest skill in the library), `modern-web-guidance` (run `npx -y modern-web-guidance@latest` FIRST for HTML/CSS/JS best practice), `web-artifacts-builder` (single-HTML React artifacts), `threeui-reference` (102 components + 45 shader collections at `~/Projects/threeui`), `pop-motion` (CSS motion system — read its reference-gallery.md before coding), `tools-ui` + `agent-ui` (agent chat/tool-call UI, shadcn), `walkable-architecture-storytelling` (minted 2026-09-27 from seijaku — scroll-driven walkable architecture worlds), `visual-self-review-loop` (render→screenshot→critique loop with a pixel checklist + render gates — runs between build chunks, feeds mengto-iterate-until-verified).

**Pages & conversion (5):** landing-page, pricing-page, product-proof-saas, operational-enterprise-ai, editorial-service-booking.
**Theme/layout systems (28):** agency-grid-layout-minimal, blue-cloudy-clean-modern, blue-laser-clean-glass-layout, book-serif-index, bright-green-tech-system-webgl, clean-minimal-beige-light-mode, dark-blue-contrasting-clean, dark-glass-clean-layout, documentary-brutalist-agency, editorial-portfolio-chapters, editorial-tech, framed-grid-layout, framed-tech-dark-border-gradient, funky-purple-container-tech, glass-dark-mode-clock, glass-dark-ui, high-contrast-skeuomorphic-clean, image-first-grid-layout, light-mode-paper-technical, mesh-gradient-dark-blue-clean, nested-container-clean-agency, nested-container-frames, orange-clean-paper-saas, skeuomorphic-ui, split-layout-technical, tech-green-dark-mode-modern, technical-wireframe-info-layout, dither-laser-dark-mode.
**Libraries (7):** gsap, tailwindcss, threejs, unicorn-studio, matterjs, cobejs, vantajs.
**Animation/scroll/CSS effects (31):** animation-systems, animation-on-scroll, cinematic-gsap-lenis-motion-system, cinematic-scroll-storytelling, gsap-scrolltrigger-storytelling, masked-reveal, staggered-word-reveal, scroll-scrubbed-word-reveal, scroll-scrubbed-visual-sequence, scroll-progress-timeline, scroll-world-storytelling, marquee-loop, optimize-web-animations, reveal-hover-effect, css-alpha-masking, css-border-gradient, beautiful-shadows, progressive-blur, beam-glow-states, liquid-metal-border, thinking-orbs, falling-leaves, gooey-blob-system, dither-background, atmosphere-background, background-grid-webgl, webgl-laser, corner-lasers, container-lines, corner-diagonals, number-details.
**3D/WebGL & cursor (26):** build-threejs-scroll-worlds, threejs-landscape, threejs-towers, threejs-weather, build-wireframe-scan-reveal, webgl-3d-object, webgl-landing-steering, globe-gl, globe-particles, add-mouse-driven-orbit, add-shader-cursor-trail, shaders-cursor-ripples, ambient-section-particles, build-interactive-particle-trail, pointer-trail-emitter, img2threejs (reference image → quality-gated procedural Three.js model in code), 3d-falling-leaves, 3d-four-seasons, 3d-high-poly-models, 3d-high-resolution-textures, 3d-retina-resolution, 3d-sky-background, 3d-sky-rays, 3d-ultra-realistic-water, 3d-virtual-tour, interactive-scene-graph (JSON nodes/edges → SVG/Canvas scene with pan/zoom/focus camera and hit-testing).
**Games (21):** build-isometric-arpg, test-playable-web-games, ship-web-games, build-mobile-threejs-games, optimize-threejs-games, author-game-levels, design-action-combat, design-game-encounters, tune-enemy-ai, implement-fog-of-war, build-game-audio-feedback, build-game-camera-controls, build-game-changelog, build-game-inventory, build-game-map-editor, build-game-monster-system, build-threejs-enemy-systems, create-game-vfx, build-hybrid-game-assets, build-rigged-game-assets, build-vesperfall-review-assets.
**Assets/media (6):** unsplash-asset-images, elevenlabs-tts, aura-asset-images, company-logos, solar-duotone-bold, codex-gpt-image-2-5-flare (built-in Codex image gen — transparent PNG ornaments, sprites, emblems, UI graphics).
**Fabrication/CAD (1):** text-to-cad — umbrella catalog: parametric CAD modeling, STEP/STL/3MF/DXF export, DFM checks, G-code, 3D-printer profiles (Bambu), SendCutSend quoting; pairs with the hatch pipeline (`/home/hatch`). RFQ submission is outward-facing — confirm with the user before send.
**Writing/social (2):** write-like-meng-on-x, x-bookmark-quote-posts.
**Capture/publishing (5):** daily-ui-inspiration-capture, build-daily-inspiration-sites, browser-video-recording, stitched-full-page-capture, generate-reference-inspired-brand-worlds.
(All unprefixed names above are `mengto-*`.)

### Lane C — Research & evidence (19 skills)

**Depth ladder (checkpoint reports in `~/Documents/research/INDEX.md` — never re-run covered topics):** `parallel-deep-research` (hosted, needs parallel-cli auth; on ANY auth/balance failure auto-falls back) → `deep-research-free` (zero-auth default: built-in web/fetch/gh tools) → `deep-research` (heavyweight evidence-ledger pipeline, McKinsey-style output). `firecrawl-deep-research` only with `FIRECRAWL_API_KEY`.

**GitHub:** `unified-github-research` (supersedes github-deep-research + swarm-github-research for NEW runs — solo 7-sieve pipeline + swarm zone mode + mandatory omission pass; route ALL "find every repo / ecosystem mapping" asks here first), `github-deep-research` (exhaustive repo discovery; degrades gracefully to plain `gh` CLI — on this machine the MCP tools are unavailable, gh is authed as DXv3). `swarm-github-research` is a worked example composing agent-reach + github-deep-research + web-search — treat as a pattern, not a starting point.

**Fetch & search:** `agent-reach` (MUST-USE router for 15 platforms; zero-config: Exa via mcporter, r.jina.ai, gh, yt-dlp; Twitter/Reddit/XHS need logins). `web-search` + `agent-tools` + `agent-browser` require an inference.sh `infsh` account (paid). `osint-datasets` is fully local (osint-cli + SQLite in `~/.ai-memory`).

**Sessions:** `continue-claude-work` (bundled extractor, resumes execution from Claude/Kilo JSONLs) vs `chat-archaeologist` (grep/jq triage across Claude/OpenCode/Cursor/git with finish/scrap verdicts).

Also here: `kb-collection-query` (preferred: answers ANY question about the 4,596-record prompt KB `~/surface/prompt_kb.db` by querying it, never from memory — kb-waterhole MCP tools `kb_search`/`kb_get`/`kb_stats` first, shim fallback; read-only forever, every claim carries its record ID, stale numbers marked `[verify live]`) + `waterhole-ask` (sibling router for the same KB — VM ask.py → tailnet shim → read-only sqlite `mode=ro` ladder, measured FTS5 syntax notes; the shim serves an OLDER copy, the DB is authoritative; never echo the shim token), `browser-act-zai` (z.ai login automation via browser-act-cli — route ALL z.ai/GLM browser work here), `microsoft-foundry` (Azure-only; blocks without Azure MCP foundry tools), `custom-brainstorm-storm` (multi-agent deliberation methodology — needs a research skill underneath; **HUMAN-ONLY** — never auto-fire, explicit summons only).

### Lane D — Product / ship (4 primary, cross-listed elsewhere)

`ship-it` (5-phase project→product pipeline; reads `~/SYSTEM-RULES.md` + `~/SYSTEM-STATE.md` first; ROI ranking; one API at a time, verify each; writes `~/Documents/ship-audit-YYYY-MM-DD.md`), `app-store-optimization`, `app-store-review` (also Lane A stage 7–8), `progress-report` (also stage 9 for every lane). Ship-stage helpers: `ios-release-polish` (A), `mengto-publish-project-to-github` (B), `push-notifications`/`storekit` (A, when the feature needs them).

### Lane E — Pipeline & meta (used by every lane)

`using-superpowers` (invoke-first rule), `skill-workflow` (book-club recommender — use when unsure WHICH skills chain), `find-skills` (exhaustive external discovery: `npx skills find` ≥10 queries + harvest-and-synthesize pipeline; also installs skills), `skill-dashboard` (local catalog), `chat-pattern-miner` (**HUMAN-ONLY** — never auto-fire; mines past chats into DRAFT hooks / slash commands / AGENTS.md rules / skills — drafts only, never auto-installs or auto-sends; corpus state at `~/Projects/chat-mining/INDEX.md`), `brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, `systematic-debugging`. Note: some skills reference helpers that live outside this library — `chain-orchestrator`/`code-doctor`/`context-surfacer` (opencode/claude skill dirs), `12-factor-agents` (referenced by using-superpowers), `swift-logging` (metrickit), `claude-code-history-files-finder` (continue-claude-work), and the github-ecosystem/opportunity-scout/codebase-memory MCP servers (github-deep-research degrades gracefully to plain gh) — substitute the closest skill from this file.

### Lane F — Host & browser automation

`web-guest-manners` (MUST-USE before any agent browses/forms/scrapes any site — front-door check via `~/Projects/WEB-GUEST-SITELIST.md`, per-agent profile, human pacing, hard stops at CAPTCHA/login/block pages, never auto-solve or rotate IPs, no disguise kits, visit log), `door2-chat-extraction` (logged-in chat+file extraction from any LLM web platform — Door 2 recipe, proven on Manus), `macos-gui-automation` (AppleScript + cliclick; needs Accessibility permission; Feedback Assistant submission flow), `browser-act-zai` (z.ai), `agent-browser` (cloud Playwright, infsh), ZCode-local: `browser-use:control-browser` (default for local browser work), `browser-use:web-gui-tester` (test rendered web UIs). Route by target: z.ai → browser-act-zai; local browser → browser-use plugin; cloud/scrape → agent-browser; ANY browsing/scraping task → web-guest-manners FIRST.

## Disambiguation (who wins overlaps)

| Question | Route |
|---|---|
| Narrow framework question | The kit skill (it owns the boundary; follow its sibling-routing table) |
| Whole feature spanning many frameworks | `ios-fullstack` / unified skills, kits for details |
| Slow builds | `xcode-build-orchestrator` pipeline — never `xcode-build-fixer` directly |
| Slow/janky app | `ios-performance-debug` triage → specialists above |
| Auth/security narrow | `authentication` / `swift-security` / `cryptokit` / `device-integrity`; whole feature → `ios-security-auth` |
| Persistence choice | `ios-data-persistence` decision matrix → `swiftdata` or `core-data` |
| On-device AI | `apple-on-device-ai` (router) → `coreml`/`vision-framework`/`natural-language`/`speech-recognition` |
| Deep research | Ladder in Lane C; default `deep-research-free` |
| Recover an old session | Resume work → `continue-claude-work`; triage/dig → `chat-archaeologist` |
| Browser automation | By target, Lane F |
| Web page build | `mengto-build-awwwards-quality-sites` + one theme + libraries; three scroll-storytelling variants — route on their own "Use When" text |

## Credentials & capability gates

| Gate | Skills blocked without it |
|---|---|
| inference.sh `infsh` login (paid) | agent-browser, agent-tools, web-search, agent-ui |
| `FIRECRAWL_API_KEY` | firecrawl-deep-research |
| parallel-cli auth + balance | parallel-deep-research (auto-falls back to deep-research-free) |
| `ELEVENLABS_API_KEY` (env only — never in source) | mengto-elevenlabs-tts |
| Azure MCP `foundry` tools | microsoft-foundry |
| gh CLI (authed as DXv3 here) | github-deep-research, agent-reach GitHub, swarm-github-research |
| Local binaries/datasets | osint-datasets (osint-cli + `~/.ai-memory`), macos-gui-automation (cliclick) |
| Local checkouts | threeui-reference (`~/Projects/threeui`), pop-motion (reference-gallery.md) |
| Apple entitlements / physical device | see Lane A lists |

## Parallel execution on this host (ZCode)

- Invoke skills with the **Skill tool** by exact name. Announce: "Using [skill] to [purpose]."
- Fan-out recon/review/research: spawn **Agent** subagents (Explore for read-only). This host allows **one subagent at a time** — dispatch sequentially, not in parallel batches. Hand each subagent its slice of `AGENT-BRIEF.md` — the brief is the contract; the subagent never re-derives the plan.
- Large orchestrated multi-agent runs: dynamic workflows (`zcode-guide:dynamic-workflows`, the CreateWorkflow tool) with `phase()` markers and gated `world.run` checks.
- Rendered deliverables (pptx/docx/xlsx/pdf/posters/pages) must pass the matching **visual-judge** agent (`presentations:visual-judge`, `documents:visual-judge`, `spreadsheets:visual-judge`, `pdf:visual-judge`) on rendered PNGs before you call them done. File generation itself: `documents:docx`, `presentations:pptx`, `spreadsheets:xlsx`, `pdf:pdf`.

## Stop conditions

Stop and ask the user only for: writes outside the repo boundary, deletions/moves, anything touching secrets or signing identities, purchases/account creation, and genuine architecture reversals (e.g., 3+ failed fixes per `systematic-debugging`). Everything else: pick the default, document it, keep moving.

## Maintenance

After adding/removing skills: run `~/bin/skills-indexer` (rebuilds `~/.agents/SKILLS-CATALOG.*` and updates `~/SYSTEM-STATE.md`), then regenerate `COVERAGE.md` (table = one line per skill) and update the lane counts above. 18 older skills lack a `name:` frontmatter field — they still load by directory name; no action needed.

## Worked examples

- **"Add offline sync to my SwiftUI app":** Lane A. Contract → `xcode-project-analyzer` recon → `brainstorming`/`writing-plans` → build batch with `swiftdata` + `cloudkit` + `background-processing` under TDD → verify `swift-testing` + `ios-offline-first` checklist → adversarial pass with `ios-security-auth` → `progress-report`.
- **"Build an Awwwards-grade landing page":** Lane B. `mengto-design-first-ui-prompting` spec → `mengto-landing-page` + one theme skill + `mengto-gsap`/`mengto-tailwindcss` → `mengto-build-awwwards-quality-sites` → `mengto-iterate-until-verified` + `browser-use:web-gui-tester` at 1440/390px → `mengto-audit-reference-originality` → `mengto-publish-project-to-github`.
- **"Map the GitHub ecosystem for X":** Lane C. `github-deep-research` (gh CLI) with `deep-research-free` for the write-up; register in `~/Documents/research/INDEX.md`; `progress-report` handoff.

Every example ends Stage 4 by writing `AGENT-BRIEF.md` to the project root before the first build batch; if routing surfaces a human-only skill (register above), the brief lists it as `HUMAN-ONLY — requires explicit /command` instead of invoking it.
