# Agent Team — Master Specification

**Build Watch:** `cd ~/.grok/skills/agent-team && build-watch on` → **Open a file** → `AGENT-TEAM-MASTER-SPEC.md` (or `handoffs/agent-team.MASTER-SPEC.md`)

**Version:** 1.0  
**Date:** 2026-06-05  
**Status:** Phase 1 operational; Phase 2 designed, not implemented

This document consolidates the full arc of the agent-team initiative: from terminal-tab coordination through multi-model teamwork, architectural critique, and the shipped minimal chat bus. It is the single source of truth for intent, design, and operation.

---

## 1. Executive Summary

The goal is to run **grok-build** and **grok-composer-2.5-fast** as a coordinated engineering team: better outcomes through role separation, hands-off automation when desired, scale-out to additional specialists, and room to experiment—without sacrificing the ability to **move fast safely** (auto-approve inside guardrails, nothing destructive on main until you choose).

**Core insight:** Terminal tabs do not communicate natively. Coordination requires a **shared bus** and an explicit **control plane**. Tabs are optional monitors; the bus and orchestrator are the system.

**What ships today:** **`agent-chat`** — two terminal tabs, one append-only message log (`.agent-chat/bus.jsonl`), background watchers, macOS notifications, and a single CLI (`agent-chat on` → two `session` commands → `send`).

**What is designed next:** A **Grok-native orchestrator** (one session, `spawn_subagent`, worktree isolation, permission tiers, human merge gates) that supersedes the bash turn-loop for automation and scale-out. The bash orchestrator and full `/agent-team` loop remain a secondary path for unattended/CI experimentation.

---

## 2. Problem Statement

| Need | Implication |
|------|-------------|
| Two models with different strengths | Build plans/reviews; Composer implements |
| Visible “team” (optional) | Two tabs or tmux panes, not magic IPC |
| Two-way dialogue | Bidirectional message bus, not one-shot FIFO |
| Automation (later) | Deterministic turn machine, not model-owned loop |
| Scale-out (later) | Security, tests, docs as additional subagents |
| Safety | Auto inside sandbox; human fuse before merge/destructive ops |
| R&D | Auditable event log, forkable patterns |

**Anti-pattern:** Treating tabs as the coordination layer, or granting `bypassPermissions` in unattended loops.

---

## 3. Architectural Principles (12-Factor Alignment)

1. **Own control flow** — Orchestrator (bash script or Grok session) decides whose turn it is; models emit structured handoffs, not free-form chat as state.
2. **Own context** — Dense event log + role prompts; not full chat history replayed every turn.
3. **Small micro-agents** — One role per invocation; compose via orchestration.
4. **Unified thread** — `events.jsonl` (and Grok session `events.jsonl` when native).
5. **Human as tool** — Pause, approve plan, approve merge; configurable gates.
6. **Mutations in worktrees** — Main workspace untouched until explicit apply.
7. **CLI as control plane** — `agent-chat`, `agent-team` scripts, Grok skills.

Grok already embodies much of this via `/implement`, `spawn_subagent`, `resume_from`, session directories, and `fork_secondary_model = grok-build` with default Composer.

---

## 4. System Evolution (Session Arc)

```text
Terminal tab IPC?  →  FIFO/socket/tmux (generic)
        ↓
Multi-tab agent team  →  events.jsonl + orchestrator (bash headless grok -p)
        ↓
Brainstorm A+C+D+E + safety  →  Native Grok orchestrator recommended over bash brain
        ↓
User pivot: "just two talking"  →  agent-chat MVP (bus only, no turn loop)
        ↓
Package + run  →  agent-chat CLI, .agent-chat/ in project (or ~)
```

**Lesson:** The bash orchestrator duplicated harness capabilities, used cold headless turns, fragile `team-event` fence parsing, and unsafe permission bypass. It is valid for audit trails and CI experiments, not the primary team experience.

