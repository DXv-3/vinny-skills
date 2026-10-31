# SKILLS INDEX — the lean map

**Load this, not the 115KB inventory.** This file is the cheap always-loadable map of every
skill + ability on this machine (~4K tokens whole; greppable by section). It mirrors the lane
routers in `skill-orchestrator/SKILL.md`, which stays the routing authority.
Heavy layers stay on disk — query them, never load them:
`~/bin/skills-indexer --query <term>` (0.003s) · `~/.agents/SKILLS-CATALOG.tsv|json` ·
`~/.agents/SKILLS-INVENTORY.md` (760 skills, all roots — ~29K tokens) ·
`skill-orchestrator/COVERAGE.md` (~14K tokens).
Generated 2026-09-28 · **300 library skills** (`~/.agents/skills/`) + ZCode plugin skills.

## The 30-second protocol

1. Task → find the lane below → pick 1–3 skills by name.
2. Read frontmatter only: `head -40 ~/.agents/skills/<name>/SKILL.md` (~150 tokens).
3. Load the full SKILL.md of at most 1–2 finalists you will actually execute.
4. Non-trivial or multi-domain → run `skill-orchestrator` instead of hand-routing.
5. Never bulk-read SKILL.mds and never `find`/`grep -r` the library (token flood, 120s).

**Fast lanes:** iOS/Swift feature → A (`xcode-project-analyzer`, `ios-fullstack`, kit by name) ·
Landing/site/game → B (`mengto-design-first-ui-prompting`, `mengto-build-awwwards-quality-sites`, theme skill) ·
Research → C (`deep-research-free` default; `agent-reach` router) · Ship → D (`ship-it`) ·
Unsure which skills → E (`skill-orchestrator`, `skill-workflow`) · Browser/z.ai → F.

## Lane A — Apple / iOS / macOS (103)

**Recon & Xcode tooling:** `xcode-project-analyzer` (project audit) · `xcode-build-orchestrator`
(speed-up pipeline: `xcode-build-benchmark` → `xcode-compilation-analyzer` → `spm-build-analysis`
(recommend-only) → approval → `xcode-build-fixer` — the ONLY applier) · `xcode-project-setup`
(approval-gated SPM/plist applier) · `ios-simulator` (simctl) · `debugging-instruments`
(LLDB/Instruments/hangs) · `ios-memgraph-analysis` (leaks) · `ios-ettrace-performance` (launch) ·
`ios-accessibility` · `ios-localization` · `ios-networking` · `device-integrity` ·
`clipboardlux-macos-debugging` (**HUMAN-ONLY** — ClipboardLUX case history, never auto-fire).

**Unified app skills (whole features; supersede kits broadly):** `ios-fullstack`, `ios-ai-integration`,
`ios-animation-master`, `ios-camera-ar-pipeline`, `ios-data-persistence`, `ios-deep-link-universal`,
`ios-offline-first`, `ios-performance-debug` (triage umbrella; specialists are sharper),
`ios-release-polish`, `ios-security-auth`, `apple-on-device-ai` (Foundation Models/Core ML/MLX).

**Swift & SwiftUI:** `swift-language`, `swift-concurrency`, `swift-codable`, `swift-formatstyle`,
`swift-api-design-guidelines`, `swift-architecture`, `swift-charts`, `swift-security`,
`swift-testing`, `swiftdata`, `swiftlint`, `swiftui-animation`, `swiftui-gestures`,
`swiftui-layout-components`, `swiftui-liquid-glass`, `swiftui-navigation`, `swiftui-patterns`,
`swiftui-performance`, `swiftui-uikit-interop`, `swiftui-webkit`.

**Frameworks (invoke by exact name when touched):** accessorysetupkit, activitykit,
adattributionkit, alarmkit, app-clips, app-intents, appmigrationkit, audioaccessorykit,
authentication, avkit, background-processing, browserenginekit, callkit, carplay, cloudkit,
contacts-framework, core-bluetooth, core-data, core-motion, core-nfc, coreml, cryptokit,
cryptotokenkit, dockkit, energykit, eventkit, financekit, focus-engine, gamekit, healthkit,
homekit, mapkit, metrickit, musickit, natural-language, paperkit, passkit, pdfkit, pencilkit,
permissionkit, photokit, push-notifications, realitykit, relevancekit, scenekit, sensorkit,
shareplay-activities, speech-recognition, spritekit, storekit, tabletopkit, tipkit,
vision-framework, weatherkit, widgetkit.
Entitlement/Apple-approval gated: browserenginekit, carplay, financekit, sensorkit, energykit,
weatherkit, permissionkit, musickit app service, critical alerts. Beta-flagged (re-verify vs
current docs): appmigrationkit, audioaccessorykit, energykit, relevancekit, paperkit, metrickit.
Device required: BLE, DockKit, SensorKit, push, Metal, CarPlay, AlarmKit.

