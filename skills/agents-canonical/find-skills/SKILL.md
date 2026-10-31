---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:
- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## END-TO-END SCAFFOLDING PIPELINE (the skill IS a build tool)

This skill is not a "look up a repo" helper. It is a **harvest-and-synthesize
engine** that treats **ALL OF GITHUB as a parts bin**. Any repo — a skills
package, a video editor, a CLI, a library — is just a box of features sitting
on a shelf. We walk in, pull repos down, go over them, and extract ONLY the
parts/features we want (e.g. a video tool with 30 features but we only need 5).
We do NOT adopt whole repos. We assemble a CUSTOM BUILD from the best parts
across the entire corpus, plus our own invention for the gaps.

The pipeline lives in `./pipeline/` and is driven by `pipeline/run.mjs`. Every
run produces two artifacts:

- `out/report.html` — the exhaustive website (coverage → sitemap → branches →
  parts catalog → ideas-vs-parts → comparison tables → creative picks →
  custom-build recipe → gaps → top picks).
- `out/scaffold/` — the synthesized build: `SKILL.md`, `prompts/`, `workflows/`,
  `snippets/`, `RECIPE.md`.

### The 7-stage pipeline (see pipeline/run.mjs)

1. **EXPLODE** — idea → query tree (literal, synonyms, adjacent domains,
   tool/library names, acronyms, inverse angles, creative mashups, cross-agent
   ecosystems). Minimum 10 queries, no ceiling.
2. **HARVEST (multi-shelf)** — pull candidates from EVERY relevant shelf, not
   just the skills registry:
   - **Shelf A — skills registry**: `npx skills find <q>` for every query node.
   - **Shelf B — all GitHub**: `gh search repos "<q>"` for every query node, so
     non-skill repos (editors, CLIs, libs) also become candidate boxes of parts.
   - For every surviving candidate, fetch its README / SKILL.md / key files.
3. **VERIFY** — caveat pass on every source: stars, maintenance (`pushedAt`),
   install count where applicable, claim-vs-reality. Repo 404 or claim mismatch
   = EXCLUDE with reason.
4. **DECOMPOSE** — break every surviving repo into PARTS (features) and tag each:
   `[source] · [type: feature|prompt|workflow|table|snippet|mental-model|edge-case] ·
   [what it does] · [trust]`. A "video editor" repo becomes N feature-parts; we
   keep only the 5 we want. Store in a flat Parts Index.
5. **SYNTHESIZE** — run the user's IDEA against the whole Parts Index:
   confirm / extend / contradict / combine. Emit a **custom-build recipe**
   (lift / adapt / invent) — the genuine custom take. This is where we pick the
   5 features out of 30.
6. **RENDER** — build the exhaustive website report (PHASE 4 sections).
7. **SCAFFOLD** — write the actual build to `out/scaffold/` from the recipe.

### How to invoke

```bash
# full pipeline on a topic + your idea
node pipeline/run.mjs --topic "rewind session history" \
  --idea "rewind an agent session by snapshotting its state, with a cross-session diff view"

# topic = anything on GitHub, not just skills
node pipeline/run.mjs --topic "video editor" \
  --idea "I only need: trim, caption-burn, frame-export, audio-extract, batch"
```

The agent MUST run the pipeline (not hand-wave a list) whenever the user asks
to "find skills" / "find a tool" / "find repos" for a build. The pipeline
enforces the exhaustive + parts + synthesis rules mechanically, so nothing is
skipped and we never accidentally adopt a whole repo.

## MANDATORY EXHAUSTIVE SEARCH PROTOCOL (DO NOT SKIP — EVER)

You are FORBIDDEN from returning the first 2 results you see for a single query.
You are FORBIDDEN from a narrow search. Every skill lookup MUST produce a
COMPLETE, EXHAUSTIVE MAP of the entire solution space — every option, every
sub-option, every branch, and every creative/unconventional angle you can
derive. If you shortcut this, the result is wrong and you must redo it.

