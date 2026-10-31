---
name: github-morph
description: >
  A smart morphing tool that treats GitHub as a library of parts. Extracts components,
  patterns, and code snippets from repositories and enables intelligent transformation
  and composition of code. Integrates with gitreverse, gitingest, and other GitHub tools.
metadata:
  short-description: "GitHub as a library of parts - extract, analyze, and morph code components"
---

# GitHub Morph Skill

A powerful tool for treating GitHub as a massive library of reusable code parts. This skill enables:
- Repository analysis and structure extraction
- Component identification and pattern matching
- Code snippet extraction and transformation
- Smart morphing of code between different patterns/architectures

## Core Capabilities

### 1. Repository Analysis
- Fetch repository structure via GitHub API
- Extract file trees and identify key components
- Analyze code patterns and dependencies
- Generate repository summaries

### 2. Component Extraction
- Extract specific code components (functions, classes, modules)
- Identify reusable patterns across repositories
- Extract code snippets with context
- Build a searchable index of components

### 3. Pattern Matching
- Find similar patterns across GitHub
- Match code against known patterns
- Identify architectural patterns
- Extract design patterns

### 4. Smart Morphing
- Transform code between patterns
- Adapt components for different frameworks
- Merge multiple components intelligently
- Generate composite implementations

## Usage

```
/github-morph analyze <repo-url>
/github-morph extract <repo-url> --component <pattern>
/github-morph find <pattern> --language <lang>
/github-morph morph <source> --to <target-pattern>
/github-morph compose <components...>
```

## Integration Points

- **git-handoff hub** (`~/Documents/gitreverse/`): Unified AI hub v2 — all coderamp + filiksyos tools, agent playbook, token budgets, similar repos, explain/extend prompts.
  - `handoff hub owner/repo` — fast dashboard
  - `handoff reverse owner/repo -o ./handoffs` — full bundle (+ `*.AGENT.md`)
  - `handoff tools` — ecosystem catalog
- **gitreverse_v3_master.md** (`~/Documents/gitreverse/`): Full v3 spec (atoms, composer, MCP). Phase 1 shipped in git-handoff.
- **gitreverse**: Reverse engineer repos into original prompts
- **gitingest**: Extract prompt-friendly codebase representations
- **GitHub API**: Direct repository access and analysis
- **repodissect**: Decompose repos into functional blocks

### Ecosystem URL transforms (coderamp-labs + filiksyos)

| Tool | Transform | Output |
|------|-----------|--------|
| gitingest | `github.com` → `gitingest.com` | Full codebase digest |
| gitreverse | `github.com/o/r` → `gitreverse.com/o/r` | Vibe-coding rebuild prompt |
| gitcontainer | `github.com` → `gitcontainer.com` | Dockerfile |
| gittodoc | repo → doc link | AI-readable docs |
| gittoskill | repo + objective → ZIP | SKILL.md + scripts |
| mcptoskill | MCP URL → skill | Agent skill package |
| gitsimilar | repo → similar repos | Discovery |
| gitrules | workspace | Agents/rules/MCP install script |

## Output Format

All outputs are structured for easy consumption:
- JSON for programmatic use
- Markdown for documentation
- Code snippets ready for integration