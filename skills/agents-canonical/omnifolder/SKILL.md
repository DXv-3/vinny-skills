---
name: omnifolder
description: >
  Drive OmniFolder (local file index, semantic search, organize) from Grok CLI via MCP.
  Use when the user mentions OmniFolder, file search on their Mac, organize Downloads,
  or wants Grok terminal to power the OmniFolder app.
---

# OmniFolder + Grok CLI

OmniFolder is a macOS app with a local SQLite index. **Grok Build powers it** through the `omnifolder` MCP server.

## Setup (once)

```bash
/Users/vinnygilberti/OmniFolder/Scripts/install-grok-mcp.sh
```

Restart Grok CLI after install.

## MCP tools

| Tool | Purpose |
|------|---------|
| `omnifolder_status` | Index path, file count, watched folder |
| `omnifolder_search` | Fast keyword search in the index |
| `omnifolder_agent` | Open HUD with intent (`organize`, `summarize`, `find …`) |
| `omnifolder_set_watch_folder` | Point OmniFolder at a folder |
| `omnifolder_grok_prompt` | Emit a ready-made `grok -p` command |

## Typical flows

**Terminal search (no HUD):**
```bash
grok -p "omnifolder_status then search for invoice 2024 in my Downloads" -m grok-build --cwd ~/Downloads
```

**Organize via app HUD:**
```bash
grok -p "omnifolder_agent organize my Downloads folder" -m grok-build
```
User confirms moves in the OmniFolder panel.

**Ensure app is running:** `omnifolder_agent` runs `open -a OmniFolder`.

## Requirements

- OmniFolder.app installed (`/Applications/OmniFolder.app`)
- Index built at least once (Index → Ready in HUD)
- Full Disk Access recommended for broad folder coverage

## In-app LLM

OmniFolder agents also support OpenRouter and Ollama. Grok CLI orchestration is separate from in-app chat unless you add an xAI API key in Settings.