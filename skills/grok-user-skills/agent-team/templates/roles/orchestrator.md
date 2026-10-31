# Human / orchestrator tab

This pane is for **you** or manual overrides.

## Watch
- `orchestrator.sh status`
- `tail -f .agent-team/events.jsonl`

## Manual control
```bash
TEAM_DIR=.agent-team ~/.grok/skills/agent-team/scripts/orchestrator.sh pause
TEAM_DIR=.agent-team ~/.grok/skills/agent-team/scripts/orchestrator.sh task "new goal"
TEAM_DIR=.agent-team ~/.grok/skills/agent-team/scripts/orchestrator.sh emit '{"type":"done","from":"human","body":"stop"}'
```

Automated turns run in the orchestrator pane (`orchestrator.sh run`).