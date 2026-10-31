---
name: agent-chat
description: >
  Turn on two-way chat between grok-build and grok-composer-2.5-fast in two terminal
  tabs. Shared .agent-chat/bus.jsonl, macOS notifications, simple CLI. Use for
  agent chat, two tabs talking, build vs composer, two-way communication, or
  /agent-chat on.
metadata:
  short-description: "Build ↔ Composer two-tab chat bus"
---

# /agent-chat — Two-way Build ↔ Composer

Minimal team mode: **two tabs, one bus, both directions.** No orchestrator loop.

## Turn it on (one command)

From your **project directory**:

```bash
agent-chat on
```

Copy the two lines it prints into **Tab 1** and **Tab 2**.

## Tab commands

| Tab | Run |
|-----|-----|
| 1 — Build | `agent-chat session build` |
| 2 — Composer | `agent-chat session composer` |

## Send messages (either tab, while Grok runs use a split or pause)

```bash
agent-chat send build "Plan: use JWT in src/auth/"
agent-chat send composer "Implemented — see src/auth/jwt.ts"
```

Messages go **build → composer** and **composer → build**. Peer gets a **macOS notification** + log entry.

## Other commands

| Command | Purpose |
|---------|---------|
| `agent-chat status` | Bus path, watchers, recent messages |
| `agent-chat tail build` | Live log in a split pane (optional) |
| `agent-chat off` | Stop watchers |

## When invoked in Grok

1. Run `agent-chat on` in the user's project cwd (shell).
2. Show the two `session` lines clearly.
3. Tell them: `agent-chat send <role> "..."` to bridge what they type in Grok to the other model.
4. Do **not** start the full `/agent-team` orchestrator unless they ask.

## Install CLI on PATH (once)

```bash
mkdir -p ~/.grok/bin
ln -sf ~/.grok/skills/agent-team/scripts/chat/agent-chat ~/.grok/bin/agent-chat
export PATH="$HOME/.grok/bin:$PATH"
```

## Files created

```
.agent-chat/
  bus.jsonl           # message log
  cwd                 # project root
  prompt-build.txt
  prompt-composer.txt
  watch-*.log
  README.txt
```

CLI path: `~/.grok/skills/agent-team/scripts/chat/agent-chat`