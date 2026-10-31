---
name: agent-playbook
description: >
  Vinny's multi-agent orchestration playbook — when to use Task subagents vs
  /agent-team vs /implement, how to slice parallel reviews, synthesize findings,
  implement P0, and verify. Auto-invoke when user asks about agents, subagents,
  parallel review, agent memory, how agents work, spin up N agents, or what to
  ask after a code review. Slash: /agent-playbook
metadata:
  short-description: "Multi-agent review → synthesize → implement → verify"
---

# Agent Playbook — Review, Ship, Remember

Use this before spinning up agents. Prevents "8 reports, zero patches."

## Decision tree

```
User request
├── "review / audit / find bugs"     → REVIEW pipeline (below)
├── "build / fix / implement"        → /implement OR agent-team run
├── "try N approaches"               → /best-of-n
├── "verify what we did"             → /check-work
└── "how do agents work?"            → explain + load MEMORY.md
```

## REVIEW pipeline (parallel agents)

### Step 0 — Confirm scope (ask only if ambiguous)

- **Review only** — reports, no code changes
- **Review + P0 fixes** — default recommendation
- **Review + full refactor** — needs explicit approval

### Step 1 — Slice work (non-overlapping)

Max **4–8** parallel `Task` agents. Each gets:
- Absolute file paths
- One focus area (bugs | security | perf | arch)
- Output format: `CRITICAL/HIGH/MEDIUM/LOW` + line refs + top 5 fixes

**VinnyOS standard slices:**

| # | Slice | Paths |
|---|-------|-------|
| 1 | Hub JS | `surfaces/disk-hub/index.html` script |
| 2 | Hub CSS | `style.css` + HTML structure |
| 3 | Proxy | `surfaces/proxy/server.js` |
| 4 | MATRIX bridge | `~/MATRIX/matrix/{api,dedup_engine,security}.py` + proxy matrix routes |
| 5 | Shell ops | `scripts/*.sh`, `Start VinnyOS.command` |
| 6 | Security cross-cut | hub + proxy + MATRIX threat model |
| 7 | Performance | JS hot paths, CSS GPU, proxy I/O |
| 8 | Architecture | repo layout, data flow, tech debt |

### Step 2 — Launch agents

```text
Task × N, subagent_type: generalPurpose, model: composer-2.5-fast
```

**Note:** `code-reviewer` subagent type is NOT available in Grok Build — use `generalPurpose`.

### Step 3 — SYNTHESIZE (parent agent, not parallel)

One pass to:
1. Dedupe overlapping findings (proxy auth flagged by agents 3, 4, 6 → one P0)
2. Build master queue: P0 / P1 / P2
3. Present rundown table to user
4. Ask OR auto-start P0 if user said "fix it" / "ALL NOW"

### Step 4 — IMPLEMENT

- **Small P0 set:** parent agent edits directly
- **Large refactor:** `/agent-team run "Implement VinnyOS P0 security hardening"`
- **Quality bar:** `/implement` for feature work with review loop

### Step 5 — VERIFY

Always after implementation:
```bash
curl -s http://127.0.0.1:3001/api/health
# Optional: /check-work
```

Manual: hard-refresh hub, test mobile nav, test Delete Buddy dry-run.

### Step 6 — MEMORY

After productive session:
- Append to `~/.grok/memory/MEMORY.md` under `## Agent Orchestration`
- User runs `/flush` in TUI for full session capture
- Enable persistent memory: `GROK_MEMORY=1` or `[memory] enabled = true` in `~/.grok/config.toml`

## Agent types reference

| Tool | Role | Persistence |
|------|------|-------------|
| Parent (you) | Orchestrate, synthesize, talk to Vinny | This conversation |
| `Task` subagent | Isolated review/implement chunk | Returns once; ID resumable |
| `/agent-team` | build plans, composer implements, events.jsonl | `.agent-team/` on disk |
| `/implement` | Implementer + N reviewers loop | Review files on disk |

## Prompt templates

### Parallel review launch

```text
Code review [SLICE]. Read [PATHS]. Focus: [bugs|security|perf].
Return CRITICAL/HIGH/MEDIUM/LOW with line refs, root cause, fix snippet.
Top 5 immediate fixes. Do not edit files.
```

### Post-review synthesis (parent)

```text
Merge all agent reports. Dedupe. Master P0/P1/P2 table.
Tell user what they should ask for next if they only asked for review.
```

### Implementation handoff

```text
Implement P0 only from synthesized review:
1. [item]
2. [item]
Do not expand scope. Run health check after.
```

## Anti-patterns

| Bad | Good |
|-----|------|
| 8 agents, no synthesis | 8 agents → 1 synthesis → P0 implement |
| Review then stop | Review → implement P0 → verify |
| Overlapping agent scopes | Fixed slices per file/domain |
| `code-reviewer` type (fails) | `generalPurpose` |
| Agents implement in parallel | One implementer after synthesis |
| No memory after big session | Update MEMORY.md + `/flush` |

## Vinny-specific defaults

- Canonical repos: `~/Projects/VinnyOS/`, `~/MATRIX/`
- Hub URL: `http://localhost:3001`
- UI: responsive, distinctive (not Inter/cyan-purple)
- User tone: direct, wants action — default to **review + P0 fix** unless "review only"