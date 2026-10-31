---
name: agent-team
description: >
  Multi-model agent team via shared events.jsonl and a deterministic orchestrator.
  Runs grok-build (plan/review) and grok-composer-2.5-fast (implement) in turn,
  with optional tmux dashboard. Scaffolds .agent-team/, runs orchestrator.sh step|run,
  and launches tmux panes. Use for agent team, multi-tab agents, build vs composer,
  tmux team, events.jsonl coordination, or /agent-team.
metadata:
  short-description: "Build + Composer team bus (tmux + events.jsonl)"
---

# /agent-team — Multi-model team bus

## Quick: two-tab chat (start here)

For **open two-way talk** between Build and Composer (no automation loop):

```bash
agent-chat on
# Tab 1: agent-chat session build
# Tab 2: agent-chat session composer
# Send:  agent-chat send build "…"  /  agent-chat send composer "…"
```

See skill **`agent-chat`** (`/agent-chat on`).

---

## Full orchestrator mode

Deterministic orchestration (12-factor control flow) with two Grok micro-agents:

| Role | Model | Job |
|------|-------|-----|
| **build** | `grok-build` | Plan, review, approve/revise |
| **composer** | `grok-composer-2.5-fast` | Implement, test, report |

Coordination is **not** tab-to-tab chat. All agents read/write `.agent-team/events.jsonl`; `orchestrator.sh` owns turns and state.

Scripts live at: `~/.grok/skills/agent-team/scripts/`

## Usage

`/agent-team <task description>`

Variants:

- `/agent-team setup` — scaffold only (no run)
- `/agent-team run <task>` — setup + automated loop
- `/agent-team tmux <task>` — setup + attach tmux dashboard (requires `tmux`)

## When invoked — do this

1. **Parse** task text from the user message (required unless subcommand is `setup`).

2. **Scaffold** (from project cwd — where the user is working):

```bash
SKILL=~/.grok/skills/agent-team/scripts
"$SKILL/setup-team.sh" --cwd "$(pwd)" --task "<TASK>"
```

3. **Tell the user** the team directory: `.agent-team/` and how to watch:

```bash
"$SKILL/orchestrator.sh" status
tail -f .agent-team/events.jsonl
```

4. **Run mode** (default unless user asked setup-only):

```bash
# Foreground loop (good for one terminal tab)
"$SKILL/orchestrator.sh" run --sleep 5
```

Or **tmux** if installed and user wants the dashboard:

```bash
brew install tmux   # if missing — only suggest if launch fails
"$SKILL/launch-tmux.sh"
```

5. **Do not** manually alternate copy-paste between tabs unless the user is debugging. The orchestrator owns the turn machine.

6. On **completion** (`status` = `done`, `error`, or `max_rounds`), summarize:
   - final `task`
   - last `review` / `implement` events
   - paths under `.agent-team/runs/` for logs
   - suggest `git diff` in project cwd

## Commands reference

| Command | Action |
|---------|--------|
| `orchestrator.sh setup [task]` | Create `.agent-team/` |
| `orchestrator.sh task "..."` | New task, reset to build |
| `orchestrator.sh step` | One agent turn |
| `orchestrator.sh run [--sleep N]` | Loop until done |
| `orchestrator.sh status` | State + recent events |
| `orchestrator.sh pause` / `resume` | Halt / continue automation |
| `orchestrator.sh emit '<json>'` | Manual event |
| `launch-tmux.sh` | 4-pane tmux (orchestrator, tail, build, composer) |

## Tmux layout (optional)

```
┌─────────────────┬─────────────────┐
│ orchestrator    │  events tail    │
│ (run loop)      │                 │
├─────────────────┼─────────────────┤
│ grok-build      │ composer        │
│ (manual)        │ (manual)        │
└─────────────────┴─────────────────┘
```

Install tmux: `brew install tmux`

## Customization

After setup, edit:

- `.agent-team/roles/build.md`
- `.agent-team/roles/composer.md`
- `.agent-team/state.json` — `max_rounds`, `models`, `task`

Event schema: `references/event-schema.md` in the skill folder.

## 12-factor compliance

- **Owned state**: `events.jsonl` + `state.json` thread
- **Owned control flow**: orchestrator turn machine (not model-decided)
- **Small agents**: one role per headless `grok -p` call
- **Human gate**: `pause`, manual `emit`, or stop tmux

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Missing `team-event` block | Re-run `step`; check `.agent-team/runs/*.txt` |
| `tmux not found` | `brew install tmux` or use `orchestrator.sh run` in one tab |
| Wrong directory | `TEAM_DIR=/path/.agent-team orchestrator.sh status` |
| Stuck loop | `orchestrator.sh pause` then `emit '{"type":"done","from":"human","body":"stop"}'` |

## Success criteria

- `.agent-team/` exists with `events.jsonl` and `state.json`
- At least one full cycle: `plan` → `implement` → `review` (or clear error in log)
- User knows how to watch events and open tmux if used