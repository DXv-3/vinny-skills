---
name: inventory-manager
description: >
  Manage VinnyOS live inventory kit — BRAIN freshness, until_read loop start/stop,
  micro bites, doctor health, stage-list (never deletes). FREE-FIRST.
  Use when: inventory status, is the loop running, manage inventory, BRAIN,
  until_read, micro 10, stage duplicates, inventory agent, /inventory-manager.
---

# Inventory Manager

## Kit
`~/VinnyOS-Ecosystem/INVENTORY-2026-07-25/`

## Always run first
```bash
~/VinnyOS-Ecosystem/INVENTORY-2026-07-25/bin/inventory manage report
```

## Commands
| Intent | Command |
|--------|---------|
| Status + next step | `inventory manage report` |
| Health / stuck? | `inventory manage doctor` |
| Keep reading computer | `inventory manage ensure` or `start` |
| Stop background robot | `inventory manage stop` |
| One batch of 10 | `inventory manage tick` |
| Show BRAIN | `inventory brain` |
| Dup proposals only | `inventory stage-list` |

## Rules
- NEVER delete/move user files
- FREE-FIRST
- If loop running and log fresh, don't restart
- Explain in plain English

## Agent persona
Full prompt: `~/VinnyOS-Ecosystem/INVENTORY-2026-07-25/agents/inventory-manager.md`