**Lesson:** Fully autonomous dialogue between two **live Grok TUIs** is awkward; the practical MVP is **bus + notify + human/Grok bridge via `send`**, with optional relay later.

---

## 5. Current System — `agent-chat` (Phase 1)

### 5.1 Purpose

Open **two-way** communication between Build and Composer in two terminal tabs. No automated turn-taking. User (or Grok in each tab) bridges content onto the bus.

### 5.2 Components

| Component | Location / command |
|-----------|-------------------|
| CLI | `~/.grok/skills/agent-team/scripts/chat/agent-chat` → `~/.grok/bin/agent-chat` |
| Skill | `~/.grok/skills/agent-chat/SKILL.md` — invoke `/agent-chat on` |
| Bus | `<project>/.agent-chat/bus.jsonl` |
| Project anchor | `<project>/.agent-chat/cwd` |
| Role prompts | `prompt-build.txt`, `prompt-composer.txt` |
| Watchers | Background `watcher.sh` per role; PID in `watch-<role>.pid` |
| Logs | `watch-<role>.log` |
| Skill cross-ref | `agent-team/SKILL.md` links here before full orchestrator |

### 5.3 Message Schema (bus)

One JSON object per line:

```json
{
  "from": "build | composer | human",
  "to": "build | composer | all",
  "body": "string",
  "ts": "ISO8601 UTC"
}
```

Routing: `send build "…"` → `from: build`, `to: composer`. `send composer "…"` → reverse. `send all` → broadcast.

### 5.4 Turn-On Procedure (canonical)

**Once per machine:**

```bash
brew install jq
mkdir -p ~/.grok/bin
ln -sf ~/.grok/skills/agent-team/scripts/chat/agent-chat ~/.grok/bin/agent-chat
echo 'export PATH="$HOME/.grok/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**Every session:**

```bash
cd /path/to/project
agent-chat on
```

**Tab 1:** `agent-chat session build`  
**Tab 2:** `agent-chat session composer`

**Bridge:**

```bash
agent-chat send build "…"
agent-chat send composer "…"
```

**Off:** `agent-chat off`

### 5.5 Best Experience

- Same `cd` in both tabs.
- Enable macOS notifications for Terminal/Cursor.
- Optional split below Grok: `agent-chat tail build` / `tail composer`.
- In Grok: reference `.agent-chat/bus.jsonl`; ask model to draft the next `send` line.
- Review diffs on disk before trusting Composer; chat does not enforce worktrees.

### 5.6 Limitations (accepted in Phase 1)

- No automatic relay between TUIs (user or Grok runs `send`).
- No worktree enforcement.
- No review loop or merge gate.
- Watchers notify; they do not inject into Grok TUI (avoids corrupting alternate-screen UI).

---

## 6. Designed System — Full Team (Phase 2)

### 6.1 Purpose

Deliver goals **A** (quality), **C** (hands-off), **D** (scale-out), **E** (R&D) with **safety**: fast inside boundaries, reversible by design.

### 6.2 Recommended Architecture: Grok-Native Orchestrator

```text
Human / orchestrator session (coordinator only — no direct source edits)
    │
    ├─► subagent [build]      model: grok-build       plan, review
    ├─► subagent [composer]  model: composer-2.5     implement (worktree)
    ├─► subagent [security]  optional
    └─► subagent [tests]     optional

