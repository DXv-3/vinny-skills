---
name: github-deep-research
description: Exhaustive GitHub research — recursive topic following, multi-tool search, commit archeology, issue mining, cross-repo dependency mapping. Leaves NO stone unturned. Use when the user wants comprehensive GitHub discovery for any topic, technology comparison, ecosystem mapping, or "find me every repo that does X." Triggers on "deep github research," "exhaustive github search," "find every repo for X on github," "github ecosystem audit," "map all repos that," or /github-deep-research.
---

# GitHub Deep Research — The Exhaustive Skill

## When to Use

Trigger when the user asks for:
- "Find every repo that does X" or "what repos exist for Y"
- "Deep github research on Z" or "exhaustive github search"
- "Map the github ecosystem for W" or "github audit"
- Technology comparison requiring full landscape mapping
- Cross-repo dependency/connection discovery
- Any request where surface-level `gh search repos` would miss critical findings

Not for: a single repo lookup, "what's the best X" (use regular search), or non-GitHub research.

## Core Principle: Exhaustive by Design

Normal GitHub searches stop at Page 1 of results. This skill treats that as the *starting point*. It uses recursive topic following, dependency-graph reverse-lookup, issue/PR mining, commit archeology, and cross-repo intelligence to ensure nothing is missed.

## Methodology — Phases of Exhaustion

### Phase 0: RESUME & PRIOR-COVERAGE CHECK (mandatory, before any search)

Research sessions die — user concurrency limits kill long chats, crashes happen, the user closes the window. Anything held only in context is lost. Work lives on disk, never only in the conversation. So, before the first query:

1. **Check prior coverage**: read `~/Documents/research/INDEX.md` (maintained by this skill) and scan `~/Documents/research/github-*.md` for this topic or an adjacent one. If a complete report already covers it, present that report and ask the user whether to extend it or deliberately re-run. Do NOT silently re-research a covered topic.
2. **Check for in-flight state**: if `~/Documents/research/github-$TOPIC-state.json` exists, load it, tell the user what was already done, and continue from `next_actions`. Never re-run queries listed in `queries_executed`.
3. **Create both files before the first search** (`mkdir -p ~/Documents/research` first):
   - `~/Documents/research/github-$TOPIC-$DATE.md` — report stub: header, metadata block, empty section skeleton from the Deliverable Format.
   - `~/Documents/research/github-$TOPIC-state.json` — initial state, per the Checkpointing section below.

### Phase 1: QUERY EXPLOSION

Before any search, explode the seed term into a query tree:

1. **Literal synonyms**: exact topic terms, alternate phrasings
2. **Adjacent domains**: related technologies, competing approaches
3. **Tool/library names**: known implementations in the space
4. **Acronyms**: both full form and abbreviations
5. **Inverse angles**: what it's NOT, what it replaces, what replaces it
6. **Creative mashups**: combining with "awesome", "curated", "tracking", "hub"

**Minimum 10 queries per topic.** No ceiling. Use ALL of these search surfaces:

| Surface | Tool | Example |
|---------|------|---------|
| Repo name/description | `gh search repos` | `gh search repos "term" --sort stars` |
| Code content | `gh search code` | `gh search code "import term" language:python` |
| README files | `gh api` | `gh api "search/repositories?q=term+in:readme"` |
| Topics/tags | `gh api` | `gh api "search/repositories?q=topic:term"` |
| Issues | `gh search issues` | `gh search issues "term" --label bug` |
| Commits | `gh search commits` | `gh search commits "fix: term" --sort committer-date` |
| GitHub Ecosystem MCP | `discover_layer` | 6-layer search (capture/fuse/think/act/self/dream) |
| Opportunity Scout MCP | `scout_search` | Cross-layer repo discovery |
| Codebase Memory MCP | `search_graph` | Search indexed repos for related code |

### Phase 2: RECURSIVE EXPANSION

For each discovered repo, DON'T STOP. Expand recursively:

```
Found repo → check its topics → search those topics → check orgs → search those orgs → repeat
```

**Expansion checklist per repo:**
- [ ] `gh api repos/owner/name/topics` → search each topic as new query
- [ ] `gh api orgs/owner/repos` → scan all repos in the org
- [ ] `gh api repos/owner/name/dependents` → who depends on this?
- [ ] Check `package.json`/`Cargo.toml`/`requirements.txt` → what dependencies does it use?
- [ ] `gh search code "import {owner/name}"` → who imports this?
- [ ] Related README mentions: `gh search repos "owner/name" in:readme`
- [ ] Stargazer overlap: `gh api repos/owner/name/stargazers` → what else do they star?

