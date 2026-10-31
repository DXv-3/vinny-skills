# GitHub Ecosystem MCP — Setup for All Platforms

## The Server

Location: `/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py`

This is a Python script that runs as an MCP server. It uses your `gh` CLI authentication (already set up). No additional API keys needed.

## How It Works

Each AI platform has a config file where you register MCP servers. The server definition is almost identical across platforms — you just copy-paste into different files.

## Platform Configs

### Claude Code (ALREADY DONE)
Config: `~/.claude.json`
```json
"github-ecosystem": {
  "command": "python3",
  "args": ["/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py"],
  "cwd": "/Users/vinnygilberti/.claude/skills/github-ecosystem",
  "env": {},
  "type": "stdio"
}
```

### Claude Desktop
Config: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
"github-ecosystem": {
  "command": "python3",
  "args": ["/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py"],
  "cwd": "/Users/vinnygilberti/.claude/skills/github-ecosystem",
  "env": {},
  "type": "stdio"
}
```

### opencode
Config: `opencode.json` (project root) or `~/.config/opencode/opencode.json`
```json
"github-ecosystem": {
  "type": "local",
  "command": ["python3", "/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py"],
  "enabled": true
}
```

### Cursor
Config: `~/.cursor/mcp.json`
```json
"github-ecosystem": {
  "command": "python3",
  "args": ["/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py"],
  "cwd": "/Users/vinnygilberti/.claude/skills/github-ecosystem",
  "env": {},
  "type": "stdio"
}
```

### Windsurf
Config: `~/.codeium/windsurf/mcp_config.json`
```json
"github-ecosystem": {
  "command": "python3",
  "args": ["/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py"],
  "cwd": "/Users/vinnygilberti/.claude/skills/github-ecosystem",
  "env": {},
  "type": "stdio"
}
```

### Kilo Code
Config: `~/.config/kilo/kilo.jsonc`
```json
"github-ecosystem": {
  "type": "local",
  "command": ["python3", "/Users/vinnygilberti/.claude/skills/github-ecosystem/mcp_server.py"],
  "enabled": true
}
```

## Quick Setup Script

Run this to add the server to all platforms at once:

```bash
python3 /Users/vinnygilberti/.claude/skills/github-ecosystem/setup_all_platforms.py
```

## Available Tools

Once configured, these tools are available in any MCP-compatible client:

| Tool | What It Does |
|------|--------------|
| `discover_layer` | Find best repos for a layer (capture/fuse/think/act/self/dream) |
| `discover_all` | Search all 6 layers at once |
| `analyze_repo` | Map a repo's structure, entry points, reusable modules |
| `extract_module` | Pull a specific file from a repo |
| `isolate_wrapper` | Generate safe wrapper to prevent breaking your code |
| `test_extraction` | Verify extracted code compiles and runs |
| `generate_imports` | Generate import statements for integration |
| `full_pipeline` | Complete: analyze → extract → isolate → test → imports |

## Usage Examples

```
"Find me the best dream consolidation tools"
→ Uses: discover_layer(dream="dream")

"Analyze khoj-ai/khoj and tell me what's reusable"
→ Uses: analyze_repo(repo="khoj-ai/khoj")

"Extract the memory module from cognee and wire it into my project"
→ Uses: full_pipeline(repo="topoteretes/cognee", path="cognee/modules/memory", project_dir=".")

"Search all layers and show me the wiring diagram"
→ Uses: discover_all(limit=5)
```

## Troubleshooting

If a tool doesn't appear:
1. Check the config file has the correct JSON
2. Restart the AI client
3. Run: `python3 /path/to/mcp_server.py mcp` to test standalone
4. Check: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 /path/to/mcp_server.py mcp`
