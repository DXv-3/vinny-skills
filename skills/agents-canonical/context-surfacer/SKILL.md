---
name: context-surfacer
description: "Search all data sources on this Mac. Sessions, files, knowledge base, state, octopus journal, skills, code, opencode, hermes, subagent sessions. One query, unified ranked results. MCP server included."
---
# Context Surfacer

Search everything you've built, written, or discussed. One command.

## Usage

```bash
# Standard search
python3 ~/.claude/skills/context-surfacer/surf.py "your query"

# Quick search (4 sources only)
python3 ~/.claude/skills/context-surfacer/surf.py "your query" --depth quick

# Deep search (all sources + follow threads)
python3 ~/.claude/skills/context-surfacer/surf.py "your query" --depth deep

# Filter to specific source
python3 ~/.claude/skills/context-surfacer/surf.py "your query" --source sessions

# JSON output
python3 ~/.claude/skills/context-surfacer/surf.py "your query" --json

# Find sessions mentioning a file
python3 ~/.claude/skills/context-surfacer/surf.py --related ~/path/to/file.py
```

## Daily Brief

Run daily to see what needs updating:

```bash
python3 ~/.claude/skills/context-surfacer/daily_brief.py
```

Shows freshness status for all sources and lists specific actions to take.

## Feed new sessions

```bash
# Dry run (parse but don't write)
python3 ~/.claude/skills/context-surfacer/sources/session_feeder.py --dry-run

# Feed all new sessions
python3 ~/.claude/skills/context-surfacer/sources/session_feeder.py

# Force re-feed (ignore hash cache)
python3 ~/.claude/skills/context-surfacer/sources/session_feeder.py --force

# Rebuild file→session back-links
python3 ~/.claude/skills/context-surfacer/sources/session_feeder.py --rebuild-links

# Feed subagent sessions
python3 ~/.claude/skills/context-surfacer/sources/subagent.py

# Import browser chat exports
python3 ~/.claude/skills/context-surfacer/sources/browser_bridge.py --import-all
```

## MCP Server

The surfacer runs as an MCP server on opencode. Tools:
- `surf` — Search all data sources
- `surf_related` — Find sessions mentioning a file

## Data sources searched

| Source | What | Count |
|--------|------|-------|
| sessions | Session logs (8 agent formats) | 505 sessions, 19K turns |
| opencode_db | OpenCode sessions + parts (read-only) | 250 sessions, 83K parts |
| hermes_db | Hermes sessions + messages (read-only, FTS5) | sessions + messages |
| subagent | Saved subagent outputs (markdown) | 5+ files |
| knowledge | YouTube transcripts, articles, browser history | 12K items |
| code | 65 indexed projects (175K nodes) | codebase-memory graph |
| state | VINNYOS-STATE.md sections | parsed |
| files | Scripts, configs, databases | direct glob + grep |
| skills | 129 SKILL.md definitions | YAML frontmatter |
| octopus | Journal entries + decisions | SQLite queries |
| file_mentions | File→session back-links | auto-extracted |
