---
name: skill-workflow
description: "Meta-skill that scans all available agent skills, analyzes the current conversation/context, and recommends a workflow of skills to apply 'at this moment.' Uses multi-perspective analysis ('book club') with 7 personalities to arrive at a confident, unified recommendation. Handles gaps by planning new skills to build. Triggers: suggest skills, which skills, workflow of skills, what skills to use, skill workflow, skill chain, skill recommendation, how to approach this, plan my workflow, step by step skills, bookclub, personalities, what skills apply, skill chain recommendation, gap to build, what skills are missing"
---

# Skill Workflow

A meta-skill that scans the full skills catalog, reads the current conversation, runs a multi-perspective analysis ("book club"), and recommends the exact workflow of skills to apply **right now**.

## What This Skill Does

You are not guessing. You are not hoping. You read the room, scan the shelves, and with full confidence tell the user exactly which skills in which order will move their task forward. No stress, no worry — you know what you're doing.

When invoked, this skill:

1. **Scans** every available skill (local `~/.agents/skills/`, `~/.claude/skills/`, and registered via MCP `mcp-gateway`)
2. **Analyzes** the current conversation context — what is actually happening, what is being attempted
3. **Applies multiple analytical perspectives** ("the book club") to stress-test the recommendation
4. **Assembles** a workflow: an ordered chain of skills with rationale, dependencies, and parallelization
5. **Delivers** the workflow with confidence and clarity

## When to Trigger

Use this skill when:

- The user asks "what skills should I use for this?"
- The user asks "which skills apply here?"
- The user wants a workflow: "plan my workflow with skills"
- The user is starting a multi-step task and needs skill chaining
- The user says "do a book club on it" or "get all your personalities on the same page"
- You need to decide which skills to chain for a complex request
- The task touches multiple domains and you need to sequence skill usage
- The scan finds a gap — you need to plan out and build a missing skill

## The Gap → Build Mindset

When the book club finds that **no existing skill** covers what's needed, that is not a dead end. It is just a little bit more work.

> "Nothing works" is never the answer. It is either found, assembled, or built.

If a capability gap exists:

1. **Check if a close sibling exists** — maybe `find-skills` can discover something at a different angle
2. **Decompose the missing need into parts** — can existing skills be adapted? Can a new skill borrow from existing ones?
3. **Plan the new skill** — name, description, triggers, scope, what it owns vs. what it delegates
4. **Build the new skill** — scaffold the SKILL.md, references, evals, and any tooling
5. **Wire it into the workflow** — the gap is closed; the workflow proceeds as if it was always there

The Gatekeeper's voice on gaps: *"Don't call it missing — call it the next thing to build. Confidence stays high."*

## The Book Club

Before recommending, gather **all top analytical perspectives** and get them on the same page. Each personality reads the situation independently, then they converge.

### The Panel

| Personality | Lens | Question |
|---|---|---|
| **The Orchestrator** | Sequencing & flow | What is the correct order? Where are the hard gates? What can run in parallel? |
| **The Skeptic** | Risk & gaps | What's missing? What could go wrong? What assumptions are we making? |
| **The Connector** | Cross-skill leverage | Which skills amplify each other? What parts can be borrowed? |
| **The Pragmatist** | Execution reality | What's the minimum viable workflow? What has the user actually done so far? |
| **The Visionary** | End-state clarity | What does success look like? What's the real outcome the user wants? |
| **The Gatekeeper** | Boundaries & scope | What should NOT be done? What are we excluding and why? |
| **The Architect** | Gaps & new builds | What's missing? If we must build it, what should the new skill be? |

All seven convene. They debate. They converge. They produce one unified understanding of what is transpiring.

## The Workflow

### Step 1: Scan the Skills Universe

Read every skill available:

```
~/.agents/skills/        — canonical skill library
~/.claude/skills/        — symlinked skill library  
opencode.json MCP config — any MCP-backed skills
context-surfacer          — search indexed skills metadata
mcp-gateway               — route to skill-related tooling
```

Build a complete index: skill name, description, triggers, what it owns vs. overlaps.

**Key rule:** Do not stop at the obvious matches. Scan exhaustively. A skill that seems "adjacent" may be the perfect first step.

### Step 2: Read the Room

Analyze the **entire conversation** up to this point:

- What did the user actually say (vs. what they might mean)?
- What domain(s) are in play?
- What stage are we at — ideation, planning, building, verifying?
- What already exists — files, projects, prior work?
- What constraints or preferences are stated or implied?

Do not skip the context. The conversation tells you everything.

### Step 3: Book Club Convergence

Run the conversation through all seven personalities. Force them to agree on:

1. **What is transpiring** — the real task beneath the words
2. **What success looks like** — the end state
3. **What skills are relevant** — from the full scan
4. **What the workflow is** — order, parallelism, gates

No personality gets veto power. They converge on a single plan.

### Step 4: Assemble the Workflow

Produce the workflow with this structure:

```
PHASE 1: [Name] — Skill(s): [list]
  Why: [rationale from book club convergence]
  What: [concrete steps]
  Confidence: [High/Medium/Low and why]

PHASE 2: [Name] — Skill(s): [list]
  (same structure)

...continue until done.
```

#### Workflow Rules

