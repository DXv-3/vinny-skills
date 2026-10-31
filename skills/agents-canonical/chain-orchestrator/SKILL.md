---
name: chain-orchestrator
description: 4-phase orchestrator that chains VALIDATE → DISCOVER → BUILD → VERIFY. Triggers the right sub-skills at the right time. One command to rule them all.
---

# Chain Orchestrator

A meta-skill that orchestrates the full development lifecycle: plan → research → build → verify. One trigger, all phases, smart execution.

## When to Use

- "Build me X" — full lifecycle
- "Create a system that..." — full lifecycle
- "I want to build..." — full lifecycle
- Any multi-step project that needs planning, research, coding, and verification

## The Chain

```
┌─────────────────────────────────────────────────────────────┐
│                    CHAIN ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: VALIDATE                                          │
│  ├─ writing-plans → create implementation plan              │
  │  └─ code-doctor → review plan (phases 0-3 only)            │
│                                                             │
│  PHASE 2: DISCOVER                                          │
│  ├─ deep-research → multi-source research                   │
│  ├─ web-search → find specific implementations              │
│  └─ github-ecosystem → discover repos, extract parts        │
│                                                             │
│  PHASE 3: BUILD                                             │
│  ├─ brainstorming → design (HARD GATE: no code till approved)│
│  ├─ test-driven-development → red-green-refactor            │
│  └─ executing-plans → implement task-by-task                │
│                                                             │
│  PHASE 4: VERIFY                                            │
  │  ├─ code-doctor → full 7-phase review                       │
│  └─ test-extraction → verify parts compile + run            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## How to Trigger

### Option 1: Full Chain (recommended)
```
Use chain-orchestrator for: [describe what you want to build]
```

### Option 2: Specific Phase
```
Use chain-orchestrator phase 2 for: [research topic]
```

### Option 3: Resume from checkpoint
```
Use chain-orchestrator resume from phase 3
```

## Phase Execution Rules

### Rule 1: No Skipping
Every phase must complete before the next begins. The orchestrator tracks state in `.chain-state.json`.

### Rule 2: Smart Parallelization
Within a phase, run independent tasks in parallel:
- Phase 2: `deep-research` + `web-search` + `github-ecosystem` can run simultaneously
- Phase 3: `brainstorming` must complete before `test-driven-development`

### Rule 3: Gate Checks
Each phase has a gate that must pass before advancing:

| Phase | Gate | Pass Condition |
|-------|------|----------------|
   | 1 VALIDATE | Plan exists + code-doctor approved | Plan file exists, no critical issues from phases 0-3 |
| 2 DISCOVER | Research complete + parts identified | sources.jsonl exists, parts cataloged |
| 3 BUILD | Design approved + tests pass | Design doc signed off, all tests green |
| 4 VERIFY | Code-doctor clean + extraction tested | 0 critical issues, parts compile |

### Rule 4: Failure Recovery
If a phase fails:
1. Log the failure in `.chain-state.json`
2. Run `code-doctor` (full 7-phase chain) on the failed phase output
3. Fix issues
4. Re-run the failed phase
5. Max 3 retries per phase, then escalate to human

### Rule 5: Context Preservation
Between phases, preserve:
- Decision log (why we chose X over Y)
- Parts catalog (what we extracted from where)
- Test results (what passed/failed)
- Open questions (what needs human input)

## State File Format

`.chain-state.json` tracks progress:

```json
{
  "project": "knowledge-graph-system",
  "started": "2026-07-31T22:00:00Z",
  "current_phase": 3,
  "phases": {
    "1_validate": {
      "status": "complete",
      "plan_path": "docs/superpowers/plans/2026-07-31-knowledge-graph.md",
      "code_doctor_review": "approved",
      "completed_at": "2026-07-31T22:15:00Z"
    },
    "2_discover": {
      "status": "complete",
      "research_path": "~/Documents/knowledge-graph-research/",
      "parts_cataloged": 47,
      "completed_at": "2026-07-31T22:30:00Z"
    },
    "3_build": {
      "status": "in_progress",
      "design_approved": true,
      "tests_passing": 12,
      "tests_failing": 0
    },
    "4_verify": {
      "status": "pending"
    }
  }
}
```

## Phase Details

### PHASE 1: VALIDATE (10-15 min)

**Goal:** Create a plan that survives scrutiny before any code is written.

**Steps:**
1. **Understand the request** — parse what the user wants
2. **Load `writing-plans`** — create implementation plan
3. **Save plan** to `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`
4. **Load `code-doctor`** — run phases 0-3 (PROFILE → READ → MAP → CATEGORIZE) on the PLAN
5. **Fix issues** if code-doctor finds problems
6. **Gate check** — plan exists + no critical issues → advance

**Output:** Validated implementation plan

### PHASE 2: DISCOVER (15-30 min)

**Goal:** Find every existing tool, library, and pattern we can reuse.

**Steps:**
1. **Load `deep-research`** — research the domain (parallel with step 2-3)
2. **Load `web-search`** — find specific implementations (parallel)
3. **Run `github-ecosystem_discover_all`** — find repos across all layers (parallel)
4. **Catalog parts** — for each promising repo:
   - `github-ecosystem_analyze_repo` → map structure
   - `github-ecosystem_extract_module` → pull the part
   - `github-ecosystem_test_extraction` → verify it works
5. **Build parts catalog** — save to `docs/parts-catalog.md`
6. **Gate check** — research complete + parts cataloged → advance

**Output:** Research report + verified parts catalog

### PHASE 3: BUILD (varies)

**Goal:** Design, then build with tests.

**Steps:**
1. **Load `brainstorming`** — design the architecture
   - HARD GATE: no code until design approved
   - Write design doc to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
2. **Load `test-driven-development`** — for each component:
   - Write failing test
   - Verify it fails
   - Write minimal code
   - Verify it passes
   - Refactor
   - Commit
3. **Load `executing-plans`** — implement remaining tasks from plan
4. **Gate check** — design approved + all tests green → advance

**Output:** Working code with tests

### PHASE 4: VERIFY (10-20 min)

**Goal:** Prove everything works. No assumptions.

**Steps:**
1. **Load `code-doctor`** — full 7-phase review (PROFILE → READ → MAP → CATEGORIZE → FIX → VERIFY → REVIEW)
2. **Fix all issues** found by code-doctor
3. **Re-run tests** — all must pass
4. **Test extracted parts** — verify they still compile + run in isolation
5. **Integration test** — verify parts work together
6. **Final report** — generate summary
7. **Gate check** — 0 critical issues + all tests pass → DONE

**Output:** Verified, tested, reviewed code

## Integration with Existing Skills

This orchestrator chains these skills:

| Skill | Phase | What it does |
|-------|-------|-------------|
| `writing-plans` | 1 | Creates implementation plan |
| `code-doctor` | 1, 4 | Reviews code/plan (7-phase chain) |
| `deep-research` | 2 | Multi-source research |
| `web-search` | 2 | Web search + extraction |
| `github-ecosystem` | 2, 4 | Discover repos, extract parts, test |
| `brainstorming` | 3 | Design architecture (hard gate) |
| `test-driven-development` | 3 | Red-green-refactor |
| `executing-plans` | 3 | Implement tasks |

## Error Handling

### If deep-research fails
Fall back to web-search only. Log the failure.

### If github-ecosystem can't extract
Log the repo as "extractable: false" in parts catalog. Continue with other parts.

### If tests fail during build
Run `systematic-debugging` on the failure. Fix before continuing.

### If code-doctor finds critical issues
STOP. Fix all critical issues before advancing. No exceptions.

### If phase retries exceed 3
Escalate to human with full context of what failed and why.

## Example Usage

### Full chain
```
User: Build me a personal knowledge system that indexes all my data
Agent: Using chain-orchestrator for: personal knowledge system
        Phase 1: VALIDATE — creating plan...
        Phase 2: DISCOVER — researching + finding parts...
        Phase 3: BUILD — designing + building with tests...
        Phase 4: VERIFY — code review + testing...
        DONE — all phases complete, all tests passing
```

### Specific phase
```
User: Research the best knowledge graph libraries
Agent: Using chain-orchestrator phase 2 (DISCOVER)
        Running deep-research + web-search + github-ecosystem...
        Results: [research report + parts catalog]
```

## Files Created

```
.chain-state.json          — progress tracking
docs/superpowers/plans/    — implementation plans
docs/superpowers/specs/    — design documents
docs/parts-catalog.md      — extracted parts
~/Documents/<topic>_Research_<date>/  — research output
```

## Remember

1. **Never skip phases** — the chain exists for a reason
2. **Never code before design** — brainstorming HARD GATE
3. **Never ship without tests** — TDD Iron Law
4. **Never approve without code-doctor** — mandatory review
5. **Work smart** — parallelize independent tasks, serialize dependent ones
6. **Preserve context** — decisions, parts, tests, failures — all logged
7. **Escalate when stuck** — 3 retries max, then ask human
