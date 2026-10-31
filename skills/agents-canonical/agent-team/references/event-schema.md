# Agent-team event schema

Append-only log: `.agent-team/events.jsonl` (one JSON object per line).

## Common fields

| Field | Type | Description |
|-------|------|-------------|
| `ts` | string | UTC ISO8601 (added by orchestrator) |
| `type` | string | Event kind (see below) |
| `from` | string | `human`, `build`, `composer`, `orchestrator` |
| `body` | string | Human-readable summary |
| `verdict` | string \| null | `approve`, `revise`, or null |
| `artifacts` | string[] | Paths or doc names |
| `blockers` | string[] | Non-empty when blocked |

## Event types & turn machine

| type | From | Next turn |
|------|------|-----------|
| `task` | human | `build` |
| `plan` | build | `composer` |
| `implement` | composer | `build` (increments `round`) |
| `review` | build | `composer` if `revise`, else **done** |
| `status` | any | `build` |
| `error` | any | **error** (stop) |
| `done` | human/orchestrator | **done** |

## Agent handoff format

Each automated turn must end with:

```team-event
{"type":"plan","from":"build","body":"...","verdict":null,"artifacts":[],"blockers":[]}
```

## State file

`.agent-team/state.json` — orchestrator-owned; agents read via prompts but do not edit directly.