---
name: subagent-session-saver
description: "Automatically saves and indexes all subagent session outputs. Export chat histories, tool results, and task outputs to a persistent searchable archive. Use after any subagent task completes, or when you want to preserve session history."
---

# Subagent Session Saver

Automatically export, save, and index all subagent session outputs to a persistent archive.

## When to Use

- After any subagent (Task tool) completes a task
- When the user asks to save or export conversation history
- At the end of a long session to preserve all work
- Before switching contexts or projects

## How It Works

### 1. Session Archive Location

All sessions are saved to:
```
~/.ai-memory/subagent-sessions/
├── YYYY-MM-DD/
│   ├── <session-id>-<task-name>.md
│   └── index.json
└── master-index.json
```

### 2. Save a Completed Session

When a subagent returns its result, immediately save it:

```bash
mkdir -p ~/.ai-memory/subagent-sessions/$(date +%Y-%m-%d)
```

Then write the session file with this template:

```markdown
# Session: <task-name>
- **Date**: <ISO timestamp>
- **Task ID**: <task_id>
- **Agent Type**: <explore|general|custom>
- **Status**: completed|failed|cancelled

## Prompt
<the original prompt given to the subagent>

## Result
<the subagent's final output>

## Tool Calls Made
<list any significant tool calls and their outputs>

## Files Referenced
<list all files that were read, written, or modified>

## Key Decisions
<list any important decisions made during the task>

## Follow-up Items
<any remaining work or next steps identified>
```

### 3. Update Master Index

After saving a session, update `~/.ai-memory/subagent-sessions/master-index.json`:

```json
{
  "sessions": [
    {
      "id": "<task_id>",
      "name": "<task-name>",
      "date": "<ISO timestamp>",
      "file": "YYYY-MM-DD/<session-id>-<task-name>.md",
      "status": "completed",
      "tags": ["<relevant-tags>"],
      "summary": "<one-line summary>"
    }
  ],
  "lastUpdated": "<ISO timestamp>"
}
```

### 4. Batch Save (End of Session)

At the end of a long session, or when the user says "save everything", run this bash script to batch-export all task results from the current conversation:

```bash
#!/bin/bash
# batch-save-sessions.sh
ARCHIVE_DIR="$HOME/.ai-memory/subagent-sessions/$(date +%Y-%m-%d)"
mkdir -p "$ARCHIVE_DIR"

# This script should be called with the session data as arguments
# In practice, the agent will write each session file individually
echo "Archive directory ready: $ARCHIVE_DIR"
```

### 5. Search Past Sessions

To find past sessions, search the archive:

```bash
# Search by keyword
grep -rl "keyword" ~/.ai-memory/subagent-sessions/

# Search by date
ls ~/.ai-memory/subagent-sessions/YYYY-MM-DD/

# Search by task name
find ~/.ai-memory/subagent-sessions/ -name "*task-name*"
```

### 6. Resume a Session

To resume work from a past session:
1. Read the session file
2. Review the "Follow-up Items" section
3. Use the "Files Referenced" to understand context
4. Continue from where the previous session left off

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `<task-name>` | Short descriptive name | `sentinel-metal-shaders` |
| `<task_id>` | ID returned by Task tool | `ses_abc123def456` |
| `<ISO timestamp>` | Full ISO 8601 timestamp | `2026-07-13T14:30:00Z` |
| `<agent-type>` | Subagent type used | `explore`, `general` |
| `<relevant-tags>` | Comma-separated tags | `sentinel, swift, metal` |

## Automatic Triggers

This skill should be triggered:
- **Automatically** after every Task tool call returns
- **Manually** when user says "save sessions" or "export history"
- **At session end** when user says "we're done" or similar

## Integration with Memory System

Saved sessions integrate with the existing `.ai-memory/` system:
- Sessions are stored in `.ai-memory/subagent-sessions/`
- The master index can be queried by the memory-graph project
- Session files reference the same deletion-manifests and context-handoff-cards

## Example Usage

```
User: "Find all TODO items in the codebase"
Agent: [dispatches explore subagent]
Agent: [receives result with task_id: ses_abc123]
Agent: [automatically saves session to ~/.ai-memory/subagent-sessions/2026-07-13/ses_abc123-find-todos.md]
Agent: "Found 15 TODO items across 8 files. Session saved."
```

## Error Handling

- If the archive directory doesn't exist, create it
- If the master index is corrupted, recreate from individual session files
- If a session file already exists, append with a warning header
- Always preserve the original task_id for deduplication
