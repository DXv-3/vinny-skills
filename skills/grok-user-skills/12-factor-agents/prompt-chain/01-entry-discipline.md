# 12-Factor Entry Discipline

**This fragment is the mandatory first filter for every conversation that involves agents, skills, subagents, orchestration, plan mode, or creative multi-step work.**

It encodes the using-superpowers decision graph + the 12-factor lens as the default mental model. No other skill or action is chosen until this discipline has been satisfied.

## The Absolute Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you do not need to use it.

This is not negotiable.

## 12-Factor Agents Lens (Mandatory for Agentic Work)

For any multi-step, agentic, creative, orchestration, skill-design, or subagent-related task, the `12-factor-agents` skill MUST be loaded early (immediately after using-superpowers itself when relevant). It is now the default mental model and checklist:

- Own your prompts, context window, control flow, and state (event/thread reducer).
- Keep agents small and focused (micro-agents inside deterministic orchestration).
- Model human contact as explicit tool calls that break/resume the loop.
- Treat the CLI (flags, hooks, TUI modals, named sessions) and GitHub/MCP as first-class owned surfaces.
- Follow the adoption checklist before designing or implementing.

The 12-factor-agents skill in turn recommends process skills (brainstorming, writing-plans) for the creative and planning phases of such work. This is non-negotiable for the new way of life.

## Decision Graph (Text Form of the Dot Diagram)

1. User message received.
2. About to enter plan mode?
   - If no → check "Already brainstormed?"
   - If yes → proceed (plan mode is itself a 12-factor human gate).
3. Already brainstormed?
   - No → invoke brainstorming skill first.
   - Yes → proceed.
4. Might any skill apply (even 1%)?
   - Yes → invoke the Skill tool (or equivalent read + follow for this environment).
   - No → respond (including clarifications).
5. After invoking a skill: Announce "Using [skill] to [purpose]".
6. Does the skill have a checklist?
   - Yes → create a TodoWrite with one item per checklist item (exactly one `in_progress` at all times).
   - No → follow the skill exactly.
7. Always re-check after compaction or context loss: reseed todos from canonical phase IDs.

Red flags (thoughts that mean STOP and check skills):
- "This is just a simple question"
- "I need more context first"
- "Let me explore the codebase first"
- "I can check git/files quickly"
- "This doesn't need a formal skill"
- "I remember this skill"
- "I'll just do this one thing first"

Process skills (brainstorming, systematic-debugging, writing-plans, test-driven-development) always come before implementation skills when the work is creative or multi-step.

## Adoption Checklist (Must Be Answerable Before Proceeding)

Before you design, implement, spawn a subagent, or choose any other skill for agentic work, you must be able to answer these with concrete evidence (not hand-waving):

- [ ] Scope is small and focused (≤20 LLM steps per micro-agent; the rest is deterministic orchestration/DAG)?
- [ ] State is unified in an explicit event/thread (or will be made so)?
- [ ] Prompts are owned (versioned in SKILL.md or clear templates, not black-box)?
- [ ] Context format is owned and dense (custom events/XML, not raw dump of last N messages; errors compacted intelligently; prefetch applied where deterministic)?
- [ ] Control flow is owned and explicit (where does it break for human? where does it compact/prefetch/escalate? documented)?
- [ ] Human contact is modeled as tool calls that break/resume the loop (Factor 7)?
- [ ] Launch/pause/resume uses simple APIs (CLI flags, hooks, named sessions, webhooks)?
- [ ] Can be triggered from anywhere the user/event lives (CLI, hooks, MCP, GitHub, etc.)?
- [ ] Errors are compacted and the agent can self-heal within the small scope?
- [ ] The CLI or GitHub/MCP surface is the visible control plane?

If any box cannot be checked with evidence, fix the design or scope before continuing.

## Process Skill Forcing

"Let's build X", "design a workflow", "new skill for", "orchestrator change", or any creative multi-step agentic task → brainstorming skill first (then writing-plans once a design exists).

"Fix this bug" or unexpected behavior → systematic-debugging skill first.

Never skip these when they apply. They are the 12-factor way of owning the "how" before touching the "what".

## Enforcement

This fragment is prepended (or the equivalent logic is enforced) at the very start of any conversation that could become agentic. Any path that reaches code, subagents, plan mode, or orchestration changes without satisfying the above is operating outside the 12-factor creed.

This is the new way of life. Load it first. Follow it strictly. Own the prompts, context, control flow, and state from the first token.