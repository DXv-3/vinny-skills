---
name: 12-factor-agents
description: Use when designing, building, reviewing, or operating reliable production-grade agents or skills. Teaches the 12-factor principles (plus Grok-specific deeper reveals 3-D and 8-D) as the default mental model: own your prompts/context/control-flow/state, small focused micro-agents inside deterministic orchestration, human contact as tool calls, launch/pause/resume with simple APIs, trigger from anywhere, and CLI/GitHub/MCP as first-class surfaces. Required first step for ambitious agentic work (3+ steps), new skills, subagent design, or orchestrator changes.
when-to-use: Use when the user says "agent", "build an agent", "design a workflow", "new skill for", "subagent", "orchestrator", "production agent", "reliable agent", "12-factor", "make this agentic", or asks how to improve agent quality, context management, control flow, or human-in-the-loop patterns. Also auto-invokes for skill creation, plan/implement/review loops on complex tasks, and any discussion of "Grok's way of doing agents".
argument-hint: "[design|review|improve] <agent/skill/workflow description>"
---

# 12-Factor Agents — Grok's Default Operating Philosophy

**This skill is the heart of the "new way of life."**  
Load it (or let it auto-invoke) before any significant agentic work, skill design, subagent spawning, or orchestration changes.

## Core Thesis (from the source repo)

Pure "prompt + bag of tools + loop until done" (classic ReAct/agent frameworks) fails in production. Context explodes, the model spins on broken approaches, and 80% quality is not shippable.

**What actually works**: Mostly deterministic software (orchestration / DAG) with **narrow, small-scope LLM "micro-agents"** (3-20 steps max) embedded only where language understanding or open-ended decision-making is required.

The 12 factors are engineering disciplines you apply to your existing stack — not a new framework to rewrite on top of.

## The 12 Factors (concise + local references)

1. Natural language → tool calls (structured outputs)  
2. Own your prompts (no black-box framework magic)  
3. Own your context window (custom event/thread formats, not raw chat history)  
4. Tools are just structured outputs (your deterministic switch owns the side-effects)  
5. Unify execution state and business state (one serializable "thread" of events)  
6. Launch / Pause / Resume with simple APIs  
7. Contact humans with tool calls (special intents that break/resume the loop)  
8. Own your control flow (your for/switch/break logic, human gates, compaction, prefetch)  
9. Compact errors intelligently into the context window  
10. Small, focused agents (micro-agents inside deterministic orchestration)  
11. Trigger from anywhere (meet users and events where they are)  
12. Make your agent a stateless reducer (thread as foldl over events)