State: Grok session thread (primary) + mirror → .agent-team/events.jsonl (audit)
Mutations: worktree only until human apply/merge
```

Align with `/implement`: tool-call-first, personas via prompt prefix, `resume_from`, bracketed descriptions for pager labels.

### 6.3 Safety Model (approved direction)

| Layer | Policy |
|-------|--------|
| **Worktree default** | All implementation in isolated worktree |
| **Auto-approve** | Reads, search, tests, edits inside worktree |
| **Never auto** | `rm -rf`, `git push --force`, `git clean -fd`, writes outside worktree, `~/.ssh`, `.env` |
| **Profiles** | `safe` (default), `fast`, `paranoid` — configurable per run |
| **Human gates** | Optional plan approve; **merge/apply to main** default-on |
| **Done** | Review subagent `approve` → diff summary → human apply |
| **Retired** | `bypassPermissions` in team automation |

### 6.4 Permission / Gate Matrix (target)

| Profile | In worktree | Merge to main | Destructive shell |
|---------|-------------|---------------|-------------------|
| safe | auto | ask | deny |
| fast | auto | ask | deny |
| paranoid | ask | ask | deny |

Configurable: `--gates plan,merge` per run.

### 6.5 Relation to Existing `/agent-team` Bash Orchestrator

The shipped bash `orchestrator.sh` implements:

- State: `.agent-team/state.json` (`turn`, `round`, `max_rounds`, `models`)
- Events: `.agent-team/events.jsonl` with types `task`, `plan`, `implement`, `review`, `status`, `error`, `done`
- Turn machine: plan → composer → implement → build → review (approve/revise)
- Headless `grok -p` per step; `team-event` fenced JSON handoff
- Optional `launch-tmux.sh` (4 panes: orchestrator loop, tail, build, composer)

**Disposition:** Keep for headless/CI/R&D; **do not** position as primary UX. Phase 2 skill should orchestrate via Grok harness, optionally mirror events to the same JSONL schema for continuity.

---

## 7. Future System — DAG Network (Phase 3)

Decompose work as a small DAG: `plan → implement → test → security → review → merge`. Each node is a micro-agent; edges may require human approval. Best for scale-out (**D**) and topology experiments (**E**). **Prerequisite:** Phase 2 loop stable with safety rails.

---

## 8. Comparative Approach Matrix

| Approach | Best for | Weakness |
|----------|----------|----------|
| Tab paste / FIFO | Quick hack | No structure, not scalable |
| **agent-chat bus** | **Two-way tab dialogue now** | Manual/auto relay bridge |
| Bash + events.jsonl orchestrator | Unattended experiment, audit | Cold context, fragile parse, permission risk |
| **Grok subagent orchestrator** | **Quality, automation, safety, scale** | Less “two terminals as people” unless tailed |
| `/implement` (bundled) | Single-session implement/review | Not branded as Build/Composer team |
| `grok agent leader` | One agent, many UIs | Wrong pattern for multi-model team |
| tmux dashboard | Visibility | Optional; not required |

**Strategic stack:** Use **agent-chat** daily for collaborative dialogue; graduate to **Grok-native team skill** for unattended guarded runs; use **`/implement`** when a single-session review loop suffices.

---

## 9. Event Schemas (consolidated)

### 9.1 Chat bus (Phase 1)

See §5.3.

### 9.2 Team orchestrator bus (Phase 2 bash / mirror)

| type | from | Next turn / effect |
|------|------|-------------------|
| task | human | build |
| plan | build | composer |
| implement | composer | build; increment round |
| review | build | done if approve; else composer |
| status | any | build |
| error | any | stop |
| done | human/orchestrator | stop |

Agent handoff (bash path): fenced block `team-event` with JSON `{type, from, body, verdict, artifacts, blockers}`.

---

## 10. Operational Reference

### 10.1 Chat commands

| Command | Action |
|---------|--------|
| `agent-chat on` | Init bus, start watchers, print tab commands |
| `agent-chat session build` | Watcher + `grok -m grok-build` + role rules |
| `agent-chat session composer` | Watcher + `grok -m grok-composer-2.5-fast` + role rules |
| `agent-chat send <role\|all> "msg"` | Append to bus; route to peer |
| `agent-chat status` | Paths, PIDs, recent events |
| `agent-chat tail <role>` | Follow watch log |
| `agent-chat off` | Stop watchers |

### 10.2 Team orchestrator commands (secondary)

| Command | Action |
|---------|--------|
| `orchestrator.sh setup [task]` | Scaffold `.agent-team/` |
| `orchestrator.sh step` | One headless turn |
| `orchestrator.sh run [--sleep N]` | Loop until done/error/max_rounds |
| `orchestrator.sh task "…"` | Reset task, turn=build |
| `orchestrator.sh pause` / `resume` | Halt/continue |
| `launch-tmux.sh` | 4-pane dashboard (requires tmux) |

### 10.3 Grok skills

| Skill | Use |
|-------|-----|
| `/agent-chat on` | Phase 1 two-tab chat |
| `/agent-team …` | Full orchestrator mode (bash) |
| `/implement` | Single-session implement + review swarm |
| `12-factor-agents` | Design discipline for Phase 2+ |

### 10.4 Models (this environment)

| Role | Model ID |
|------|----------|
| Composer (default) | `grok-composer-2.5-fast` |
| Build | `grok-build` |
| Config fork | `fork_secondary_model = grok-build` in `~/.grok/config.toml` |

---

## 11. File Layout (repository of record)

```text
~/.grok/skills/agent-chat/SKILL.md
~/.grok/skills/agent-team/
  SKILL.md
  references/
    AGENT-TEAM-MASTER-SPEC.md    ← this document
    event-schema.md
  scripts/
    setup-team.sh
    orchestrator.sh
    launch-tmux.sh
    lib/common.sh
    chat/
      agent-chat                  ← Phase 1 CLI
      watcher.sh
      lib.sh
  templates/
    roles/build.md, composer.md, orchestrator.md
    state.json

