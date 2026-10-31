---
name: waterhole-ask
description: Legacy alias for kb-collection-query - use that skill for any prompt KB question; kept so old references still resolve.
---

The prompt KB's canonical skill is `/Users/vinnygilberti/.agents/skills/kb-collection-query/SKILL.md` — route every prompt-KB question there.

Three doors, in order: MCP `kb-waterhole` (`kb_search`/`kb_get`/`kb_stats`, first choice inside ZCode), the HTTP shim :8921 (`/api/waterhole`, bearer token from `~/opencode-shim/.token` via command substitution only, never echoed), and read-only SQLite `sqlite3 "file:$HOME/surface/prompt_kb.db?mode=ro"`.

Read-only forever — never write to the DB, never modify records.
