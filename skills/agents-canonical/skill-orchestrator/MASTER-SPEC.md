# Skill Orchestrator — Master Specification

**Date:** 2026-09-21 · **Status:** SHIPPED, test-verified · **Owner machine:** darwin/arm64 (Vinny's MacBook Air)
**Scope:** full audit of the agent skill library + design, build, and verification of the router that uses it.

| Artifact | Path | Role |
|---|---|---|
| Router (executable skill) | `~/.agents/skills/skill-orchestrator/SKILL.md` | The pipeline + lane routers. Invoke as `skill-orchestrator`. |
| Coverage index | `~/.agents/skills/skill-orchestrator/COVERAGE.md` | One row per skill (library + plugins) + verification log. |
| Routing test | `~/.agents/skills/skill-orchestrator/verify-coverage.sh` | PASS = every library skill token-matches SKILL.md. Run after every edit. |
| This document | `~/.agents/skills/skill-orchestrator/MASTER-SPEC.md` | The consolidated spec and evidence record. |
| Catalog | `~/.agents/SKILLS-CATALOG.json` (+ `.tsv`) | 0.003s lookup; rebuilt by `~/bin/skills-indexer`. |

---

## 1. Mission and outcome

**Ask:** scan all skills, review the content, build a skill workflow that uses everything.
**Delivered:** a four-pass content review of the entire library (four family agents, run sequentially — this host allows one subagent at a time — plus firsthand reads of the 12 process skills), consolidated into `skill-orchestrator`: a 9-stage pipeline with 6 lane routers that reach **every library skill, test-enforced at 275/275**.

Design constraint honored throughout: "use everything" does not mean invoking 275 skills in one run — it means **every skill is reachable through the router**, with precedence rules for overlaps and a mechanical test that fails the moment any skill becomes unreachable. The library is a live corpus; the test is the drift detector (it caught three skills born mid-build).

## 2. Library census

| Measure | Value |
|---|---|
| Library skills (`~/.agents/skills/`) | 275 (grew from 272 during the build — see §7) |
| Supporting files (references, scripts, demos) | ~1,443 across the library |
| Largest skill | `ui-ux-pro-max` (~6,466 words + 21 files: 14 CSVs, 2 scripts) |
| ZCode plugin skills (separate, auto-loaded) | 14 (documents, presentations, spreadsheets, pdf, browser-use ×2, skill-creator, plugin-creator, zcode-guide ×7) |
| Missing `name:` frontmatter | 18 (load by directory name; no action required) |
| Catalog total (all sources) | 743 (341 active / 176 archived / 226 vendor-user) |

**Lane decomposition (exclusive, sums to 275):** A Apple 103 · B Web 139 · C Research 18 · D Ship 4 · E Pipeline/meta 10 · F Host 1.

## 3. Structural conventions the library follows

1. **Apple family is self-routing.** Every skill: frontmatter "use when" → workflow → code patterns → Common Mistakes → Review Checklist → `references/<name>-patterns.md` on demand. Sibling boundary tables ("route X to Y") are first-class — the router leans on them instead of duplicating them.
2. **MengTo family is technique cards, not code.** Imperative SKILL.md (Use When / Workflow / named failures / tuning knobs / Avoid), real constants instead of adjectives, `demo/` folders (index.html + PROMPT.md + preview.jpg), browser verification at 1440/390px before any claim of done.
3. **Research skills checkpoint and register.** All deep-research variants write state files and register reports in `~/Documents/research/INDEX.md` — never re-run a covered topic.
4. **Two generations coexist in iOS tooling.** Newer skills are evidence-gated with accurate CLI contracts; older "unified" skills supersede broadly but are code-dump style with some inaccurate snippets (see §5).
5. **Process skills hard-gate each other.** brainstorming's terminal state is writing-plans; TDD's iron law; systematic-debugging's 4 phases with the 3-failures = architecture-question rule.

## 4. Family reviews — distilled findings

### 4.1 Apple frameworks (55 kits + 20 Swift/SwiftUI + 12 unified + 16 tooling = Lane A, 103)

- **Load-bearing five:** `app-intents` (7 system surfaces), `activitykit` (full APNs payload contract), `swift-concurrency` (isolation triage used by nearly every other skill), `cloudkit` (end-to-end sync incl. SwiftData), `storekit` (full purchase lifecycle).
- **Boundary splits to respect:** coreml (inference) vs apple-on-device-ai (conversion/selection) · cryptokit (primitives) vs swift-security (storage/lifecycle) · core-data vs swiftdata (coexistence) · authentication vs swift-security · pencilkit vs paperkit · core-bluetooth vs accessorysetupkit · app-store-review (compliance) vs app-store-optimization (strategy) · activitykit/widgetkit/push-notifications (notification surfaces).
- **Gates:** entitlement/Apple-approval — browserenginekit, carplay, financekit, sensorkit, energykit, weatherkit, permissionkit, musickit app service, critical alerts. Physical device required — BLE, DockKit, SensorKit, push, Metal, CarPlay, AlarmKit. Beta-flagged (re-verify vs docs) — appmigrationkit, audioaccessorykit, energykit, relevancekit, paperkit, metrickit, Swift 6.4/Xcode 27 corners.
- **Build-optimization is a real pipeline:** `xcode-build-orchestrator` → `xcode-build-benchmark` (measure) + three recommend-only analyzers (`xcode-compilation-analyzer`, `xcode-project-analyzer`, `spm-build-analysis`) → **user approval gate** → `xcode-build-fixer` (the only applier) → re-benchmark. Shared artifacts in `.build-benchmark/`. Never invoke the fixer directly.
- **Performance routing chain:** `ios-performance-debug` is the triage umbrella (its CLI snippets are less accurate than the specialists) → `debugging-instruments` (LLDB/Instruments/hangs) · `ios-memgraph-analysis` (leaks/heap) · `ios-ettrace-performance` (launch sampling) · `swiftui-performance` (hitching) · `metrickit` (production telemetry).

### 4.2 MengTo web family (131 skills + 8 core web = Lane B, 139)

- **The expected chain:** `mengto-design-first-ui-prompting` (spec) → `mengto-build-awwwards-quality-sites` (master build; must name one theme skill + library skills) → effect/library skills → `mengto-test-playable-web-games` (games) → `mengto-iterate-until-verified` / `mengto-audit-verify-explain-grade-5` → `mengto-audit-reference-originality` → `mengto-publish-project-to-github`. `mengto-web-technique-to-skill` is the quality constitution (mechanism-vs-staging, numbers-not-adjectives, 9-step browser verification).
- **Taxonomy:** pages/conversion 5 · theme/layout systems 28 · library guides 7 (gsap, tailwindcss, threejs, unicorn-studio, matterjs, cobejs, vantajs) · animation/scroll/CSS effects 31 · 3D/WebGL + cursor 15 · games 21 · assets/media 5 · writing/social 2 · capture/publishing 5 · method/meta 12.
- **Load-bearing:** web-technique-to-skill, iterate-until-verified, build-awwwards-quality-sites, the two audits, build-threejs-scroll-worlds (309 lines, carries scroll-conductor.js). Thin micro-prompts (marquee-loop at 21 lines) are still routable one-shots.
- **Core web anchors:** `ui-ux-pro-max` (heaviest skill in the library), `modern-web-guidance` (run `npx -y modern-web-guidance@latest` FIRST for HTML/CSS/JS), `threeui-reference` (needs `~/Projects/threeui` checkout), `pop-motion` (read reference-gallery.md before coding), `frontend-design` (aesthetic direction, anti-slop bans).
- **Watch:** three near-duplicate scroll-storytelling variants — route on each skill's own "Use When" text.

### 4.3 Research & agent tooling (Lane C, 18)

- **Depth ladder:** `parallel-deep-research` (hosted, auth+balance; on ANY failure auto-falls back) → `deep-research-free` (zero-auth default) → `deep-research` (heavyweight evidence-ledger pipeline). `firecrawl-deep-research` only with `FIRECRAWL_API_KEY`.
- **GitHub:** `github-deep-research` degrades to plain `gh` CLI (on this machine gh is authed as DXv3; the MCP trio is unavailable). `swarm-github-research` is a worked composition example, not a starting point.
- **KB pair (born during this build):** `kb-collection-query` (preferred — kb-waterhole MCP tools first, shim fallback, every claim carries its record ID, stale numbers marked `[verify live]`) and `waterhole-ask` (same KB, invocation-ladder + measured FTS5 syntax notes; shim serves an OLDER copy — DB authoritative). Both read-only forever.
- **Fetch:** `agent-reach` is the MUST-USE 15-platform router (zero-config: Exa via mcporter, r.jina.ai, gh, yt-dlp). The inference.sh trio (`agent-browser`, `agent-tools`, `web-search`) needs a paid infsh account.
- **Sessions:** `continue-claude-work` (bundled extractor; resumes execution) vs `chat-archaeologist` (grep/jq triage, finish/scrap verdicts).

### 4.4 Process/meta + ship (Lanes D/E/F, 15)

- **Pipeline spine:** `using-superpowers` (≥1% relevance → invoke) → `brainstorming` (hard gate: approved design before code) → `writing-plans` (bite-sized TDD tasks) → `executing-plans` / `test-driven-development` → `systematic-debugging` (root cause first; 3+ failed fixes = question the architecture) → `ship-it` (5 phases, ROI ranking, reads `~/SYSTEM-RULES.md` + `~/SYSTEM-STATE.md` first) → `progress-report`.
- **Meta:** `skill-workflow` (book-club recommender for "which skills chain"), `find-skills` (external discovery, ≥10-query exhaustion + parts-not-packages synthesis), `skill-dashboard` (prebuilt catalog — never `find` the library), `chat-pattern-miner` (chats → DRAFT hooks/commands/rules; drafts only, state at `~/Projects/chat-mining/INDEX.md`), `macos-gui-automation` (cliclick + Accessibility permission).

## 5. Defect ledger (found in the review, all dispositioned)

| # | Finding | Disposition |
|---|---|---|
| 1 | 18 skills lack `name:` frontmatter | Harmless — load by directory name. Logged in COVERAGE.md. |
| 2 | `ios-swift-development` is a stub (truncated code) | Router routes to `ios-fullstack` instead. |
| 3 | `ios-performance-debug` CLI snippets less accurate than specialists | Router uses its triage flowchart only; details from specialists. |
| 4 | `skill-workflow` references skills outside the library (chain-orchestrator, code-doctor, context-surfacer, 12-factor-agents) | SKILL.md Lane E note names every outside reference + substitutes. |
| 5 | `clipboardlux-macos-debugging` is a single-app case history (macOS 27 beta) | Router flags it never-general. |
| 6 | Credential gates undocumented | Full gate table in SKILL.md (infsh, FIRECRAWL_API_KEY, parallel-cli, ELEVENLABS_API_KEY, Azure MCP, entitlements, local binaries/checkouts). |
| 7 | `xcode-project-setup` executes a bundled Swift script against real .pbxproj | Routed as approval-gated, "the only applier of project-file changes". |
| 8 | Library mutated mid-build (3 new skills) | Caught by the routing test; all read and routed. Drift doctrine in §8. |

## 6. The orchestrator specification (summary)

The executable router is `SKILL.md` (the lane routers carry all 275 names — this section records the architecture, not the roster).

1. **Operating contract (8 rules).** Repo root = write boundary; read-only outside. Never move/delete/rename during recon. Never read/print/index secrets. Evidence log on every inspection. Never claim uninspected access. Stop-and-show before anything hard to reverse. Small reversible batches, build+test each. Ask only on architecture/data-safety/permissions/cost; otherwise default-and-document.
2. **Orientation.** `~/SYSTEM-STATE.md` authoritative (add `~/SYSTEM-RULES.md` for ship work); skill lookup via `SKILLS-CATALOG.json` / `~/bin/skills-indexer --query`, never `find`; Xcode 27 beta needs the DEVELOPER_DIR check.
3. **Pipeline (9 stages):** Contract → Orient → Recon (read-only, artifacts to `docs/agent-audit/` in the target repo) → Design & plan (brainstorming → writing-plans hard gate) → Build in batches (TDD; declare files/behavior/tests/risks before editing) → Verify (systematic-debugging on any failure; lane verifiers; browser/visual checks at 1440/390px) → Adversarial review (his Prompt-5 checklist + lane audit skills) → Ship (lane-specific: ios-release-polish → app-store-review → ASO / mengto-publish-project-to-github / ship-it phases 4–5) → Handoff (progress-report, SYSTEM-STATE update, next-3-actions).
4. **Lanes:** A Apple 103 · B Web 139 · C Research 18 · D Ship 4 · E Pipeline/meta 10 · F Host 1. Every skill in exactly one lane; disambiguation matrix arbitrates overlaps (kit vs unified, orchestrator-vs-fixer, ladder order, browser-automation routing by target).
5. **ZCode execution notes:** invoke via Skill tool; ONE subagent at a time (sequential dispatch); dynamic workflows for large fan-outs; rendered deliverables pass the matching visual-judge agent on rendered PNGs; file generation via the documents/presentations/spreadsheets/pdf plugins.
6. **Stop conditions:** writes outside the boundary, deletions/moves, secrets/signing, purchases, architecture reversals. Everything else: default-and-document, keep moving.

## 7. Verification log (evidence, including the failures)

Four iterations of the routing test, each catching something real:

1. **Run 1 (backticked tokens only):** 96/272 "routed" — extractor bug; kit and mengto category lists are deliberately plain text. False alarm, test rewritten.
2. **Run 2 (plain-text tokens):** 261/272 — mixed bag: 10 false misses from trailing punctuation on list-final names (".\" captured into tokens) + **1 genuine miss: `xcode-project-setup`**. Fixed the skill (routed, approval-gated); fixed the extractor (strip trailing punctuation). Lane counts corrected 104→103, 138→139.
3. **Run 3 (as `verify-coverage.sh`):** 272/274 — the script caught **library drift**: `chat-pattern-miner` and `waterhole-ask` existed on disk but were absent from the session's initial sweep. Both read and routed (Lane C / Lane E); counts updated.
4. **Run 4:** 274/275 — third mid-session addition `kb-collection-query`. Read, routed as the preferred KB router in Lane C. **Final: 275/275, exit 0.**

Also performed: catalog rebuild via `~/bin/skills-indexer` (743 skills; skill-orchestrator registered under `agents_canonical`); COVERAGE.md regenerated at 275 rows with the verification section.

## 8. Maintenance protocol

After ANY change to the library (add, remove, rename, edit a name/description):

1. `~/bin/skills-indexer` — rebuilds the catalog, updates `~/SYSTEM-STATE.md`.
2. Regenerate `COVERAGE.md` (mechanical: one row per skill) and update lane counts in `SKILL.md`.
3. `~/.agents/skills/skill-orchestrator/verify-coverage.sh` — must print `routed: N/N` and exit 0. A new skill that fails this test is a routing gap, not a test problem — route it, then re-run.
4. Route new skills by reading them first (never blind-route from the name), then state lane membership so the counts still sum.

**Drift doctrine:** the library grows without notice (three additions in one afternoon). The test, not memory, is the source of truth for "everything is reachable." Run it at the start of any session that extends the router.

## 9. Reversibility

Everything shipped this session is additive: one new directory (`~/.agents/skills/skill-orchestrator/`, 4 files) plus the indexer's own catalog rebuild. No existing file was moved, renamed, or edited. Full revert: delete the directory, re-run `~/bin/skills-indexer`.

---

## 10. Upgrade v2 — human-only lanes + AGENT-BRIEF (2026-09-26)

**Source research:** `~/Documents/research/github-skill-orchestration-dna-2026-09-26.md` (skill orchestration DNA/RNA). The report CONFIRMED the orchestrator against Addy's phase tree + wshobson's patterns + mattpocock's triage state machine and named exactly two extensions it lacked — both shipped here as one reversible batch (git baseline `01a5125` in `~/.agents/skills`).

**1. Human-only lane attribute (`disable-model-invocation`).** Triage's discipline: some skills are human-summoned only; an assigner that auto-fires them from description matching breaks its own contract. Added to SKILL.md: the route-time rule (check frontmatter for `disable-model-invocation: true` + the register before invoking; if marked, name the `/command` instead of invoking), a seeded human-only register, and inline `HUMAN-ONLY` annotations on the three affected lane-router entries — `chat-pattern-miner` (E; drafts-only contract), `custom-brainstorm-storm` (C; expensive deliberation), `clipboardlux-macos-debugging` (A; single-app case history). Zero library skills carry the frontmatter flag today; the register seeds from their own documented contracts and grows as skills adopt the flag.

**2. AGENT-BRIEF (durable work order).** Triage's AGENT-BRIEF.md reference, adapted: at the end of Stage 4 (design approved, before the first build batch) the orchestrator writes `<project-root>/AGENT-BRIEF.md` — objective, constraints (write boundary, secrets, batch discipline, task-specific), skills-to-load with full paths, verify gate (exact commands + observable PASS criteria), out-of-scope. The executing agent (same session later, a subagent, or a fresh session) reads the brief instead of re-deriving the plan. Rules: append-only, gate checked off with evidence paths, outcome appended at Stage 9, subagents receive their slice as the prompt. Pipeline table rows 4/5/9 hook into it; the frontmatter description advertises it.

**Library drift handled in the same batch:** the routing test was red at baseline — 275/289. Fourteen skills had landed since 2026-09-21 (9 `mengto-3d-*` + `img2threejs` + `text-to-cad` + the two slop-audit skills + `codex-gpt-image-2-5-flare`). All fourteen read (frontmatter) and routed into Lane B: method/meta 12→14, 3D/WebGL & cursor 15→25, assets/media 5→6, new fabrication/CAD entry (1). Lane B 139→153; total 289. New dispositions: `img2threejs` (image → procedural Three.js, 4.1K words) in 3D/WebGL; `text-to-cad` in a new fabrication entry flagged outward-facing-RFQ-confirm-first.

**Verification:** `verify-coverage.sh` → `routed: 289/289`, exit 0. Lane sums: A 103 · B 153 · C 18 · D 4 · E 10 · F 1 = 289. Test itself unchanged (existing pipeline intact — the upgrade touched SKILL.md/MASTER-SPEC.md/COVERAGE.md only).
