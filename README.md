# Vinny Skills — Entire Skill Index

[![Skills](https://img.shields.io/badge/skills-782%20unique-blue)](./catalog.json) [![Manus](https://img.shields.io/badge/manus-31%20internal-orange)](./manus-audit.json) [![Indexer](https://img.shields.io/badge/indexer-0.003s-green)](./skills-indexer) [![Claude Marketplace](https://img.shields.io/badge/marketplace-claude--code-purple)](./.claude-plugin/marketplace.json)


> **782 unique skills** (1022 entries incl. cross-source duplicates) across **10 local sources** + **35 Manus internal** + **5 Manus profiles** — one searchable registry. Generated 2026-10-31.

`cat catalog.json` in 0.003s instead of `find ... SKILL.md` in 120s. For agents, by agents.

## Stats

| Source | Count | Path |
|--------|-------|------|
| `agents_canonical` | 721 | `~/.agents/skills/` |
| `agents_archive` | 107 | `~/.agents/skills-archive/` (inferen-sh, disabled) |
| `opencode` | 5 | `~/.config/opencode/skills/` |
| `gemini_plugins` | 59 | `~/.gemini/config/plugins` |
| `gemini_antigravity` | 8 | `~/.gemini/antigravity-ide/plugins` |
| `grok_user_skills` | 13 | `~/.grok/skills` |
| `grok_installed_plugins` | 38 | `~/.grok/installed-plugins` |
| `jcode_mirror` | 10 | `~/.jcode/skills` |
| `daimon_backup` | 59 | `~/VINNYOS-BACKUPS/.../kimi-desktop-data` |
| `vinnyos_sync` | 2 | `~/VinnyOS-Sync/skills` |
| **Manus internal** | 35 | 5 LevelDB profiles (only 2 common) |
| **Manus accounts** | 5 | 5 gmail accounts (redacted here; full mapping in local SYSTEM-STATE.md) |

**Total cataloged:** `1022 (782 unique) + 35 manus internal + 20+ AGENTS.md`

Gone since the 2026-08-21 index: `saaas_primary`, `saaas_toto`, `pep_engine`, `vinnyos_skills` (paths no longer exist on the machine; their entries were dropped with this reindex).

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
├── catalog.json              # 1022 entries / 782 unique, machine-readable (0.003s)
├── catalog.tsv               # grep-friendly
├── INVENTORY.md              # human view
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

*Generated by `~/bin/skills-indexer` (v2.1) — latest rebuild 2026-10-31. See `SYSTEM-STATE.md` § SKILL SYSTEM for canonical state.*


## Honest Gaps (self-review 2026-10-31)

- The 2026-08-21 gaps below are **resolved by this reindex**: Gemini/Grok/daimon/jcode sources were added to `skills-indexer` v2 ROOTS and are now in the catalog (10 active sources).
- **Full skill content now included (2026-10-31):** `skills/agents-canonical/` (718 skills), `skills/agents-archive/` (107), `skills/grok-user-skills/` (13), `skills/opencode/` (5) — the real SKILL.md files, installable via `npx skills add DXv-3/vinny-skills`. Vendor mirrors (Gemini/Grok/jcode/daimon third-party copies) stay index-only to avoid republishing third-party content under this MIT license.
- **AGENTS.md snapshots under `agents-md/` are point-in-time** from 2026-08-21; most source paths have since been removed from the machine.
- **`.skill-lock.json` provenance omitted** — source GitHub URLs live in `~/.agents/.skill-lock.json` locally.
- **tier-mapper API maps referenced but not committed** — see `~/Downloads/manus-mega-deliverables/tier-mapper/` (32 official endpoints + 9 sandbox routes).
- **239/267 descriptions truncated to ~250 chars** — full text lives in each SKILL.md.
- Original claim "only 2 common" corrected: only `github-gem-seeker` is in all 5 profiles; `manus-config` in 4/5.

## Changelog

- **2026-10-31 (v2.1):** full reindex — 592→1022 entries (782 unique); `agents_canonical` 141→721; sources dropped (paths gone): `saaas_primary`, `saaas_toto`, `pep_engine`, `vinnyos_skills`; `jcode_mirror` 121→10; `daimon_backup` 66→59. Marketplace manifests + index-lite + stats regenerated.
- **2026-08-21 (v2.0.0):** full index (592 skills, 14 sources), provenance, agents-md, tier-mapper, Pages search UI.
