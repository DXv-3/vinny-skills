---
name: unified-github-research
description: One complete GitHub research system — merges the exhaustive solo pipeline (7 progressively narrower search sieves, recursive topic expansion, deep validation, comparative matrix) with the swarm zone fan-out mode and a mandatory omission pass. Use for ANY comprehensive GitHub discovery, technology landscape, ecosystem mapping, or "find every repo that does X", large or small. Triggers on "deep github research," "exhaustive github search," "find every repo for X on github," "github ecosystem audit," "map all repos that," "research this across github," "swarm github research," or /unified-github-research. Supersedes github-deep-research and swarm-github-research for new runs.
---

# Unified GitHub Research

One pipeline, two modes, one state format. Full design rationale: `~/Documents/research/github-research-system/UNIFIED-SPEC.md`.

## Mode selection

- **Solo** (default): one topic → run Phases 0–6 once.
- **Swarm**: a topic with 3+ clearly separable sub-areas (e.g. "our agent stack") → Phase S0 splits it into 3–8 zones, Phases 1–6 run per zone, Phase 7 synthesizes across zones. When unsure, start solo; upgrade to swarm if the topic outgrows one state file.

## Phase 0: RESUME & PRIOR-COVERAGE CHECK (mandatory, before any search)

Research sessions die — concurrency limits, crashes, closed windows. Anything only in context is lost. Before the first query:

1. **Prior coverage**: read `~/Documents/research/INDEX.md` and scan `~/Documents/research/github-*.md` for this topic or an adjacent one. Complete report exists → present it and ask whether to extend or deliberately re-run. Never silently re-research a covered topic.
2. **In-flight state**: if `github-$TOPIC-state.json` (or a `github-swarm-$TOPIC-state.json` parent) exists, load it, tell the user what was already done, continue from `next_actions`. Never re-run `queries_executed`, never re-research `zones_completed`.
3. **Create files before the first search** (`mkdir -p ~/Documents/research`): the report stub (`github-$TOPIC-$DATE.md` — header + empty section skeleton) and the state file (format below).

## Phase 1: QUERY EXPLOSION + THE 7 SIEVES

Explode the seed into **≥10 queries** from six angles: literal synonyms, adjacent domains, known tool names, acronyms (both forms), inverse angles (what it replaces / what replaces it), mashups ("awesome X", "curated X", "X hub").

Push every query through all 7 progressively narrower sieves — exhaust each sieve (paginate past page 1) before the next:

| Sieve | Pattern | Finds |
|---|---|---|
| 1 Broad | `gh search repos "term" --sort stars` | Big players |
| 2 Recent | `--sort updated` | Active projects stars miss |
| 3 Niche | per-language: `language:rust` etc. | Language-specific solutions |
| 4 README-deep | `"term" in:readme` | Repos that merely mention it |
| 5 Topic-tagged | `topic:term` via `gh api search/repositories` | GitHub's own taxonomy |
| 6 Inverse | `"alternative to term" / "term replacement" / "better than term"` | Competitors |
| 7 Curated | `"awesome term" / "curated term"` | Hand-picked lists |

Tool priority: MCP discovery tools if available → `gh search repos --json` → `gh api` + `--jq` → `gh search code` (who imports it) → `gh search issues`. Check `gh auth status` first; batch calls, don't fire 50 in parallel.

## Phase 2: RECURSIVE EXPANSION ROUNDS

Per discovered repo, expand: topics (`repos/owner/name/topics`) → org repos → dependents → `package.json`/`Cargo.toml`/`requirements.txt` deps → `gh search code "owner/name"` importers → README mentions. Found repos feed new rounds.

**Stop condition:** 3 consecutive rounds yield no new repos meeting the quality bar (>5 stars AND pushed ≤18 months, OR community-recommended).

## Phase 3: DEEP VALIDATION

Every surviving candidate: license (`repos/owner/name/license`), `pushed_at`, issue open/close ratio and response time, release cadence, contributor count (bus factor), structure via repo analysis if available. Assign risk: **ABANDONED** (12+ mo silent) / **SOLO** / **ALPHA** (pre-1.0) / **STABLE** / **ENTERPRISE** (company-backed).