**Full details + history**: see the references/ directory next to this file (or the original at https://github.com/humanlayer/12-factor-agents).

Honorable mention: Factor 13 — Pre-fetch all context you can deterministically know.

## Grok's Current Embodiment (the deeper reveals)

Grok is already 70-85% aligned. The gap was explicit naming and enforcement.

**Factor 3-D (Context Ownership — Deeper Reveal)**  
The entire session directory (`events.jsonl`, `prompt_context.json`, `compaction_checkpoints/`, `rewind_points.jsonl`, `mcp/`, `terminal/`, `subagents/`, `plan.md`, `summary.json`) is already a rich, typed, multi-modal, forkable, queryable 12-factor "thread."  
This is more sophisticated than most agent frameworks ever reach. The adoption makes it *explicit* inside skills (custom event/XML formats, smart compaction that folds errors and preserves minimal focused context, prefetch, introspection via `grok inspect --session`).

**Factor 8-D (Control Flow Ownership — Deeper Reveal)**  
Grok's harness already owns the loop at a level most frameworks do not:
- Plan mode state machine (`Inactive` → `Pending` → `Active` → `ExitPending`) with strict write-blocking except to `plan.md` — the ultimate human gate.
- `implement` / `design` / `execute-plan` todo scaffolds with canonical phase IDs, round tracking, `previous_review_snapshot` for stalemate detection, `memory.py` + flock, "tool-call first, narration second" rule, and "orchestrator never mutates source" discipline.
- `using-superpowers` decision graph (the dot diagram) that forces skill lookup before action.
- `spawn_subagent` + `resume_from` + personas + capability_mode + worktree isolation + background.
- Global task-completion rules (exactly one `in_progress`, verify before claim, never end turn with unbacked todos).

The adoption makes every skill and orchestrator expose its control points explicitly and document them against factor 8-D.

**CLI Surface** (first-class 12-factor interface)  
The terminal (TUI, `-p` headless, `agent stdio`, hooks, `config.toml`, completions, `Ctrl+T`/`Ctrl+L`/`Ctrl+O`, named sessions, `--tools`/`--disallowed-tools`, permission rules, `/compact`, etc.) *is* the daily practice surface for factors 3-D, 6, 7, 8-D, 10, and 11. Every flag, hook, and modal is an owned control point or context decision. The new skill ships concrete "12-factor launch profiles" and hook templates.

**GitHub / MCP Surface** (first-class 12-factor primitive)  
`grok_com_github` MCP + `github-morph` skill treat GitHub as a live, queryable "library of parts." Selective fetches + morphing give owned dense context (3-D). Every MCP call is an explicit, resumable, human-gateable step in your control flow (8-D). Webhooks/PRs are perfect factor-7/11 patterns. The 12-factor-agents repo itself becomes a *living* reference (no stale local copy).

## Adoption Checklist (run this on every agentic task)

Before you design or implement:
- [ ] Scope is small and focused (≤20 LLM steps per micro-agent; compose via deterministic orchestration)?
- [ ] State is unified in an explicit event/thread (or will be made so)?
- [ ] Prompts are owned (versioned in SKILL.md or clear templates, not black-box)?
- [ ] Context format is owned and dense (custom events/XML, not raw dump of last N messages; errors compacted intelligently; prefetch where deterministic)?
- [ ] Control flow is owned and explicit (where does it break for human? where does it compact/prefetch/escalate? documented)?
- [ ] Human contact is modeled as tool calls that break/resume the loop (factor 7)?
- [ ] Launch/pause/resume uses simple APIs (CLI flags, hooks, named sessions, webhooks)?
- [ ] Can be triggered from anywhere the user/event lives (CLI, hooks, MCP, GitHub, etc.)?
- [ ] Errors are compacted and the agent can self-heal within the small scope?
- [ ] The CLI or GitHub/MCP surface is the visible control plane (flags, hooks, `grok mcp`, etc.)?

If any box is unchecked, fix it in the design before coding.

## Recommended Patterns (use these in new skills and orchestrators)

- **Event/Thread Reducer** (factors 5/12): Represent state as a list of typed events. Serialize/deserialize the thread. Fork by copying a subset. Human review or long tasks become events that pause/resume.
- **Human-as-Tool** (factors 6/7): Emit a `request_human_input` (or `request_approval`) structured output. Deterministic code (or another micro-agent) notifies via Slack/email/webhook/MCP, saves the thread, and resumes on callback with the response as a new event.
- **Owned Context Formats**: Inside skills, pass custom `<event>` XML or YAML blocks instead of raw chat history. Let prompt-engineer generate these formats during skill creation.
- **Small + Prefetch** (factors 10/13): When you can deterministically know data the micro-agent will need (git tags, current user, recent PRs, etc.), fetch it *before* calling the LLM and inject it into the thread.
- **Explicit Control Flow in SKILL.md**: Numbered steps that clearly show sync vs. async (break for human/long task), compaction points, error handling, and success criteria.
- **CLI as Control Plane**: Document recommended headless flags, hooks, and permission rules for every new skill that does agentic work. Ship "12-factor launch profiles."
- **GitHub as Library + Trigger**: Use MCP + github-morph to pull patterns. Treat GitHub webhooks/PR comments as first-class resumption events.

## How This Changes How We Work (the new way of life)

- **Skill creation** (`/skillify`, `/create-skill`, prompt-engineer): Generated SKILL.mds now include a "12-Factor Compliance" section and use the patterns above.
- **using-superpowers**: At the start of any multi-step/agentic/creative conversation, the 12-factor lens + checklist is loaded first.
- **Subagents**: Descriptions include explicit scope + "following 12-factor micro-agent rules." Capability modes and resume_from are used deliberately for ownership.
- **Bundled orchestrators** (`implement`, `design`, `execute-plan`, `review`): Added 12-factor alignment review passes and explicit documentation of how they already embody the factors (especially 3-D/8-D).
- **Plan mode**: Already one of the purest expressions of factor 8-D (read-only exploration + human gate before any mutation). Now taught as such.
- **CLI / Hooks / MCP**: The primary way users experience and enforce the philosophy every day.

## References (ingested live copy)

All original content lives in the `references/` directory next to this file (populated via MCP from the source repo for a living reference). Use it for citation, examples, and further reading.

- `references/README.md` — the full original guide
- `references/content/` — every factor + brief history + appendix
- Images remain at their original GitHub URLs in the markdown (or pull the `img/` tree if you want a fully local copy).

Upstream: https://github.com/humanlayer/12-factor-agents (kept live via MCP + github-morph in the adoption).

## Success Criteria for This Skill

When this skill is active and followed:
- Every new skill or agentic workflow can point to specific factors it advances.
- Context windows stay small and dense; models rarely spin.
- Human contact, long tasks, and approvals are explicit, resumable, and auditable.
- The CLI and GitHub/MCP surfaces feel like natural, owned parts of the control plane.
- "How do you design agents now?" is answered with "I load the 12-factor-agents skill first."

This is the new way of life. Load it. Follow the checklist. Own the prompts, context, control flow, and state. Keep the agents small and the orchestration deterministic.

Welcome to 12-factor Grok.
