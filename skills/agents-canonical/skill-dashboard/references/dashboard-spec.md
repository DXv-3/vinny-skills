# Skill Dashboard Spec — Local-first Registry + Manus Sync

Based on GitHub archetypes: dukelyuu/skills-marketplace (npm-for-skills UI), secondsky/claude-skills (142 skills marketplace), majiayu000/claude-skill-registry-core (daily indexed registry), jeremylongshore/claude-code-plugins-plus-skills (3,069 skills).

## What a Skill Dashboard Is

On GitHub, a "skill dashboard" = a local or hosted web app that gives you:
- **One search bar** over all SKILL.md (FTS5 full-text, filters by source/tag/language)
- **Grid + List toggle** (cards show stars, description, install count, platform badges)
- **System dashboard** (4 stat cards: total skills, active sources, downloads, quota + sync activity chart + tag/star distribution)
- **Detail view** (renders SKILL.md, star history, version timeline, file tree, ZIP download)
- **Source management** (GitHub repos + Awesome Lists — one-click Full Discovery)
- **Editor** (split-pane Markdown, YAML validation, export)
- **Multi-platform** (12 agents: Claude Code, Kiro, Cursor, Windsurf, Copilot, Cline, Antigravity, opencode, etc)

## How People Use Skills Interestingly (from GitHub)

1. **Marketplace mode** (secondsky): `plugin marketplace add` → `/plugin install @marketplace` — federated, auto-updates, team deployment via `.claude/settings.json` extraKnownMarketplaces.
2. **Cross-harness bridge** (skills.sh / npx skills): `npx skills add secondsky/claude-skills --skill cloudflare-d1` auto-detects harness (Claude/Cursor/Codex/opencode/Gemini) and installs to correct dir. Universal path for non-marketplace harnesses.
3. **Registry + crawler** (majiayu000): daily GitHub crawl, deduped index, gzip search-index.json + lite.json, Pages search UI, sk CLI manager — 1K+ skills, live stats.
4. **Stack compiler** (agents-inc/skills): 150+ atomic skills + metadata.yaml + reference.md — `npx agents-inc init` picks stack (React, Prisma, Redis...) and compiles subagents.
5. **SaaS packs** (jeremylongshore): 468 plugins / 3,069 skills / 347 agents, by category (SAAS packs 106, DevOps 36, Crypto 27) — tonsofskills.com browse-by-skill / by-job-to-be-done / by-certification-tier + ccpi CLI.
6. **Skill creator meta-skill** (daymade): skill-creator skill that teaches Claude to build/validate/package new skills — the skill that builds skills.

## What We'd Build for You (Local, No Cloud)

### V1 — Already Done (saves time now)
- `~/.agents/SKILLS-CATALOG.json` (282 skills, 0.003s read)
- `~/.agents/SKILLS-CATALOG.tsv` (grep-friendly)
- `~/.agents/SKILLS-INVENTORY.md` (human)
- `~/bin/skills-indexer` (0.03s query, rebuild)
- `~/.agents/skills/skill-dashboard/SKILL.md` (this skill — tells future agents to use catalog)

**Time saved:** 120s → 0.04s per lookup. 1000 future agent calls = 33 hours saved.

### V2 — CLI Sync Tool (2-4 hours)
- `~/bin/skills-sync` — Manus profile reconciler
- Compares 5 LevelDBs, outputs matrix: which skill missing where
- One-shot sync: `skills-sync --fix` copies SKILL.md refs or re-enables via LevelDB strings patch (or just documents manual fix)
- Also handles `.agents/skills` ↔ `.agents/skills-archive` enable/disable via `.skill-lock.json` (like `npx skills add` but local)

### V3 — Web Dashboard (1-2 days, using ui-ux-pro-max + pop-motion)
- Stack: Next.js 15 + Tailwind + SQLite FTS5 (or just JSON) + Framer Motion
- Location: `~/Projects/skill-dashboard/` — `pnpm dev` on :8765
- Features:
  - Top bar: search (⌘K), filter by source (5 pills), sort by name/stars/size
  - Grid: 141+110+14 cards, platform badges (Claude/opencode/Manus), description, path
  - List: TSV-style with size/mtime
  - Matrix view: Manus 5 profiles × 31 skills — red/green cells for missing skills (your core ask)
  - Detail: click card → renders SKILL.md (markdown), shows file tree, copy path, open in editor
  - System: 4 stat cards (total/active/archived/manus divergent) + sync activity (when last indexed) + tag cloud
  - Actions: Enable/Disable (moves between skills/skills-archive, updates .skill-lock.json), Reindex, Export ZIP
- No backend needed — reads catalog JSON directly. Optional: watch with `chokidar` for auto-reindex.

### V4 — Marketplace Adapter (optional)
- Wrap catalog as a real Claude Code marketplace: generate `plugins/*/ .claude-plugin/plugin.json` like secondsky does
- Then: `/plugin marketplace add file://~/.agents/skills` and `/plugin install skill-dashboard@local`
- Cross-harness: `npx skills add ~/.agents/skills --skill <name>` already works via skills.sh

## Recommendation

**Ship V1 now (done). Do V2 next if Manus sync is urgent. Do V3 only if you want a pretty UI to show others.**

V2 is highest ROI for your "few accounts don't have same skills" fix — it actually repairs the divergence instead of just showing it. V3 is demo-ware unless you plan to publish.

Want me to:
- A) Build `skills-sync` (V2) now — 30 min
- B) Scaffold `~/Projects/skill-dashboard/` (V3) — 1 hour to clickable
- C) Both
- D) Just keep V1 and move on