**Stop condition:** When 3 consecutive rounds of expansion yield no new repos meeting the quality threshold (stars > 5 AND pushed within 18 months OR explicitly recommended by community).

### Phase 3: DEEP VALIDATION

For every candidate that passes the surface scan, validate deeply:

| Check | Tool | What It Reveals |
|-------|------|-----------------|
| License | `gh api repos/owner/name/license` | Can you use it? |
| Maintenance | `gh api repos/owner/name` + check `pushed_at` | Is it alive? |
| Issue health | `gh search issues --repo owner/name` | Open/closed ratio, response time |
| Release frequency | `gh api repos/owner/name/releases` | Active development? |
| Community | `gh api repos/owner/name/contributors` | Bus factor? |
| README quality | `github-ecosystem.analyze_repo` | Entry points, dependencies, structure |
| Code quality | `codebase-memory.index_repository` + `query_graph` | Hotspots, complexity, architecture |
| Cross-connections | `codebase-memory.index_repository mode:cross-repo-intelligence` | What else does this connect to? |

### Phase 4: COMPARATIVE MATRIX

Build a comparison matrix across all validated repos:

```
| Repo | Stars | License | Lang | Last Push | Health | Community | Architecture | Risk |
|------|-------|---------|------|-----------|--------|-----------|--------------|------|
```

**Risk assessment categories:**
- **ABANDONED**: No pushes in 12+ months, unresolved issues piling up
- **SOLO**: Single contributor, no forks, no community
- **ALPHA**: Active but pre-1.0, breaking changes frequent
- **STABLE**: Regular releases, clear roadmap, responsive maintainers
- **ENTERPRISE**: Backed by company, SLAs, long-term support

### Phase 5: GAP ANALYSIS & REPORTING

After exhausting all queries and recursions:

1. **Map what was found** — categorize by approach, maturity, language
2. **Identify gaps** — what should exist but doesn't? What's underbuilt?
3. **Surface conflicts** — two repos claiming to do the same thing but disagreeing on approach
4. **Recommend build path** — given the landscape, what should the user build vs adopt?

## Tool Priority Order

For each phase, use tools in this priority (fastest/richest first):

1. `github-ecosystem.discover_layer` — 6-layer scan gives immediate broad coverage
2. `opportunity-scout.scout_search` — cross-layer scored discovery  
3. `gh search repos --sort stars --json` — structured data, sortable
4. `gh api "search/repositories?q=..."` — flexible querying (README, topics, code)
5. `gh search code` — for finding who uses/imports a library
6. `gh search issues` — for issue and PR mining
7. `codebase-memory.search_graph` — for indexed repo code search
8. `github-ecosystem.analyze_repo` — for deep structural analysis
9. `codebase-memory.index_repository` + `query_graph` — for max-depth code analysis
10. `codebase-memory.index_repository mode:cross-repo-intelligence` — for connection discovery

## Search Strategy: The 7-Layer Sieve

Every topic gets searched through these 7 progressively narrower sieves:

| Sieve | Query Pattern | Purpose |
|-------|--------------|---------|
| 1. Broad | `"topic" sort:stars` | Discover the big players |
| 2. Recent | `"topic" sort:updated` | Find active projects missed by stars |
| 3. Niche | `"topic" sort:stars language:rust` (each lang) | Language-specific solutions |
| 4. README-deep | `"topic" in:readme sort:stars` | Find repos that MENTION the topic |
| 5. Topic-tagged | `topic:topic-name sort:stars` | GitHub's own topic system |
| 6. Inverse | `"alternative to topic" OR "topic replacement" OR "better than topic"` | Find competitors |
| 7. Community-curated | `"awesome topic" OR "awesome-list topic" OR "curated topic"` | Hand-picked collections |

Every sieve must be exhausted before moving on. Use `--paginate` or offset-based pagination to go beyond page 1.

## Deliverable Format

Produce a structured report with this exact structure, saved to `~/Documents/research/github-$TOPIC-$DATE.md`. The file is created as a stub at Phase 0 and **appended to after every phase** — Tier entries after Phase 3, the matrix after Phase 4 — so a session killed mid-run leaves a readable partial report, not nothing. When the report is complete, add one line to `~/Documents/research/INDEX.md` (create if missing): `filename | topic | status | date`.