<project>/.agent-chat/          ← Phase 1 runtime
<project>/.agent-team/          ← Phase 2 bash runtime
```

---

## 12. Success Criteria

### Phase 1 (done when)

- [x] `agent-chat on` + two `session` commands documented and usable
- [x] Bidirectional `send` with notifications
- [x] Bus persisted under project (or user home for ad hoc)
- [ ] User completes one real task with plan (Build) → implement (Composer) → review (Build) via bus

### Phase 2 (done when)

- [ ] Orchestrator session spawns Build/Composer subagents with worktree isolation
- [ ] Permission profiles enforced; no bypass in automation
- [ ] Human merge gate before main applies
- [ ] Events mirrored to JSONL for audit
- [ ] Bash loop deprecated or wired as `agent-team --engine bash` fallback

### Phase 3 (done when)

- [ ] Optional DAG with security/tests nodes
- [ ] Configurable gates per run

---

## 13. Anti-Patterns (do not)

1. **Tabs as IPC** — Always use bus + control plane.  
2. **bypassPermissions** in automated team runs.  
3. **Orchestrator implements** — Coordinator spawns only.  
4. **Full context reload** every turn when harness provides subagent resume.  
5. **Skipping merge review** while claiming safety.  
6. **Expanding to DAG** before two-model loop is trustworthy.

---

## 14. Glossary

| Term | Meaning |
|------|---------|
| **Bus** | Append-only JSONL message log |
| **Build** | grok-build role: plan, review |
| **Composer** | grok-composer-2.5-fast role: implement |
| **Orchestrator** | Deterministic controller of turns (bash or Grok session) |
| **Watcher** | Background process tailing bus; notifies peer role |
| **Relay** | (Future) Auto `grok -p` on inbound bus message |
| **Apply** | Human-confirmed promotion of worktree changes to main |

---

## 15. One-Page Quick Start (canonical)

```bash
# Once
brew install jq
ln -sf ~/.grok/skills/agent-team/scripts/chat/agent-chat ~/.grok/bin/agent-chat
export PATH="$HOME/.grok/bin:$PATH"

# Every task
cd your-project && agent-chat on
# Tab 1: agent-chat session build
# Tab 2: agent-chat session composer
agent-chat send build "plan: …"
agent-chat send composer "done: …"
agent-chat off
```

For automation with safety, Phase 2 will add a Grok-native `/agent-team` orchestrator; until then, pair **agent-chat** dialogue with manual `git diff` and optional **`/implement`** for gated review.

---

*End of master specification.*