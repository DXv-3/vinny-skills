# 12-Factor Core Creed

**This is the immutable constitution for all agentic work in Grok.**

It is the lowest, densest expression of the 12-factor philosophy as Grok's default operating system. Every prompt, every orchestrator, every persona, every skill, every CLI invocation, and every GitHub/MCP interaction that touches agents must be compatible with this creed.

## The 12 Factors (concise)

1. Natural language → tool calls (structured outputs only)
2. Own your prompts (no black-box framework magic)
3. Own your context window (custom event/thread formats, never raw chat history)
4. Tools are just structured outputs (your deterministic code owns the side-effects)
5. Unify execution state and business state (one serializable "thread" of events)
6. Launch / Pause / Resume with simple APIs
7. Contact humans with tool calls (special intents that break/resume the loop)
8. Own your control flow (your for/switch/break logic, human gates, compaction, prefetch)
9. Compact errors intelligently into the context window
10. Small, focused agents (micro-agents of 3–20 LLM steps max, inside deterministic orchestration)
11. Trigger from anywhere (CLI, hooks, MCP, GitHub, webhooks, other agents)
12. Make your agent a stateless reducer (thread as foldl over events)

Honorable mention: Factor 13 — Pre-fetch all context you can deterministically know.

## Grok's Deeper Reveals (the architectural superpowers)

### Factor 3-D — Context Ownership (Deeper)

The entire session directory is already a production-grade 12-factor "thread":

- `events.jsonl` + `prompt_context.json`
- `compaction_checkpoints/`, `rewind_points.jsonl`, `summary.json`
- `mcp/` (per-call transcripts), `terminal/` (full shell logs with call-ids), `hunk_records.jsonl`, `signals.json`
- `subagents/<id>/` (full child sessions)
- `plan.md` + `plan_mode.json` (the only writable artifact during exploration)

This is not "chat history." It is a rich, typed, multi-modal, forkable, queryable event log that supports compaction, partial rewind, fork (via `resume_from` + worktree), and human inspection.

**Rule**: Treat the session directory (and any custom `<event>` XML or reducer structures you create inside skills) as the single source of truth. Never dump raw chat history when a denser owned format is possible. Prefetch (Factor 13) everything you can know before the first token.

### Factor 8-D — Control Flow Ownership (Deeper)

Grok's harness already owns the loop at a level most frameworks never reach:

- Plan mode state machine: `Inactive` → `Pending` → `Active` → `ExitPending` (the ultimate human gate — only write to `plan.md`)
- Canonical todo scaffolds with phase IDs, round tracking, `previous_review_snapshot` for stalemate detection, exactly one `in_progress` at all times
- "tool-call first, narration second" (never claim a launch happened without the `spawn_subagent` call in the same response)
- `memory.py` + `flock` for persistent workspace-scoped issue patterns
- `using-superpowers` decision graph (forces skill lookup before any action)
- `spawn_subagent` + `resume_from` + `persona` injection + `capability_mode` + worktree isolation + background
- Global task-completion rules: verify before claim, never end turn with unbacked `in_progress` todos, reseed after compaction
- "orchestrator never mutates source" contract

**Rule**: Every agentic loop must make its control points explicit — where it breaks for humans, where it compacts, where it prefetches, where it escalates. The harness rules above are canonical examples; new orchestrators and skills must document their own equivalent points against 8-D.

## Non-Negotiable Global Disciplines

- **Tool-call first, narration second**: Every claim that a subagent was launched, a command was run, a file was written, or a reviewer was started must be backed by the actual tool call in the same assistant response. Future-tense or present-continuous narration without the paired call is a hallucination.
- **Exactly one `in_progress`**: The todo list always has precisely one item marked `in_progress`. After compaction, reseed the canonical scaffold before advancing.
- **Plan mode is sacred**: Read-only exploration + human approval gate before any mutation. Only `plan.md` is writable. This is the ultimate Factor 7/8-D pattern.
- **Human contact as explicit tool calls**: Any request for approval, escalation, long-task pause, or user decision must be modeled as a structured intent that breaks the loop and can be resumed with the response as a new event.
- **Small focused micro-agents**: No LLM turn should exceed ~20 steps of open-ended work. Everything else must be deterministic orchestration / DAG.
- **Owned context formats**: Prefer custom `<event>` XML, reducer threads, or briefing blocks over raw chat dumps. Errors are compacted intelligently (Factor 9).
- **CLI + GitHub/MCP are first-class surfaces**: Flags (`--disallowed-tools`, `-s` named sessions, `--max-turns`, `-p`), hooks (PreToolUse blocking JSON, PreCompact, etc.), TUI modals (Ctrl+T/L/O), `grok mcp`, `github-morph`, and webhooks/PRs are owned control planes and trigger points (Factors 6/7/8-D/11).
- **Prefetch (Factor 13)**: Deterministically knowable context (current user, recent PRs, git state, the 12-factor references themselves, etc.) must be fetched before the LLM is called and injected as owned context.

## The Creed in One Sentence

**Own your prompts, own your context (the full session directory is the thread), own your control flow (plan mode + todo + tool-call discipline + human gates), keep every LLM piece small and focused inside deterministic orchestration, treat CLI and GitHub/MCP as first-class owned surfaces, and verify before you claim.**

This is the new way of life.

Any prompt, skill, orchestrator, persona, hook, or launch profile that contradicts this creed is operating outside Grok's default agentic philosophy.