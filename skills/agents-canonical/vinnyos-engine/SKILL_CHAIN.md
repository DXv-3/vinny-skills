# The VinnyOS Skill Chain Workflow

A 3-phase workflow that chains multiple skills together to validate, discover, and build.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE SKILL CHAIN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: VALIDATE          PHASE 2: DISCOVER                  │
│  ┌─────────────────┐        ┌─────────────────┐                │
│  │ writing-plans   │───────▶│ deep-research    │                │
│  │ systematic-     │        │ vinnyos-engine   │                │
│  │   debugging     │        │ web-search       │                │
│  └─────────────────┘        └─────────────────┘                │
│           │                          │                          │
│           ▼                          ▼                          │
│  Is the plan optimal?       What already exists?               │
│                                                                 │
│                          PHASE 3: BUILD                         │
│                         ┌─────────────────┐                    │
│                         │ brainstorming    │                    │
│                         │ code-doctor      │                    │
│                         │ test-driven-     │                    │
│                         │   development    │                    │
│                         └─────────────────┘                    │
│                                  │                              │
│                                  ▼                              │
│                         Build it right.                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: VALIDATE (Is the plan optimal?)

**Skills used:** writing-plans, systematic-debugging

**Goal:** Stress-test the plan before writing a single line of code.

### Step 1.1: Write the Plan
- Use `writing-plans` to create a detailed implementation plan
- Include exact file paths, code snippets, test cases
- Make every step 2-5 minutes (bite-sized)

### Step 1.2: Debug the Plan
- Use `systematic-debugging` Phase 1-3 ON THE PLAN ITSELF
- Ask: "What could go wrong with this approach?"
- Trace the data flow through the proposed architecture
- Find the root causes of potential failures BEFORE they happen

### Step 1.3: Validate Checklist
- [ ] Every file path exists or will be created
- [ ] Every dependency is available
- [ ] Every integration point is tested
- [ ] Every error path is handled
- [ ] The plan follows DRY, YAGNI, TDD

**Output:** A validated, debugged plan ready for execution.

---

## Phase 2: DISCOVER (What already exists?)

**Skills used:** deep-research, vinnyos-engine, web-search

**Goal:** Find every existing tool, library, and pattern we can reuse.

### Step 2.1: Multi-Surface Search
- Use `vinnyos-engine` Layer 1 (EXPLORE) to generate 12+ queries
- Use `vinnyos-engine` Layer 2 (HARVEST) to search repos, code, issues, PRs
- Use `vinnyos-engine` Layer 5 (DISCOVER) to search by layer

### Step 2.2: Deep Research
- Use `deep-research` to analyze the top 5 candidates
- Check: stars, activity, documentation, license, compatibility
- Extract: code snippets, patterns, mental models

### Step 2.3: Web Search
- Use `web-search` for blog posts, tutorials, Stack Overflow answers
- Find: hidden gems, unconventional approaches, real-world usage

### Step 2.4: Knowledge Graph
- Use `vinnyos-engine` Layer 13 (GRAPH) to search local codebase
- Find: existing implementations, reusable components

**Output:** A curated list of existing tools with extraction paths.

---

## Phase 3: BUILD (LLM's Choice)

**Skills used:** brainstorming, code-doctor, test-driven-development

**Goal:** Go rogue. Do what needs to be done, regardless of what was asked.

### Step 3.1: Brainstorm the Unasked
- Use `brainstorming` to explore what the user DIDN'T ask for
- Ask: "What does this system need that they haven't thought of?"
- Propose 2-3 approaches with trade-offs

### Step 3.2: Doctor the Code
- Use `code-doctor` to review ALL existing code
- Phase 1-6 on the entire codebase
- Find: bugs, dead code, missing features, security issues

### Step 3.3: Test Everything
- Use `test-driven-development` to write tests for everything
- Red-Green-Refactor cycle
- No production code without a failing test first

### Step 3.4: Build What's Missing
- Implement the unasked features
- Fix the bugs found by code-doctor
- Add tests for everything

**Output:** A complete, tested, production-ready system.

---

## The Chain in Action

### Example: "Build a knowledge graph for my codebase"

**Phase 1: VALIDATE**
1. Write plan: "Index codebase → Extract entities → Build graph → Query API"
2. Debug plan: "What if codebase is too large? What if entities are ambiguous?"
3. Validate: "Need chunking strategy, need entity resolution, need caching"

**Phase 2: DISCOVER**
1. EXPLORE: "knowledge graph codebase", "code intelligence", "AST analysis"
2. HARVEST: Find microsoft/graphrag, tree-sitter, scip
3. DEEP RESEARCH: Analyze graphrag's approach, tree-sitter's performance
4. WEB SEARCH: Find blog posts on code intelligence
5. GRAPH: Search local codebase for existing graph code

**Phase 3: BUILD (LLM's Choice)**
1. BRAINSTORM: "They asked for a knowledge graph, but they also need:
   - Incremental updates (not full rebuilds)
   - Cross-reference linking (not just extraction)
   - Privacy controls (not everything should be indexed)"
2. CODE-DOCTOR: Review existing codebase for related code
3. TDD: Write tests for incremental updates, cross-references, privacy
4. BUILD: Implement the unasked features

---

## When to Use This Chain

| Use When | Don't Use When |
|----------|----------------|
| Building something new | Quick bug fix |
| Complex multi-step task | Simple lookup |
| System architecture | Configuration change |
| Integration work | Documentation update |

---

## The Rules

1. **Never skip Phase 1** - A bad plan wastes all subsequent work
2. **Never skip Phase 2** - Reinventing the wheel is waste
3. **Never skip Phase 3** - The user asked for X, but they need Y too
4. **Always chain the skills** - Each skill feeds the next
5. **Always produce output** - Plans, research, code, tests

---

## The Output

After running this chain, you have:
1. ✅ A validated, debugged plan
2. ✅ A research report on existing tools
3. ✅ A complete, tested implementation
4. ✅ Documentation of what was built and why

**The system is ready.**