## Lane B — Web build & design (156 = 143 mengto-* + 13; unprefixed names are mengto-*)

**Chain:** `design-first-ui-prompting` (spec) → `build-awwwards-quality-sites` (master build;
name one theme + libraries) → effect/library skills → `test-playable-web-games` (games) →
`iterate-until-verified` / `audit-verify-explain-grade-5` (verify at 1440px + 390px via
`browser-use:web-gui-tester`) → `audit-reference-originality` → `publish-project-to-github`.
`web-technique-to-skill` = family quality constitution (mechanism-not-adjectives).

**Method/meta (14):** coding-skill, article-prompts-to-skills, web-technique-to-skill,
video-to-superprompt, html-to-interaction-prompts, design-first-ui-prompting,
iterate-until-verified, build-awwwards-quality-sites, publish-project-to-github,
audit-reference-originality, audit-verify-explain-grade-5, audit-ai-design-slop,
no-ai-design-slop, performance-profiling (⚠️ Apple Instruments/MetricKit — Lane A verify).

**Core web (non-mengto, 12):** `frontend-design` (aesthetic direction) · `ui-ux-pro-max`
(⚠️ heaviest skill in library — 658-line rulebook + CSVs + scripts; load in pieces) ·
`modern-web-guidance` (run `npx -y modern-web-guidance@latest` FIRST) · `web-artifacts-builder`
(single-HTML React) · `threeui-reference` (102 components + 45 shaders at `~/Projects/threeui`) ·
`pop-motion` (CSS motion; read reference-gallery.md first) · `tools-ui` + `agent-ui` (agent chat
UI, shadcn) · `img2threejs` (image → procedural Three.js model) · `walkable-architecture-storytelling` (minted 9/27 from seijaku) · `text-to-cad` (CAD/STEP/STL/G-code;
pairs with /home/hatch; RFQ send = confirm with user first) ·
`visual-self-review-loop` (render→screenshot→critique gate between build chunks).

