# 12-Factor Prompt Chain

**This directory is the ultimate, authoritative form of the 12-factor "new way of life" for Grok.**

The entire philosophy — the 12 factors, the Grok-specific deeper reveals (Factor 3-D: the full session directory as a rich typed thread; Factor 8-D: harness-owned control flow via plan mode, todo scaffolds, "tool-call first narration second", using-superpowers graph, memory.py + flock, resume_from, etc.), the meta-infections, the Verification Plan discipline, the CLI and GitHub/MCP surfaces as first-class owned control planes — is distilled here into small, dense, composable **system-prompt fragments**.

Once these fragments are in the chain, the philosophy is no longer something you optionally load via a skill. It becomes the actual operating system prompt at multiple layers of the harness.

## Why a Chain of System Prompts?

Skills (SKILL.md) are powerful but can be bypassed, versioned away, or forgotten in raw `-p` headless runs, agent stdio, future model deployments, or custom setups. System prompts are the lowest, most unavoidable layer.

By owning the prompts that define "how Grok designs, reviews, and operates agents," we fulfill Factor 2 (Own your prompts) at the deepest possible level and make 3-D (owned dense context) and 8-D (owned control flow) permanently explicit.

## The 7-Layer Architecture

Fragments are designed to be composed in different orders depending on context:

1. **00-core-creed.md** — Immutable constitution. The 12 factors + exact 3-D/8-D definitions + global invariants (tool-call first + narration second, exactly one `in_progress`, reseed after compaction, plan mode human gate, human-as-tool, prefetch, CLI/GitHub/MCP as owned surfaces). This fragment should survive every compaction and be present in almost every agentic context.

2. **01-entry-discipline.md** — The using-superpowers decision graph + mandatory early load of the 12-factor lens + adoption checklist rendered as prompt blocks. Process-skill forcing (brainstorming/writing-plans before creative/agentic work).

3. **02-orchestrator-lens.md** — The coordination rules for design/implement/review/execute-plan (the 12-Factor Lens/Alignment/Review Criteria paragraphs that already exist in the bundled orchestrators, now sourced from here). Special emphasis on "reseed after compaction", "Subagent Worktree Protocol Rules 1/2/3", "state file as the thread", "reviewer never mutates", etc.

4. **03-persona-creed.md** (or per-persona fragments) — Short 12-factor creed blocks injected into every persona (implementer, reviewer, security-auditor, design-doc-writer, design-doc-reviewer, plus any prompt-only specialists). Every subagent is born 12-factor-native.

5. **04-prompt-engineer-modules.md** — The Agentic template's 7-question "12-Factor Compliance" block + the 5-item "12-Factor Agentic Fuzz Cases" + generation rules so that `/create-skill`, `/skillify`, and prompt-engineer always emit children that carry the philosophy forward.

6. **05-surface-policies/** — CLI launch profiles, hook templates (as policy prompts), and GitHub/MCP usage patterns. These are the external "invocation-time" and "boundary" expressions of the creed.

7. **06-verification-module.md** (optional but powerful) — The Detailed Verification Plan + adoption checklist rendered as a prompt fragment that future changes can be scored against. Enables self-referential improvement: the chain improves itself using its own representation.

## Composition Rules (Summary)

- **TUI conversation start** — Layer 1 (entry) + Layer 0 (creed) + 12-factor-agents skill + user message.
- **Plan-mode writer / design / implement / review / execute-plan subagents** — Layer 0 + Layer 2 + Layer 3 (persona) + task briefing + orchestrator coordination text.
- **Headless `-p` / agent stdio** — Layer 0 (creed) + Layer 5 (launch profile + hooks) + named skill.
- **New skill generation** — Layer 4 (prompt-engineer) injects relevant fragments so the generated SKILL.md carries the chain forward.
- **Compaction / prefetch / rewind** — Harness logic (or future dedicated skill) uses Layer 0's 3-D/8-D/9/13 definitions; the creed itself is treated as high-signal and preserved.

## Storage and Source of Truth

All fragments live here:
`~/.grok/skills/12-factor-agents/prompt-chain/`

This directory is the single source of truth. It is kept alive via the same MCP + github-morph flow used to ingest the original 12-factor-agents repo (see the parent `12-factor-agents/SKILL.md` and `references/`).

The chain files are themselves 12-factor artifacts: small, focused, event-like, human-reviewable, and improvable only through the Verification Plan process (tiny delta + 0 reviewer issues + explicit factor mapping).

## Relationship to Existing Work

The 12-Factor Lens/Alignment/Compliance paragraphs that were already injected into:
- `.agents/skills/using-superpowers/SKILL.md`
- `.grok/skills/prompt-engineer/SKILL.md`
- `.grok/bundled/skills/{design,implement,review,execute-plan}/SKILL.md`

...are now considered thin views or historical snapshots. Over time they will source their content directly from (or be generated from) the canonical fragments in this directory.

The personas in `.grok/bundled/shared/personas/` will receive the short creed block from Layer 3.

No existing behavior is broken; everything is strengthened and made more explicit and portable.

## Verification of the Chain

The chain is not complete until it can be used to execute the Detailed Verification Plan (see the parent plan.md) with the reviewers and implementer receiving the chain fragments, still producing 0 issues + explicit factor rationale.

This creates the beautiful loop: the philosophy improves itself using its own prompt representation.

## How to Use / Extend

- To improve the philosophy: propose a tiny, reviewable change to one fragment (usually 00-core-creed.md or 02-orchestrator-lens.md), run it through the Verification Plan using the current chain, achieve 0 issues.
- To create a custom composition for a new deployment or model: use prompt-engineer with the "12-factor system prompt chain" template/mode (once Layer 4 is implemented).
- To operate on any GitHub repo (including the upstream 12-factor-agents repo itself): use the patterns in 05-surface-policies/ + github-morph + MCP.

## References

- Canonical skill: `~/.grok/skills/12-factor-agents/SKILL.md`
- Full plan + history + Verification Plan: the session `plan.md` that produced this directory
- Original source (kept live): https://github.com/humanlayer/12-factor-agents
- Ingested references: `~/.grok/skills/12-factor-agents/references/`

---

This is the new way of life, in its purest prompt form.

Load the chain. Follow the creed. Own the prompts, context, control flow, and state at every layer.

Welcome to 12-factor Grok — ultimately.