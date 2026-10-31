---
name: swarm-github-research
description: "Swarm GitHub Research Workflow"
---

# Swarm GitHub Research Workflow

Researches GitHub for each swarm zone to find patterns, improvements, and best practices.

## Zones

| Zone | Description | GitHub Search |
|------|-------------|---------------|
| **swarm-status** | Controller status, devices, online/offline | "tailscale agent swarm controller" |
| **indexes** | File indexes across Mac + iCloud | "cross-device file index ios mac" |
| **search** | Search indexed files | "distributed file search agent" |
| **tasks** | Task history and execution | "agent task queue distributed" |
| **llm** | Query layer with litellm | "litellm local llm agent" |
| **ios-agent** | Web-based iOS agent | "ios web agent remote control" |

## Workflow

### Phase 1: Scan Zones (parallel)
For each zone, run:
1. `agent-reach` search: "github [zone query]"
2. `github-deep-research`: exhaustive repo discovery for the zone
3. `web-search`: latest articles and discussions

### Phase 2: Analyze (sequential)
For each zone's results:
1. Identify top 3 similar projects
2. Extract key features and patterns
3. Note gaps and improvement opportunities
4. Score relevance (1-5)

### Phase 3: Report (sequential)
For each zone, produce:
- Summary of findings
- Top repos with stars and last updated
- Key patterns to adopt
- Gaps to fill
- Confidence score

## Triggers
- "research swarm zones"
- "github for swarm"
- "analyze each zone"
- "swarm github research"

## Dependencies
- agent-reach (web search)
- github-deep-research (exhaustive repo discovery)
- web-search (latest articles)
- deep-research (comprehensive analysis)

## State & Resume (mandatory)

This is a long multi-zone process — the chat running it WILL die before finishing all six zones unless state is on disk. After completing each zone:

1. Save the zone report to `~/Documents/research/swarm-<zone>-$DATE.md` (`mkdir -p ~/Documents/research` first).
2. Update `~/Documents/research/swarm-github-state.json`:
   ```json
   {
     "updated_at": "...",
     "zones_completed": ["swarm-status"],
     "zone_reports": {"swarm-status": "~/Documents/research/swarm-swarm-status-$DATE.md"},
     "zones_in_progress": [],
     "next_zone": "indexes"
   }
   ```
3. On start or resume: load the state file, skip zones already completed, and continue from `next_zone`. Never re-research a completed zone.
4. Each zone's `github-deep-research` run does its own Phase 0 resume + checkpointing automatically.

## Fallback
If GitHub search fails, use `web-search` with site:github.com filter.
If deep research fails, use `agent-reach` for quick searches.