```markdown
# GitHub Deep Research: [Topic]
Generated: [ISO date]
Engine: github-deep-research  
Queries executed: [N]
Repos scanned: [N]
Repos validated: [N]
Search depth: exhaustive (5-phase)

## Executive Summary
2-3 paragraphs of what was found, key themes, and build vs adopt recommendation.

## Tier 1: Primary Repos (top N by quality)
Detailed analysis of each, with:
- Stars, license, language, last push, release cadence
- Architecture overview (from codebase-memory/analyze_repo)
- Community health (issue velocity, contributor count)
- Risk assessment
- Best for: [use case]

## Tier 2: Supplementary Repos
Shorter entries for repos that are useful but not primary.

## Tier 3: Emerging / Niche
New repos (<100 stars) doing interesting things.

## Tier 4: Abandoned but Relevant
Dead repos with valuable code or ideas worth salvaging.

## Comparative Matrix
| Repo | Stars | License | Lang | Health | Architecture | Risk |

## Gaps & Open Questions
What wasn't found, what should exist, what needs more research.

## Build Path Recommendation
Given the landscape: what to adopt, what to build, what to watch, what to avoid.

## Methodology Notes
- Queries executed (list all)
- Searches exhausted vs rate-limited
- Repos analyzed in depth vs surface-scanned
- Limitations (rate limits, private repos, etc.)
```

## Anti-Patterns (Don't Do These)

- ❌ Stop after page 1 of `gh search repos`
- ❌ Use only one search query for a topic
- ❌ Skip recursive topic following
- ❌ Accept star count alone as quality signal  
- ❌ Skip issue/mining for newer repos
- ❌ Ignore abandoned repos (they may have valuable ideas)
- ❌ Forget to check org membership for related projects
- ❌ Skip dependency graph analysis for mature repos
- ❌ Rate-limit yourself by firing 50 parallel `gh` calls — batch smartly
- ❌ Claim "nothing found" without exhausting all 7 sieves
- ❌ Hold research state only in conversation context — sessions get killed mid-run (user concurrency limits, crashes); checkpoint to the state file after every batch so a failed round loses at most one batch
- ❌ Re-research a topic already covered in `~/Documents/research/` without checking INDEX.md first
- ❌ Open multiple heavy research chats at once — concurrent sessions trip the platform's user concurrency limit and kill each other; finish or checkpoint one before starting another

## Rate Limit Management

GitHub's REST API allows ~5000 req/hr authenticated. Plan accordingly:

1. Start with MCP tools (they manage their own rate limits)
2. Batch `gh api` calls using GraphQL where possible (single request = multiple data points)
3. Prioritize high-signal searches first (stars + recency)
4. If rate-limited mid-research: document what was missed, cache results, offer to resume
5. Use `gh auth status` to check authentication before starting
6. Prefer `--jq` with `gh api` to minimize data transfer

## Checkpointing (MANDATORY — no lost work on failed rounds)

Checkpoint to disk after **every phase** and after **every batch of ≤10 queries or ≤10 repos validated**. This is not an optional extra and not only for multi-session runs — long sessions get killed by user concurrency limits, and everything not written to disk dies with the session. A checkpoint is one file write; do it constantly.

State file: `~/Documents/research/github-$TOPIC-state.json`:

```json
{
  "topic": "...",
  "updated_at": "2026-09-21T20:15:00Z",
  "phase": "2",
  "report_path": "~/Documents/research/github-$TOPIC-$DATE.md",
  "queries_executed": ["..."],
  "repos_discovered": ["owner/name"],
  "repos_validated": ["owner/name"],
  "findings": [{"repo": "owner/name", "tier": 1, "stars": 0, "license": "...", "note": "one-line analysis"}],
  "rate_limit_remaining": 4500,
  "next_actions": ["..."]
}
```

Rules:
- Update `updated_at`, `phase`, and `next_actions` on every write. Append to `findings` as repos are validated, so a resumed session inherits the analysis, not just repo names.
- The report file is written incrementally in parallel with the state file (see Deliverable Format).
- If rate-limited or interrupted: the state file documents what was missed — offer the user a resume rather than a restart.

## Multi-Turn Continuation

If a prior session died or the user resumes later: load `~/Documents/research/github-$TOPIC-state.json`, cross-check the report file, and continue from `next_actions`. Never restart a topic from scratch when a state file exists. If the user pastes "Continue the previous task" with no context, this state file is how you reconstruct it.

---

This skill is designed to be loaded by any agent (Claude Code, Kilo, Hermes, Grok, OpenCode). It forces exhaustive GitHub exploration by design — the methodology's checklists and sieves make it impossible to accidentally skip a step.