## Phase 4: COMPARATIVE MATRIX

| Repo | Stars | License | Lang | Last Push | Health | Community | Architecture | Risk |

## Phase 5: OMISSION PASS (mandatory — this is what round 1 gets wrong)

Before writing conclusions, self-audit with fresh eyes. The swarm run proved this phase earns its cost: it caught unverified licenses and the single biggest find (a router missed entirely in round 1).

1. Re-verify **every license claim** against the API (never trust README badges).
2. Re-walk the 7 sieves and ask of each: what would this sieve find that I haven't listed?
3. Cross-check the recursion: did every repo's topics/orgs actually get followed?
4. Check the obvious misses: the repo everyone in the space depends on, the newest project (<6 months), the biggest org in the space.
5. Write findings into the report's `## Omission Pass` section: what was missed, what changed. Log finds in state: `omission_pass.finds`.

## Phase 6: SYNTHESIS & REPORT

Append to the report file (never context-only): Executive Summary → Tier 1 Primary / Tier 2 Supplementary / Tier 3 Emerging / Tier 4 Abandoned-but-relevant → Comparative Matrix → **Omission Pass** → Gaps & Open Questions → Build Path Recommendation → Methodology Notes (all queries, exhausted vs rate-limited, analyzed vs surface-scanned, limitations).

On completion, add one line to `~/Documents/research/INDEX.md`: `filename | topic | status | date`.

### Phase 7 (swarm mode only): CROSS-ZONE SYNTHESIS

Merge zone reports: shared patterns, contradictions between zones, cross-zone finds, one combined build path. Synthesis goes to `github-swarm-$TOPIC-$DATE.md`; per-zone reports stay as-is.

## Phase S0 (swarm mode): ZONE SPLIT

Split the topic into 3–8 zones with one-line queries each. Create a parent state file (`github-swarm-$TOPIC-state.json`) listing zones and per-zone state paths. Zones run sequentially by default (concurrent heavy research chats trip platform concurrency limits — one at a time); each zone is a full Phases 0–6 run with its own state file and zone report (`github-$ZONE-$DATE.md`).

## State file (format v2 — checkpoint after every phase and every ≤10-query/≤10-repo batch)

`github-$TOPIC-state.json` (solo/zone) or `github-swarm-$TOPIC-state.json` (swarm parent):

```json
{
  "topic": "...", "mode": "solo|swarm", "zone": null,
  "updated_at": "ISO", "phase": "0-7",
  "report_path": "...", "zone_reports": {},
  "zones_completed": [], "next_zone": null,
  "queries_executed": [], "repos_discovered": [], "repos_validated": [],
  "findings": [{"repo": "owner/name", "tier": 1, "stars": 0, "license": "", "risk": "STABLE", "note": ""}],
  "omission_pass": {"done": false, "finds": []},
  "rate_limit_remaining": 4500, "next_actions": []
}
```

A checkpoint is one file write; do it constantly. Update `updated_at`, `phase`, `next_actions` every write; append to `findings` as repos validate. Resume = load state → cross-check report → continue from `next_actions`. Never restart a topic that has a state file.

## Fallbacks & rate limits

Rate-limited or API down → `web-search site:github.com` → `agent-reach`; document what was missed in `next_actions`, offer resume. Start with MCP tools where available (they manage their own limits); prefer GraphQL/`--jq` batching; high-signal searches first.

## Anti-patterns

- ❌ Stopping at page 1, one query per topic, skipping a sieve, or claiming "nothing found" without exhausting all 7
- ❌ Skipping recursion, org scans, dependency graphs, or issue mining
- ❌ Trusting star counts or README license badges without API verification
- ❌ Skipping the omission pass because "the research looked complete" — that is exactly when it isn't
- ❌ Holding state only in conversation, or running multiple heavy research chats concurrently
- ❌ Re-researching a topic INDEX.md already covers
