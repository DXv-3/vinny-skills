---
name: osint-datasets
description: "OSINT Datasets Skill"
---

# OSINT Datasets Skill

## Purpose

Provides AI agents and CLI users with query access to three chained OSINT datasets that map the entire username/email enumeration tool ecosystem — tools, platform site lists, and MCP servers.

## Quick Start

### CLI
```bash
# Search tools
osint-cli search sherlock
osint-cli tools --email --ai --min-stars 1000
osint-cli search --language go --min-stars 100

# Search platform sites
osint-cli sites social
osint-cli sites --source WhatsMyName --category gaming --cross

# Trace relationship chains
osint-cli chain Sherlock --depth 3
osint-cli chain Blackbird --depth 2

# MCP servers
osint-cli mcps

# Stats
osint-cli stats

# Natural language query
osint-cli query "tools that wrap sherlock via MCP"
```

### MCP (for AI agents)
```
# Available tools:
search_tools          — Search by name, language, feature, min_stars
get_tool_relationships — Trace forks, alternatives, data sources, MCP wrappers
search_sites          — Search 4,418 platforms by name, category, source
get_mcp_servers       — List MCP servers wrapping OSINT tools
dataset_stats         — Statistics across all 3 datasets
osint_query           — Natural language intent queries
chain_query           — Full dependency/relationship chain traversal
```

## Datasets

| Dataset | Path | Contents |
|---------|------|----------|
| osint-chained.db | `~/.ai-memory/datasets/osint-chained.db` | 51 tools, 196 features, 44 relationships, 102 cross-refs |
| osint-sites.db | `~/.ai-memory/datasets/osint-sites.db` | 4,418 sites (WhatsMyName 716 + Sherlock 481 + Maigret 3221), 605 cross-source matches |
| osint-mcp-registry.db | `~/.ai-memory/datasets/osint-mcp-registry.db` | 7 MCP servers, 43 tools, 25 wrap relationships |

## Data Model

### tools (in osint-chained.db)
- `name`, `github_repo`, `stars`, `language`, `license_spdx`, `last_push`, `description`, `categories`, `site_count`

### features (in osint-chained.db)
- 14 feature flags per tool: `username_search`, `email_search`, `ai_features`, `mcp_server`, `web_ui`, `docker`, `cli`, `api`, `python`, `go`, `rust`, `javascript`, `shell`, `whatsmyname_data`, `sherlock_data`, `self_check`, `permutation`, `tor_i2p`, `relationship_graph`, `breach_data`

### relationships (in osint-chained.db)
- 6 edge types: `forked_from`, `inspired_by`, `alternative_to`, `uses_dataset`, `wraps`, `ecosystem_of`

### sites (in osint-sites.db)
- `name`, `url_main`, `url_check`, `source` (WhatsMyName/Sherlock/Maigret), `error_type`, `error_message`, `category`, `tags`, `protection`

### mcp_servers (in osint-mcp-registry.db)
- `name`, `github_repo`, `stars`, `language`, `license_spdx`, `last_push`, `description`, `tool_count`, `server_type` (ai-agent/tool-wrapper)

## Chain Queries

The key power is **chaining across datasets**:

```bash
# Find the most capable MCP-wrapped OSINT setup
osint-cli query "tools that wrap sherlock via MCP"

# Find Go rewrites of Python tools
osint-cli query "Go rewrites of Python osint tools"

# Find email search tools with AI
osint-cli tools --email --ai
```

## Related Datasets

- YouTube transcripts: `~/youtube-ingest/` (2 channels, ~1,400 videos)
- Knowledge Base: `~/knowledge-base/database.sqlite` (13.9K items)
- Sessions: `~/sessions/sessions.sqlite` (500 sessions)
- File index: `~/.ai-memory/mac-catalog/catalog.sqlite` (678K files)

## Building/Updating Datasets

```bash
# Rebuild tools + relationships
python3 /tmp/build_osint_dataset.py

# Rebuild site lists (fetches fresh data from GitHub)
python3 /tmp/build_site_dataset.py

# Rebuild MCP registry
python3 /tmp/build_mcp_registry.py
```
