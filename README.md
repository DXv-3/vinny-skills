# Vinny Skills — Entire Skill Index

[![Skills](https://img.shields.io/badge/skills-592-blue)](./catalog.json) [![Manus](https://img.shields.io/badge/manus-31%20internal-orange)](./manus-audit.json) [![Indexer](https://img.shields.io/badge/indexer-0.003s-green)](./skills-indexer) [![Claude Marketplace](https://img.shields.io/badge/marketplace-claude--code-purple)](./.claude-plugin/marketplace.json)


> **592 skills** across **14 local sources** + **35 Manus internal** + **5 Manus profiles** — one searchable registry. Generated 2026-08-20.

`cat catalog.json` in 0.003s instead of `find ... SKILL.md` in 120s. For agents, by agents.

## Stats

| Source | Count | Path |
|--------|-------|------|
| `agents_canonical` | 141 | `~/.agents/skills/` |
| `agents_archive` | 110 | `~/.agents/skills-archive/` (inferen-sh, disabled) |
| `opencode` | 3 | `~/.config/opencode/skills/` |
| `saaas_primary` | 14 | `~/Documents/05_PERSONAL/SAAAS/skills/` |
| `saaas_toto` | 14 | `~/Documents/01_ACTIVE/toto-ecosystem/.../SAAAS/skills/` |
| **Manus internal** | 35 | 5 LevelDB profiles (only 2 common) |
| **Manus accounts** | 5 | 5 gmail accounts (redacted here; full mapping in local SYSTEM-STATE.md) |

**Total cataloged:** `282 + 35 manus internal + 20+ AGENTS.md`

## For Agents (Read This First)

**Do NOT run `find ... SKILL.md` — use the catalog:**

```bash
cat catalog.json | jq '.by_source.agents_canonical[]'   # list canonical
cat catalog.tsv | grep -i swiftui                        # 0.01s search
./skills-indexer --query manus                          # 0.03s fzf-style
./bin/skills-indexer --cat | jq .summary                # stats
```

Rebuild after adding skills: `./skills-indexer` or `~/bin/skills-indexer` (auto-updates `SYSTEM-STATE.md`).

## For Humans

### Install — any agent that reads SKILL.md

SKILL.md is a cross-harness format (opencode, Grok, Gemini CLI, Antigravity, Kimi, qwen-code, Codex, Claude Code all read it). Pick yours:

```bash
# Universal bridge (auto-detects 70+ agents) — works for everything
npx skills add DXv-3/vinny-skills --skill skill-dashboard
npx skills add DXv-3/vinny-skills --all          # bulk

# Or just clone and symlink into your agent's skills dir
git clone https://github.com/DXv-3/vinny-skills.git
ln -s $(pwd)/vinny-skills/skills/* ~/.agents/skills/     # opencode/Grok/Gemini convention

# Claude Code marketplace (optional — only if you use it)
/plugin marketplace add DXv-3/vinny-skills
```

### Skill Dashboard

Local-first registry + Manus sync. See `skills/skill-dashboard/SKILL.md`.

```bash
cat INVENTORY.md              # human view (38K)
cat index-lite.json | jq      # web search index
cat marketplace.json | jq .marketplace.plugins
```

## Manus Divergence (Why This Repo Exists)

5 browser/app profiles (17M DesktopApp, 10M ChromeBeta, 7.5M Comet, 3.7M ChromeDefault, 2.5M BetaP2) share only 1/35 (`github-gem-seeker`) truly common to all 5; `manus-config` in 4/5. Example:

- DesktopApp only: `codebase-patdown`, `gmail-paper-list-export`
- Comet only: `cinematic-scroll-experiences`, `portable-ai-work-state`, `manus-api`
- ChromeBeta only: `skillx`, `ui-ux-pro-max`
- ChromeDefault only: `startup-competitor-battlecards`

Repo includes `manus-audit.json` with full matrix. Fix via `skills-sync` (V2 in spec).

## Structure

```
vinny-skills/
├── catalog.json              # 282 skills, machine-readable (0.003s)
├── catalog.tsv               # grep-friendly
├── INVENTORY.md              # 38K human view
├── index-lite.json           # web search index (like majiayu)
├── stats.json                # counts + version
├── marketplace.json          # Claude Code marketplace manifest
├── .claude-plugin/marketplace.json  # native marketplace
├── skills-indexer            # 0.3s rebuild, 0.03s query (chmod +x)
├── bin/skills-indexer        # same, in bin/
├── skills/skill-dashboard/   # SKILL.md + references/dashboard-spec.md
├── agents-md/                # 16 AGENTS.md files (Octopus protocol etc)
├── tier-mapper/              # Manus API v2 (32 endpoints) + sandbox routes + platform tiers
├── provenance/               # .skill-lock.json — GitHub source + hash per archived skill
├── search.html               # zero-build web UI (works on GitHub Pages)
├── manus-audit.json          # 5 profiles × 35 skills divergence matrix
```

## Rebuild Locally

```bash
~/bin/skills-indexer            # rebuild ~/.agents/* catalog
cp ~/.agents/SKILLS-CATALOG.json ./catalog.json && cp ~/.agents/SKILLS-CATALOG.tsv ./catalog.tsv
git add -A && git commit -m "chore: reindex $(date +%Y-%m-%d)" && git push
```

## Sources

- `inferen-sh/skills` (via `.skill-lock.json` v3) — archived but preserved
- `GoogleChrome/modern-web-guidance` (via `skills-lock.json`)
- Apple framework skills (ActivityKit → WidgetKit), Swift, Xcode, etc.
- SAAAS z-ai-web-dev-sdk (ASR/LLM/VLM/TTS/docx/pdf/pptx/xlsx)
- Manus LevelDB: `Library/Application Support/Manus/IndexedDB` + Chrome/Comet variants
- Tier map: `api_v2_official.json` (32 endpoints) + `sandbox_api_thirdparty.json` (9 routes)

## License

MIT — see `LICENSE`

---

*Generated by `~/bin/skills-indexer` 2026-08-20. See `SYSTEM-STATE.md` § SKILL SYSTEM for canonical state.*


## Honest Gaps (self-review 2026-08-21)

- **970 additional SKILL.md exist locally** outside this catalog: Gemini plugins (70), Grok bundled+plugins (76), qwen-code (11), kimi-cli (3), daimon/kimi-desktop backup (66), jcode (121), codex .tmp plugins (608), ai-job-search project (8), cognee demos (3). These are third-party/vendor-bundled or temp caches — excluded deliberately. Add via `skills-indexer` ROOTS if needed.
- **AGENTS.md collection not in repo** — 20+ files live at `~/Projects/*/AGENTS.md`, mostly Octopus protocol. Not skill data.
- **`.skill-lock.json` provenance omitted** — source GitHub URLs for the 110 archived inferen-sh skills. In `~/.agents/.skill-lock.json` locally.
- **tier-mapper API maps referenced but not committed** — see `~/Downloads/manus-mega-deliverables/tier-mapper/` (32 official endpoints + 9 sandbox routes).
- **239/267 descriptions truncated to ~250 chars** — full text lives in each SKILL.md.
- Original claim "only 2 common" corrected: only `github-gem-seeker` is in all 5 profiles; `manus-config` in 4/5.
