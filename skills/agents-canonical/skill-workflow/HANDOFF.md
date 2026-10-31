# Handoff: skill-workflow Skill — Outsider Validation

## Context

An agent skill called `skill-workflow` was just created at `~/.agents/skills/skill-workflow/SKILL.md` (symlinked into `~/.claude/skills/`). The creator wants an **outsider's validation** — does this skill make sense, does it fit the ecosystem, is it fine to proceed with?

## What Was Built

A **meta-skill** that recommends which skills to chain together for any given task. It:

1. **Scans** every available skill across `~/.agents/skills/`, `~/.claude/skills/`, and MCP config
2. **Reads the current conversation** to understand context, stage, and constraints
3. **Runs a "book club"** of 7 analytical personalities that debate and converge (Orchestrator, Skeptic, Connector, Pragmatist, Visionary, Gatekeeper, Architect)
4. **Assembles** a workflow: ordered skill phases with rationale, parallelization, hard gates, fallbacks
5. **Delivers** the workflow with confidence — no hedging
6. **Handles gaps** — if no skill exists, the Architect personality plans and builds it (never a dead end)

Key trigger: the user said *"SCAN THE SKILLS AND THEN SUGGEST A WORKFLOW OF SKILLS THAT NEED TO BE APPLIED AT THAT MOMENT"* and *"if nothing works... plan out and build those skills — not dead ends, just a little bit more work."*

## What Needs to Be So (Validation Checklist)

For the creator to confidently proceed, an outsider should validate:

### 1. The skill fits the ecosystem
- [ ] It follows the same frontmatter format (name, description, triggers) as other skills
- [ ] It references existing skills correctly (chain-orchestrator, find-skills, brainstorming, etc.)
- [ ] It doesn't duplicate what `chain-orchestrator` already does, but complements it (chain-orchestrator is for full-lifecycle builds; this is for "what skills to use right now" in any context)
- [ ] It doesn't duplicate `find-skills` (that's for discovering new skills on the open market; this is for sequencing known skills)
- [ ] It respects the `using-superpowers` hierarchy (user instructions > skills > defaults)

### 2. The 7-personality model makes sense
- [ ] The panel of 7 personalities covers all necessary analytical angles
- [ ] The Architect personality (gap → build) is a meaningful addition, not redundant with the Skeptic
- [ ] The convergence model (debate → align) produces actionable output, not analysis paralysis
- [ ] No personality has veto power — they converge (avoids endless debate)

### 3. The Gap → Build mindset is sound
- [ ] Treating missing skills as "a little bit more work" rather than dead ends is the right framing
- [ ] The 5-step gap process (check sibling → decompose → plan → build → wire in) is complete and practical
- [ ] The Architect's role in the example (recognizing that existing skills cover the SEO gap) demonstrates the skill works

### 4. The workflow format is usable
- [ ] The PHASE structure (name, skills, why, what, confidence) is clear and actionable
- [ ] The hard-gate naming, parallelization, and fallback rules are practical
- [ ] The example (SEO landing page) demonstrates a realistic use case end-to-end

### 5. The integration points are correct
- [ ] The skill is invoked via the `Skill` tool with name `skill-workflow`
- [ ] The symlink between `~/.claude/skills/` and `~/.agents/skills/` is the established pattern
- [ ] The SYSTEM-STATE.md has been updated to record the new skill

## What the Creator Is Going to Try to Do Next

1. **Trigger `skill-workflow`** in the current SEO landing page context
2. **Expect it to scan all skills** and run the 7 personalities on the SEO task
3. **Expect a workflow recommendation** — which skills to chain, in what order, what's included/excluded
4. **If it identifies a gap** (e.g., no dedicated SEO skill), expect the Architect to plan + build it
5. **Proceed with that workflow** to actually build the Kage-style SEO landing page

## What "Fine to Do" Means Here

- The skill doesn't break any existing system (it's additive, non-destructive)
- It follows established conventions (frontmatter, directory structure, symlink pattern)
- It complements (not competes with) existing orchestration skills
- The "gap to build" philosophy is consistent with the `find-skills` skill's GAP → `npx skills init` pattern
- It's safe to invoke in a new chat session for validation — the worst case is someone says "this overlaps too much with chain-orchestrator" and we refine it

## File Locations

- **Skill file:** `~/.agents/skills/skill-workflow/SKILL.md`
- **Symlink:** `~/.claude/skills/skill-workflow`
- **State record:** `~/SYSTEM-STATE.md` (NEW SKILLS section)
- **System rules:** `~/SYSTEM-RULES.md` (followed — checked before creating)

---

## UPDATE: skill-workflow Applied — YouTube Ingestion Optimization

After creating `skill-workflow`, the creator applied it to a real task: **efficiently ingesting the @GithubAwesome YouTube channel (199 videos) into the knowledge base.**

### What the book club found

| Personality | Take |
|---|---|
| **Orchestrator** | "The existing `youtube-ingest` + `universal-pipeline` can do this, but it's slow (~50 min for 199 videos)." |
| **Skeptic** | "The existing pipeline depends on a third-party proxy that gets 429'd. Risky for 199 videos." |
| **Connector** | "`drpwchen/ytscribe` on GitHub is the better tool — subtitles-first, no proxy, local Whisper fallback." |
| **Pragmatist** | "ytscribe subtitles-only mode = just downloading caption files. Near-zero compute. Perfect for tech channels." |
| **Visionary** | "The end state is: 199 videos filed in `~/knowledge-base/items/youtube:GithubAwesome/` and searchable via context-surfacer." |
| **Gatekeeper** | "No paid APIs. No GPU required. No video downloads. Subtitles-first is the only acceptable approach." |
| **Architect** | "ytscribe doesn't file into knowledge-base. Gap: need a bridge script. Build it (5 lines, just file I/O)." |

### What was built

**`bridge_to_kb.py`** — `~/.claude/skills/youtube-ingest/scripts/bridge_to_kb.py`
- Converts ytscribe Markdown+YAML output → knowledge-base JSON format
- Incremental: skips already-filed items
- Compute: negligible (file I/O only, no LLM/transcription/video)

### The EFFORTLESS + SMART workflow

```bash
# 1. Install ytscribe (one command)
pip install git+https://github.com/drpwchen/ytscribe.git

# 2. Fetch subtitles (fast, ~5-10 min for 199 videos, zero compute)
ytscribe https://www.youtube.com/@GithubAwesome -o ~/youtube-ingest/GithubAwesome/transcripts

# 3. Bridge to knowledge-base (just file I/O, skips existing)
python3 ~/.claude/skills/youtube-ingest/scripts/bridge_to_kb.py \
  ~/youtube-ingest/GithubAwesome/transcripts GithubAwesome

# 4. Build unified FTS5 index
python3 ~/.claude/skills/universal-pipeline/scripts/ingest.py --build-index

# 5. Query (context-surfacer now surfaces the data)
python3 ~/.claude/skills/universal-pipeline/scripts/query.py "GitHub Trending" --source youtube
```

### Compute profile

- **Subtitles download**: Network I/O only, ~5-10 min for 199 videos
- **Whisper fallback**: Only for videos without captions (rare for tech channels); uses GPU only when `--whisper` flag is passed
- **Bridge script**: File I/O only, no LLM, no transcription
- **Index build**: One-time SQLite FTS5 indexing (~1 min)
- **Query**: Instant FTS5 search

The compute mark is barely visible. Most tech YouTube channels (including @GithubAwesome) have auto-generated captions, so subtitle download handles 99% of the work.

---

*Hand this to any outsider and ask: "Does this skill make sense? Should we proceed with triggering it?"*