**Pages (5):** landing-page, pricing-page, product-proof-saas, operational-enterprise-ai,
editorial-service-booking.
**Themes/layout (28):** agency-grid-layout-minimal, blue-cloudy-clean-modern,
blue-laser-clean-glass-layout, book-serif-index, bright-green-tech-system-webgl,
clean-minimal-beige-light-mode, dark-blue-contrasting-clean, dark-glass-clean-layout,
documentary-brutalist-agency, editorial-portfolio-chapters, editorial-tech, framed-grid-layout,
framed-tech-dark-border-gradient, funky-purple-container-tech, glass-dark-mode-clock,
glass-dark-ui, high-contrast-skeuomorphic-clean, image-first-grid-layout,
light-mode-paper-technical, mesh-gradient-dark-blue-clean, nested-container-clean-agency,
nested-container-frames, orange-clean-paper-saas, skeuomorphic-ui, split-layout-technical,
tech-green-dark-mode-modern, technical-wireframe-info-layout, dither-laser-dark-mode.
**Libraries (7):** gsap, tailwindcss, threejs, unicorn-studio, matterjs, cobejs, vantajs.
**Animation/effects (31):** animation-systems, animation-on-scroll,
cinematic-gsap-lenis-motion-system, cinematic-scroll-storytelling,
gsap-scrolltrigger-storytelling, masked-reveal, staggered-word-reveal,
scroll-scrubbed-word-reveal, scroll-scrubbed-visual-sequence, scroll-progress-timeline,
scroll-world-storytelling, marquee-loop, optimize-web-animations, reveal-hover-effect,
css-alpha-masking, css-border-gradient, beautiful-shadows, progressive-blur, beam-glow-states,
liquid-metal-border, thinking-orbs, falling-leaves, gooey-blob-system, dither-background,
atmosphere-background, background-grid-webgl, webgl-laser, corner-lasers, container-lines,
corner-diagonals, number-details.
**3D/WebGL & cursor (27):** soft-body-materials (HOUSE: deformable solids — XPBD tets + skinned surface,
WebGPU/three ladder, grab/cut grammar; minted from melon-jelly study 9/28) · build-threejs-scroll-worlds, threejs-landscape, threejs-towers,
threejs-weather, build-wireframe-scan-reveal, webgl-3d-object, webgl-landing-steering, globe-gl,
globe-particles, add-mouse-driven-orbit, add-shader-cursor-trail, shaders-cursor-ripples,
ambient-section-particles, build-interactive-particle-trail, pointer-trail-emitter,
3d-falling-leaves, 3d-four-seasons, 3d-high-poly-models, 3d-high-resolution-textures,
3d-retina-resolution, 3d-sky-background, 3d-sky-rays, 3d-ultra-realistic-water, 3d-virtual-tour,
interactive-scene-graph (JSON→scene, pan/zoom/focus, hit-testing).
**Games (21):** build-isometric-arpg, ship-web-games, build-mobile-threejs-games,
optimize-threejs-games, author-game-levels, design-action-combat, design-game-encounters,
tune-enemy-ai, implement-fog-of-war, build-game-audio-feedback, build-game-camera-controls,
build-game-changelog, build-game-inventory, build-game-map-editor, build-game-monster-system,
build-threejs-enemy-systems, create-game-vfx, build-hybrid-game-assets, build-rigged-game-assets,
build-vesperfall-review-assets.
**Assets/media (6):** unsplash-asset-images, elevenlabs-tts, aura-asset-images, company-logos,
solar-duotone-bold, codex-gpt-image-2-5-flare (built-in image gen).
**Writing/social (2):** write-like-meng-on-x, x-bookmark-quote-posts.
**Capture/publishing (5):** daily-ui-inspiration-capture, build-daily-inspiration-sites,
browser-video-recording, stitched-full-page-capture, generate-reference-inspired-brand-worlds.

## Lane C — Research & evidence (19)

**Depth ladder** (checkpoint to `~/Documents/research/INDEX.md` same turn — never re-run covered
topics): `parallel-deep-research` (hosted; auto-falls back on auth failure) → `deep-research-free`
(zero-auth DEFAULT) → `deep-research` (heavy evidence ledger). `firecrawl-deep-research` needs
`FIRECRAWL_API_KEY` = [NEEDS USER].
**GitHub:** `unified-github-research` (supersedes both below for NEW runs — solo sieves + swarm modes + omission pass) ·
`github-deep-research` (MCP unavailable here — degrades to `gh`, authed as DXv3) ·
`swarm-github-research` (worked pattern example, not a starting point).
**Fetch & search:** `agent-reach` (MUST-USE router, 15 platforms; Exa/jina/gh/yt-dlp free;
Twitter/Reddit/XHS need logins) · `web-search`, `agent-tools`, `agent-browser` need inference.sh
`infsh` = [NEEDS USER] · `osint-datasets` (fully local).
**Sessions:** `continue-claude-work` (resume from JSONLs) · `chat-archaeologist` (grep/jq triage).
**Prompt KB (4,596 records):** `kb-collection-query` (preferred — kb-waterhole MCP
`kb_search`/`kb_get`/`kb_stats` first, shim fallback; read-only; every claim carries record ID) ·
`waterhole-ask` (sibling ladder; shim serves an OLDER copy; never echo the shim token).
**Also:** `browser-act-zai` (ALL z.ai/GLM browser work) · `microsoft-foundry` (Azure MCP required) ·
`custom-brainstorm-storm` (**HUMAN-ONLY**, multi-agent deliberation).

## Lane D — Product / ship (4 primary)

`ship-it` (5-phase pipeline; reads `~/SYSTEM-RULES.md` + `~/SYSTEM-STATE.md`; ROI-ranked; one API
at a time) · `app-store-optimization` · `app-store-review` (also A verify) · `progress-report`
(stage 9 of every lane). Helpers when the feature needs them: `ios-release-polish` (A),
`mengto-publish-project-to-github` (B), `push-notifications`/`storekit` (A).

## Lane E — Pipeline & meta (11)

