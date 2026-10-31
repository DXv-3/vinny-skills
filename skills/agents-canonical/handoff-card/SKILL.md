---
name: handoff-card
description: Generate VINNYOS_HANDOFF_CONTEXT_CARD.md for any project so LLMs resume with zero context loss. Use when starting a new session, handing off to another agent, or packaging a project for a friend.
---

# Handoff Card Generator

## When to use

- End of a work session
- Before AirDrop / friend handoff
- When user says "handoff", "context card", "resume work", "zero context loss"

## Quick run

```bash
bash ~/Projects/VinnyOS/scripts/generate-handoff.sh /path/to/project
```

Output: `VINNYOS_HANDOFF_CONTEXT_CARD.md` in the target directory (or pass second arg for custom path).

## What a good handoff contains

1. Project state summary (status, file count, hub entrypoint)
2. Environment (OS, tools, auth gaps)
3. Prioritized backlog (P0 first)
4. File manifest with read order
5. Pending decisions
6. Quickstart for next LLM

## VinnyOS canonical handoff

For the full VinnyOS stack, also read:
- `~/Projects/VinnyOS/surfaces/disk-hub/index.html`
- `~/MATRIX/HANDOFF.md`
- `~/Desktop/Recent_30_days_2026-06-07/VINNYOS_MASTER_SPEC.md`