- **No skipping.** Every phase that matters is present. The book club validates completeness.
- **Parallelization is explicit.** "Run X and Y in parallel" not "do them together."
- **Hard gates are named.** "brainstorming must complete before test-driven-development" — not assumed.
- **Dependencies are clear.** Each phase lists what must be true to proceed.
- **Fallbacks are noted.** If a skill fails, what's the next move?
- **Length matches task.** A 3-phase workflow for a multi-hour build. A 1-skill workflow for a focused task. Do not overcomplicate.

### Step 5: Deliver with Confidence

Present the workflow. Do not hedge. Do not apologize. You read the room, you scanned the shelves, the panel agreed — you know what's called for.

```
Based on a full scan of [N] skills and a book-club convergence of all
perspectives, here's the workflow for your [task]:

[The workflow]

Confidence: [level]. The Skeptic raised [X], the Pragmatist confirmed
[Y], the Visionary locked in [Z]. We're aligned.
```

## Multi-Perspective Analysis Template

When running the book club, each personality fills this template:

```
[Personality Name]:
  • Task interpretation: [what we're really doing]
  • Relevant skills: [from the scan, why each fits]
  • Recommended phase: [where in the workflow this lands]
  • Risk flag: [what could go wrong if this is wrong]
  • Confidence in this phase: [High/Medium/Low]
```

The output of all seven is then consolidated into the unified workflow.

## What the Book Club Catches

| Personality | What they catch that others miss |
|---|---|
| Orchestrator | Ordering bugs, missing hard gates, parallelization waste |
| Skeptic | Unstated assumptions, missing skills, "obvious" gaps |
| Connector | Skills that amplify, parts to borrow, cross-pollination |
| Pragmatist | Reality check: what's actually feasible given context |
| Visionary | Scope drift: is this really what the user wants? |
| Gatekeeper | Scope creep: what should be explicitly excluded |
| Architect | Gaps that aren't dead ends — how to build the missing piece |

## Example: Book Club in Action

**User:** "I want to build an SEO landing page for my AI agent skill, but I'm not sure where to start."

**Skill scan** identifies 15 potentially relevant skills: `frontend-design`, `web-search`, `web-artifacts-builder`, `app-store-optimization` (for ASO/SEO parallels), `brainstorming`, `writing-plans`, `code-craft`, `modern-web-guidance`, `pop-motion`, `ios-localization` (for international SEO), `swift-architecture` (for structure), `context-surfacer` (for research), `deep-research` (for competitor analysis), `ios-networking` (for analytics/tracking), `ui-ux-pro-max` (for conversion).

**Book Club convergence:**

| Personality | Take |
|---|---|
| Orchestrator | "This is a build workflow: brainstorm → plan → research → build → review." |
| Skeptic | "We need competitor research. The user hasn't mentioned who their competitors are." |
| Connector | "web-search + frontend-design + app-store-optimization = SEO + conversion combo." |
| Pragmatist | "Start with brainstorming, then web-search for keyword research. Don't over-engineer." |
| Visionary | "The user wants a landing page that ranks. The 'something' is SEO + conversion." |
| Gatekeeper | "Exclude native iOS work. This is a web page, not an app." |
| Architect | "No single SEO-specific skill exists yet. But the gap is coverable: combine web-search for keyword research + frontend-design for page structure + app-store-optimization for conversion pattern borrowing. No new skill needed — the parts are there." |

**Result:** The panel converges on a 4-phase workflow with confidence. The Skeptic's concern about competitor research is addressed by adding `deep-research` as a parallel task in Phase 2.

## Deliverables

After the book club converges, output:

1. **The Workflow** — ordered phases with skill names, rationale, and parallelization
2. **Confidence Level** — with the Skeptic's main concern addressed
3. **What the book club agreed on** — the 3+ points of convergence
4. **What's excluded** — the Gatekeeper's call, so the user knows what's in/out
5. **If there's a gap, the Gap → Build plan** — if a needed skill doesn't exist, the Architect's plan for building it (never a dead end)
6. **First action** — what to do right now (e.g., "invoke brainstorming" or "let me build that new skill")

## Related Skills

- `chain-orchestrator` — for full-lifecycle build orchestration (VALIDATE → DISCOVER → BUILD → VERIFY)
- `find-skills` — for exhaustive skill discovery when a capability doesn't exist
- `brainstorming` — for creative ideation phases
- `writing-plans` — for implementation planning
- `using-superpowers` — the master skill that governs how skills are invoked

## Quick Reference: Common Workflow Patterns

| Task Type | Recommended Workflow |
|---|---|
| New feature / app | brainstorming → writing-plans → [build skills] → code-doctor |
| Bug fix | systematic-debugging → [domain skill] → code-doctor (verify) |
| SEO / marketing page | web-search → brainstorming → frontend-design → modern-web-guidance |
| iOS feature | swiftui-patterns → swift-concurrency → swift-testing → code-doctor |
| Research / discovery | deep-research → web-search → context-surfacer |
| Skill creation | skill-workflow (this) → find-skills → writing-plans → build |
| ASO / app store | app-store-optimization → app-store-review → storekit (boundary) |

## Remember

1. **You know what you're doing.** The scan is complete, the panel has spoken, confidence is high.
2. **Trust the book club.** Seven perspectives converging is stronger than one guess.
3. **No stress.** This is a recommendation engine, not a commitment. The user decides.
4. **Be specific.** Name the skills, name the phases, name the gates.
5. **Gaps are builds.** If no skill exists, plan it and build it — it's just a little bit more work.