`skill-orchestrator` (the router itself) · `using-superpowers` (1% invoke rule) · `skill-workflow`
(unsure WHICH skills chain) · `find-skills` (external discovery + install) · `skill-dashboard`
(local catalog) · `brainstorming` → `writing-plans` (hard gate: no code before approved design) ·
`executing-plans` · `test-driven-development` · `systematic-debugging` (any failure) ·
`chat-pattern-miner` (**HUMAN-ONLY**; drafts only, never auto-install/send).
Out-of-library helpers referenced by skills (closest substitute instead): chain-orchestrator,
code-doctor, context-surfacer, 12-factor-agents, swift-logging, claude-code-history-files-finder.

## Lane F — Host & browser automation

**`web-guest-manners`** — MUST-USE BEFORE any agent browses/forms/scrapes any website: front-door
check (`~/Projects/WEB-GUEST-SITELIST.md`), own profile per agent, human pacing, hard stops at
CAPTCHA/login/block pages (never auto-solve, never rotate IPs), no disguise kits, visit log.
**`door2-chat-extraction`** — logged-in extraction of the user's own chats+files from ANY web platform
(observed endpoints → auth capture → enumerate → harvest → files → SkillDrive ingest; worked on Manus 9/27; next: z.ai/DeepSeek/Qwen).
Route by target: **z.ai** → `browser-act-zai` · **local browser** → `browser-use:control-browser`
(default) / `browser-use:web-gui-tester` (rendered-UI testing) · **cloud/scrape** → `agent-browser`
(infsh [NEEDS USER]) · **macOS GUI** → `macos-gui-automation` (AppleScript+cliclick, needs
Accessibility permission).

## ZCode plugin skills (beyond the 290)

`documents:docx` · `pdf:pdf` · `presentations:pptx` · `spreadsheets:xlsx` (office docs) ·
`github:*` (commit, pr, issue, repo, gist, release, secret, setup, codespace, workflow-run) ·
`browser-use:*` (above) · `computer-use` (full desktop control) · `video-agent-kit:*`
(video-edit-agent, video-edit-assembly, video-recap-workflows, video-speech-workflows, env-setup —
transcribe/detect-shots/arrange/bind/render/QC pipeline) · `video2code:*` (url2video, video2code,
video2code-3d, video2fullstack, web-replicate) · `zcode-guide:diagnosing-*` + `zcode-configuration-guide`
(config/hooks/MCP/plugins troubleshooting) · `skill-creator` · `plugin-creator` · `dynamic-workflows`
(multi-subagent orchestration scripts).

## Abilities (not SKILL.md files, but real)

- **MCP `kb-waterhole`:** `kb_search`/`kb_get`/`kb_stats` over the 4,596-record prompt KB
  (`~/surface/prompt_kb.db` authoritative; shim :8921 serves an older copy; read-only forever).
- **MCP video-edit tools:** inspect_media, speech_transcribe, detect_shots, video_ingest,
  video_watch_segment, arrange/bind/render/QC — the whole video pipeline (see `video-agent-kit:*`).
- **`web_reader`:** fetch URL → markdown.
- **Agents:** Explore (read-only sweeps — returns conclusions), general-purpose, and the
  visual-judge family (pptx/docx/pdf/poster/chart acceptance). **ONE subagent at a time on this machine.**
- **Hooks:** SessionStart context-loader (injects night-log + standing rules) · PreToolUse Bash
  guardrail (exit-2 deny).
- **Commands:** `/kb` (prompt KB query), `/flood`, `/animate`, `/motion-review` (plugin commands).

## State files (read before working, checkpoint after)

`~/Projects/BUILD-STATE-2026-09-21.md` (master spec + queue) · `~/Projects/CONQUEST-PLAN.md`
(Downloads board B1–B6) · `~/Documents/research/INDEX.md` (research — never re-research covered
topics) · `~/Projects/NIGHT-SHIFT-LOG.md` · `~/SYSTEM-STATE.md` (machine) ·
`~/bin/skills-indexer` (rebuild after skill changes).

## Human-only register (never auto-fire — name the /command instead)

`chat-pattern-miner` · `custom-brainstorm-storm` · `clipboardlux-macos-debugging`

## Maintenance

After adding/removing skills: run `~/bin/skills-indexer`, then update lane counts here and in
`skill-orchestrator/SKILL.md`, and regenerate `skill-orchestrator/COVERAGE.md`. Keep this file
lean — one line per group, hooks ≤ 8 words, no full descriptions.