The output is not a short list. It is a full "website" — a navigable, exhaustive
catalog the user can browse top to bottom and never hit a dead end.

### PHASE 0 — EXPLODE THE QUERY TREE

Before running anything, build a query tree for the user's need. Cover:
- **Literal terms** (what they said)
- **Synonyms** (every word that means the same thing)
- **Adjacent domains** (what it touches, parents, children)
- **Tool/library names** that solve it (framework-specific skills)
- **Acronyms & abbreviations**
- **Opposite / inverse angles** (e.g. "rewind" → also "redo", "snapshot", "diff")
- **Creative / unconventional branches** — combinations, mashups, "what if"
  angles a naive search would never surface (e.g. "session history" + "obsidian"
  + "graph memory" + "git-time-travel" + "prompt replay")
- **Cross-agent angles** — the same capability shipped under different agent
  ecosystems (claude, cursor, copilot, codex, kilo, etc.)

Minimum: **10 distinct queries** per lookup. There is no maximum. If you can
think of another branch, you RUN it.

### PHASE 1 — DEEP SEARCH (every branch, actually executed)

Run `npx skills find` for EVERY node in the query tree. Parallelize the bash
calls in a single message. Capture the FULL output of each — never truncate to
the head. Missing a branch = protocol failure.

### PHASE 2 — CONSOLIDATE INTO A FULL CANDIDATE GRAPH

Merge all results into ONE deduped pool. For each candidate record:
- name, source repo, install count, what it claims to do
- which query branch(es) surfaced it (so the user sees the map)
Group candidates into the branches they belong to — do NOT flatten into one
ranked list yet. The structure must show the tree.

### PHASE 3 — CAVEAT SEARCH (MAX LEVEL, applied to ALL survivors)

For EVERY candidate that survives consolidation, verify before it appears in the
report. Not optional. Not sampled:
- **Install count** — prefer 1K+. Flag anything under 100 as "low-trust".
- **Source reputation** — official sources (`github`, `vercel-labs`,
  `anthropics`, `microsoft`) rank above unknown authors.
- **GitHub stars** — `gh repo view <owner>/<repo> --json stargazerCount`.
  <100 stars = skepticism. Repo 404 = EXCLUDE.
- **Maintenance** — `gh repo view ... --json pushedAt,updatedAt`.
- **Claim-vs-reality** — `npx skills add <pkg> --dry-run` (or fetch SKILL.md)
  and confirm it does what its name promises. Mismatch = EXCLUDE, and call it
  out as clickbait.
- **Creative-fit** — for unconventional branches, note why the angle is
  interesting even if install count is low (a 30-install skill may be the only
  one doing something novel).

### PHASE 3B — DECOMPOSE INTO PARTS (the corpus is parts, not packages)

CRITICAL: do NOT treat a surviving skill as an all-or-nothing "install this
repo" decision. Each surviving skill is a CONTAINER of reusable PARTS. You MUST
break every surviving skill down into its constituent pieces so our own ideas
can be run against the whole set of parts — not just whole repos:

- **Prompt fragments / system instructions** — reusable wording, rules, persona
  lines we can lift or adapt.
