---
name: vinnyos-engine
description: "Skill Chain: VinnyOS Orchestrator"
---

# Skill Chain: VinnyOS Orchestrator

A 3-phase workflow that chains skills together based on context.

---

## How This Works

This is the **main orchestrator**. It tells you WHICH skills to load and WHEN.

**Don't load everything at once.** Load skills on-demand based on what phase you're in.

---

## The Chain

```
PHASE 1: VALIDATE ──────▶ PHASE 2: DISCOVER ──────▶ PHASE 3: BUILD
```

Each phase loads different skills. See references below.

---

## Phase 1: VALIDATE

**Goal:** Stress-test the plan before writing code.

**Load these skills:**
- `@writing-plans` — Create the implementation plan
- `@systematic-debugging` — Debug the plan itself

**When to load:**
- User asks to build something new
- You have a plan that needs validation
- Complex multi-step task

**What to do:**
1. Write the plan with `writing-plans`
2. Apply debugging phases 1-3 TO THE PLAN (not code)
3. Validate: every file path, dependency, integration point

**Output:** A validated, debugged plan.

---

## Phase 2: DISCOVER

**Goal:** Find every existing tool we can reuse.

**Load these skills:**
- `@deep-research` — Analyze top candidates
- `@vinnyos-engine` — Multi-surface search (EXPLORE, HARVEST, DISCOVER, GRAPH)
- `@web-search` — Blog posts, tutorials, Stack Overflow

**When to load:**
- After Phase 1 completes
- Before writing any code
- When you suspect tools exist

**What to do:**
1. Use vinnyos-engine EXPLORE to generate 12+ queries
2. Use vinnyos-engine HARVEST to search repos, code, issues, PRs
3. Use deep-research to analyze top 5 candidates
4. Use web-search for hidden gems
5. Use vinnyos-engine GRAPH to search local codebase

**Output:** A curated list of existing tools with extraction paths.

---

## Phase 3: BUILD (LLM's Choice)

**Goal:** Go rogue. Build what they didn't ask for.

**Load these skills:**
- `@brainstorming` — Explore what user DIDN'T ask for
- `@code-doctor` — Review ALL existing code
- `@test-driven-development` — Write tests for everything

**When to load:**
- After Phase 2 completes
- When you're ready to implement
- When you see gaps in the plan

**What to do:**
1. Use brainstorming to explore unasked needs
2. Use code-doctor phases 1-6 on entire codebase
3. Use TDD to write tests for everything
4. Implement the unasked features
5. Fix bugs found by code-doctor

**Output:** A complete, tested, production-ready system.

---

## Context Triggers

| Context | Load Skill |
|---------|------------|
| "Build X" | Phase 1 → writing-plans |
| "What exists?" | Phase 2 → vinnyos-engine + deep-research |
| "Fix this" | Phase 3 → code-doctor |
| "Test this" | Phase 3 → test-driven-development |
| "What am I missing?" | Phase 3 → brainstorming |
| Complex task | All 3 phases in order |

---

## The Rules

1. **Never load all skills at once** — Load on-demand based on phase
2. **Never skip Phase 1** — A bad plan wastes all subsequent work
3. **Never skip Phase 2** — Reinventing the wheel is waste
4. **Never skip Phase 3** — The user asked for X, but they need Y too
5. **Always chain the skills** — Each skill feeds the next

---

## Reference Files

Load these when you need details:

- `references/phase1-validate.md` — Detailed validation steps
- `references/phase2-discover.md` — Detailed discovery steps
- `references/phase3-build.md` — Detailed build steps
- `references/context-map.md` — When to load which skill

---

## The Output

After running this chain, you have:
1. ✅ A validated, debugged plan
2. ✅ A research report on existing tools
3. ✅ A complete, tested implementation
4. ✅ Documentation of what was built and why