- **Workflow steps / procedures** — ordered checklists, decision trees, loops.
- **Reference tables / taxonomies** — category lists, matrices, mappings.
- **Code snippets / templates** — scripts, configs, skeletons.
- **Mental models / patterns** — the underlying idea (e.g. "rewind via git
  objects", "memory as a graph") independent of its implementation.
- **Edge-case handling** — how it deals with failure, ambiguity, limits.

Extract these parts for EVERY surviving skill (use the dry-run output / fetched
SKILL.md / repo files). Store them in a flat PARTS INDEX tagged by:
`[source skill] · [part type] · [what it does] · [trust]`.

### PHASE 3C — RUN OUR IDEAS PAST THE WHOLE PARTS SET (custom synthesis)

Take the user's actual build / idea and stress-test it against the ENTIRE PARTS
INDEX, not against whole repos. For each of our ideas:
- Which parts confirm, extend, or contradict it?
- Which parts solve a sub-problem we hadn't considered?
- Which parts can be COMBINED into something none of the source skills do alone
  (the creative mashup)?
- Which parts are worth lifting verbatim vs. adapting vs. rejecting?

This is where the genuinely CUSTOM take comes from: we are not adopting a
package, we are assembling a build from the best parts across the whole corpus,
plus our own invention for the gaps.

### PHASE 4 — BUILD THE EXHAUSTIVE WEBSITE REPORT

Present the FULL catalog as a browsable site. Required sections:

1. **Coverage header** — how many queries you ran, how many branches, how many
   candidates found, how many survived caveats, how many PARTS extracted. Proof
   you actually tried.
2. **Navigation / sitemap** — the branch tree, linked to each section below.
3. **Branch sections** — one per branch of the query tree. Each contains:
   - every surviving skill in that branch (name, installs, stars, what it does,
     install command, skills.sh link, trust caveat)
   - clearly marked EXCLUDED items with the reason (dead repo, claim mismatch)
4. **Parts catalog** — the PARTS INDEX from PHASE 3B, grouped by part type, so
   the user can see every reusable piece across the whole corpus.
5. **Ideas-vs-parts analysis** — from PHASE 3C: our build ideas mapped against
   the parts that confirm / extend / contradict / combine them.
6. **Cross-cutting comparison tables** — side-by-side by trust/installs/fit,
   so the user can compare across branches AND across parts.
7. **Creative / unconventional picks** — the off-the-map angles you discovered,
   even if low-install, with rationale.
8. **Custom build recipe** — the synthesized result: which parts to lift, which
   to adapt, which to invent, assembled into OUR take (not a repo install).
9. **Decision guide** — "if you want X, pick Y; if you want Z, pick W" across
   every branch.
10. **Gaps & "build-your-own"** — branches/parts with NO good option, with
    `npx skills init` pointers.
11. **Top recommendation(s)** — only after all of the above.

### PHASE 5 — NEVER SUMMARIZE AWAY THE DETAIL

The report must remain exhaustive end-to-end. Do not collapse it into "here are
the top 2." The user asked for the whole site; deliver the whole site. Do not
collapse parts back into whole-repo recommendations — surface the parts.

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query]` - Search for skills by keyword (run MANY times, see protocol)
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills add --dry-run <package>` - Inspect a skill's contents without installing
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:
1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Synonyms and adjacent domains a skill might be filed under

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists for the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

For example, top skills for web development include:
- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs each)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

### Step 3: EXPLODE + DEEP SEARCH (mandatory, exhaustive, ≥10 queries)

Run `npx skills find` for the original query PLUS a minimum of 10 queries
spanning the full query tree from PHASE 0 (literal, synonyms, adjacent domains,
tool/library names, acronyms, inverse angles, creative mashups, cross-agent
ecosystems). Execute them ALL in parallel — never stop at the first promising
hit, never truncate output.

```bash
npx skills find [original query]
npx skills find [synonym 1]
npx skills find [synonym 2]
npx skills find [adjacent domain]
npx skills find [tool/library name]
npx skills find [acronym]
npx skills find [inverse angle]
npx skills find [creative mashup 1]
npx skills find [creative mashup 2]
npx skills find [cross-agent angle]
npx skills find [branch N]   # keep adding until the tree is exhausted
```

Example tree for "how do I make my React app faster?":
- `npx skills find react performance`
- `npx skills find react optimization`
- `npx skills find nextjs speed`
- `npx skills find frontend bundle`
- `npx skills find web core vitals`
- `npx skills find lighthouse`
- `npx skills find bundle analyzer`
- `npx skills find react memoization`
- `npx skills find spa caching`
- `npx skills find vite build`
- `npx skills find rsc streaming`
- `npx skills find profiling flamegraph`

### Step 4: CAVEAT SEARCH / QUALITY VERIFICATION (mandatory, max level, ALL survivors)

**Do not recommend a skill until it passes ALL of these.** Execute the checks
for EVERY surviving candidate, do not eyeball or sample:

1. **Install count** — `npx skills find` output shows installs. Prefer 1K+.
   Flag anything under 100 as low-trust.
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`,
   `microsoft`, `github`) are more trustworthy than unknown authors.
3. **GitHub stars** — `gh repo view <owner>/<repo> --json stargazerCount`.
   <100 stars = skepticism. Repo 404 = EXCLUDE.
4. **Maintenance** — `gh repo view <owner>/<repo> --json pushedAt,updatedAt`.
5. **Claim verification** — `npx skills add <pkg> --dry-run` (or fetch
   SKILL.md) and confirm it does what its name promises. Exclude
   mismatched/clickbait skills and call them out.

### Step 5: BUILD THE EXHAUSTIVE WEBSITE REPORT

Do NOT present a short list. Deliver the full catalog per PHASE 4:
coverage header → sitemap → one section per branch → parts catalog →
ideas-vs-parts analysis → cross-cutting comparison tables →
creative/unconventional picks → custom build recipe → decision guide → gaps →
top picks. Every surviving skill gets: name, installs, stars, what it does,
install command, skills.sh link, trust caveat. Excluded skills get a named
reason. The PARTS CATALOG and IDEAS-VS-PARTS sections are mandatory — the whole
point is to run our ideas past the parts, not just point at repos.

Example branch entry:

```
## Branch: session-history / rewind
- rohitg00/agentmemory@session-history — 7.6K installs, 25.3K★, maintained.
  Rewind/search/restore agent sessions.
  Install: npx skills add rohitg00/agentmemory@session-history -g -y
  https://skills.sh/rohitg00/agentmemory/session-history
  Caveat: HIGH trust — official-ish, huge install base.
- EXCLUDED simota/agent-skills@rewind — dry-run shows "No matching skills
  found for: rewind" in a 132-skill repo. Clickbait name, dead skill.
```

Example parts entry (from that branch):

```
### Parts from agentmemory@session-history
- [prompt] "Index every session turn with a retrievable summary" — lift/adapt.
- [workflow] "On crash, replay from last checkpoint object" — confirms our idea.
- [mental-model] "memory as append-only log" — contradicts our snapshot model;
  consider combining.
- [pattern] "git-object-backed rewind" — from open-gsd/gsd-undo; mashup candidate.
```

Example ideas-vs-parts line:

```
Our idea "rewind by snapshotting state" is CONFIRMED by agentmemory's
checkpoint workflow, EXTENDED by gsd-undo's git-object approach, and we should
INVENT the missing piece: cross-session diff view (no part covers it).
```

### Step 6: Offer to Install

If the user wants to proceed, you can install any skill for them:

```bash
npx skills add <owner/repo@skill> -g -y
```

The `-g` flag installs globally (user-level) and `-y` skips confirmation prompts.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Explode the tree first** — literal, synonyms, adjacent domains, tool names,
   acronyms, inverse angles, creative mashups, cross-agent ecosystems. Minimum
   10 queries, no ceiling.
2. **Use specific keywords**: "react testing" is better than just "testing"
3. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
4. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`
5. **Never settle for the top 2** of a single query — run the full exhaustive
   search, then the max-level caveat pass, then build the whole report.
6. **Think in parts, not packages** — decompose surviving skills into prompt
   fragments, workflows, patterns, snippets; run our own ideas against the whole
   parts set; synthesize a custom build instead of adopting a whole repo.

## When No Skills Are Found (per branch)

If, after the full exhaustive search + caveat pass, a branch has no surviving
skill, that branch still appears in the report marked "GAP", with the query
count that was run and an `npx skills init` pointer. The website is still
complete — it just shows which branches are empty.

Example gap entry:

```
## Branch: prompt-replay (GAP)
Ran 4 searches (prompt replay, replay transcript, regenerate session,
deterministic replay). 0 candidates survived the caveat pass.
No trustworthy skill exists yet — you could build one:
npx skills init my-prompt-replay-skill
```
