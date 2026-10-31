# GitHub Ecosystem Discovery System — Full Context Handoff

## Date
2026-07-26

## What This Is
A complete system for treating GitHub as a living ecosystem of composable parts — not a code repository. The system discovers, analyzes, extracts, isolates, tests, and integrates code from any GitHub repo into your project safely.

---

## The Core Insight

**Most people use GitHub to find ONE tool for ONE job.**

**The real power is seeing GitHub as a LIVING ECOSYSTEM of composable parts.**

**The weird/experimental stuff is where the real breakthroughs are.**

This changes everything about how you build software. Instead of:
- "Find me a memory library" → pick one → hope it works

You do:
- "Memory is a LAYER. What are all the best tools for that layer? How do they connect? What's missing? Build that."

---

## The Layer Model

Every system has 6 layers. Most people build 1-2. You build all 6:

```
┌─────────────┐
│   CAPTURE   │  ← Data ingestion, scraping, collection, monitoring
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    FUSE     │  ← Dedup, entity resolution, context management, linking
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    THINK    │  ← Memory, knowledge graphs, reasoning, semantic search
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│     ACT     │────▶│    SELF     │
└──────┬──────┘     └──────┬──────┘
       │                    │
       │    ┌──────────────┘
       ▼    ▼
┌─────────────┐
│    DREAM    │  ← Consolidation, subconscious, forgetting, reorganization
└──────┬──────┘
       │
       └──────────▶ (feeds back to THINK)
```

### Layer Definitions

| Layer | Purpose | Search Patterns |
|-------|---------|-----------------|
| **CAPTURE** | Data ingestion, scraping, collection, monitoring | `"data ingestion"`, `"web scraper"`, `"file watcher"`, `"clipboard" manager` |
| **FUSE** | Dedup, entity resolution, context management, linking | `"entity resolution"`, `"semantic dedup"`, `"context management"`, `"data fusion"` |
| **THINK** | Memory, knowledge graphs, reasoning, semantic search | `"knowledge graph"`, `"AI memory"`, `"vector database"`, `"semantic search"` |
| **ACT** | Orchestration, execution, coordination, agents | `"agent orchestration"`, `"multi agent"`, `"workflow engine"`, `"MCP server"` |
| **SELF** | Self-healing, adaptation, learning loops | `"self improving"`, `"adaptive" agent`, `"learning loop"`, `"self healing"` |
| **DREAM** | Consolidation, subconscious, forgetting, reorganization | `"memory consolidation"`, `"subconscious" agent`, `"context rot"`, `"dream" memory` |

---

## What We Built

### 1. skill.md — The Skill Instructions

**Location:** `~/.claude/skills/github-ecosystem/SKILL.md`

**Purpose:** Teaches any agent how to think in layers, search by layer, evaluate candidates, and map connections.

**Key sections:**
- Phase 1: Decompose the Problem into layers
- Phase 2: Search by Layer (with specific patterns)
- Phase 3: Evaluate Candidates (stars, alive, language, license, dependencies, MCP, local-first, composability)
- Phase 4: Map Connections (wiring diagram)
- Phase 5: Extract and Wire

### 2. agent.md — The Agent Definition

**Location:** `~/.claude/skills/github-ecosystem/agent.md`

**Purpose:** Defines an agent identity that thinks in ecosystems, not tools.

**Key principles:**
- "You don't find tools — you discover organs"
- "Don't think in terms of tools — think in terms of organs"
- "The weird experimental repos are more valuable than the popular ones"
- "A 30-star repo with dream consolidation is worth more than a 10k-star repo that just stores notes"

### 3. mcp_server.py — The Extraction Engine

**Location:** `~/.claude/skills/github-ecosystem/mcp_server.py`

**Purpose:** 6-layer extraction pipeline that safely takes code from GitHub and makes it usable in your project.

**Layers:**

| Layer | Function | What It Does |
|-------|----------|--------------|
| **DISCOVER** | `discover_repos()` | Search GitHub by layer, return sorted by stars |
| **ANALYZE** | `analyze_repo()` | Clone repo, find all Python files, identify reusable modules, score them |
| **EXTRACT** | `extract_module()` | Pull specific files, find local dependencies, save locally |
| **ISOLATE** | `generate_wrapper()` | Generate safe wrapper classes that catch all errors |
| **TEST** | `test_extraction()` | Verify extracted code can be imported and instantiated |
| **INTEGRATE** | `generate_import_code()` | Generate import statements and wiring code |

**Commands:**

```bash
# Discover repos for a layer
python3 mcp_server.py discover <layer> [limit]

# Discover all layers
python3 mcp_server.py discover-all [limit]

# Analyze a repo
python3 mcp_server.py analyze <repo>

# Extract a module
python3 mcp_server.py extract <repo> <path> [name]

# Generate safe wrapper
python3 mcp_server.py isolate <dir> <class>

# Test extracted code
python3 mcp_server.py test <dir>

# Generate integration code
python3 mcp_server.py integrate <dir> <project>

# Full pipeline
python3 mcp_server.py pipeline <repo> <path> <project>
```

---

## The Extraction Pipeline — How It Works

### Step 1: DISCOVER
```python
discover_repos("think", limit=10)
```
- Searches GitHub using layer-specific patterns
- Deduplicates results
- Sorts by stars
- Returns: `[{"fullName": "khoj-ai/khoj", "description": "...", "stargazersCount": 36101, ...}]`

### Step 2: ANALYZE
```python
analyze_repo("khoj-ai/khoj")
```
- Clones repo (shallow)
- Finds all `.py` files
- For each file:
  - Extracts classes and functions
  - Counts lines
  - Checks if it's a reusable module (has classes, no `if __name__` block)
  - Scores it (0-10)
- Returns: `{"modules": [...], "reusable_modules": [...], "dependencies": [...]}`

### Step 3: EXTRACT
```python
extract_module("khoj-ai/khoj", "src/khoj/routers/api_memories.py", "memories")
```
- Clones repo (shallow)
- Copies the target file
- Finds local imports (imports that start with `.` or lowercase)
- Copies those dependencies too
- Returns: `{"extract_dir": "~/.vinnyos/extracted/memories", "local_dependencies": [...]}`

### Step 4: ISOLATE
```python
generate_wrapper("~/.vinnyos/extracted/memories", "MemoryManager")
```
- Reads the extracted module
- Finds classes
- Generates a wrapper class that:
  - Catches all exceptions from the wrapped class
  - Provides fallback behavior on failure
  - Logs all interactions for debugging
  - Has `is_ready()` method to check if initialization succeeded
  - Proxies all method calls with error handling
- Returns: `{"wrapper_file": "wrapper_memories.py", "usage": "from memories.wrapper_memories import MemoryManager"}`

### Step 5: TEST
```python
test_extraction("~/.vinnyos/extracted/memories")
```
- Tries to import each wrapper file
- Tries to instantiate wrapper classes
- Returns: `{"tests": [{"file": "wrapper_memories.py", "import": "SUCCESS", "instantiation": "SUCCESS"}]}`

### Step 6: INTEGRATE
```python
generate_import_code("~/.vinnyos/extracted/memories", "./my-project")
```
- Finds wrapper classes and functions
- Generates import statements
- Creates integration file with usage examples
- Returns: `{"integration_file": "vinnyos_memories_integration.py", "imports": [...]}`

### Full Pipeline
```python
full_extraction_pipeline("khoj-ai/khoj", "src/khoj/routers/api_memories.py", "./my-project")
```
Runs all 6 steps in sequence. Returns `{"success": true, "final_dir": "my-project/vinnyos_modules/memories", "import_path": "vinnyos_modules.memories"}`

---

## Test Results

### Test 1: Dream Layer Discovery
```
$ python3 mcp_server.py discover dream 3

★    12  milos-product-maker/context-rot-detection
         Context Rot Detection & Healing MCP Service — gives AI agent

★     1  avmkmk/vibewatch
         Context rot detection and handoff generation for AI-assisted

★     0  ostepan8/subconscious-scheduler
         Schedule Subconscious agents to run research, data syncs, an
```

### Test 2: Repo Analysis
```
$ python3 mcp_server.py analyze khoj-ai/khoj

Found: 194 modules
Reusable: 19 modules
Top modules:
  - src/khoj/routers/helpers.py (3460 lines, score: 8)
  - src/khoj/routers/api_chat.py (1754 lines, score: 8)
  - src/khoj/processor/conversation/utils.py (1282 lines, score: 8)
  - src/khoj/utils/helpers.py (1253 lines, score: 8)
```

### Test 3: Full Pipeline
```
$ python3 mcp_server.py pipeline khoj-ai/khoj src/khoj/routers/api_memories.py ./test-project

Steps completed:
  ✅ analyze: Found 194 modules
  ✅ extract: Extracted api_memories.py (115 lines)
  ✅ isolate: Generated wrapper with error handling
  ✅ test: Import SUCCESS, Instantiation SUCCESS
  ✅ integrate: Generated import code
  ✅ copy: Copied to test-project/vinnyos_modules/memories

success: true
```

---

## What We Found on GitHub

### Tier 1: Battle-Tested (10k+ stars)

| Project | Stars | What It Does | Layer |
|---------|-------|--------------|-------|
| **Scrapy** | 63,478 | Web crawling framework | CAPTURE |
| **Trilium** | 37,123 | Hierarchical note-taking KB | CAPTURE/THINK |
| **khoj-ai/khoj** | 36,101 | AI second brain with RAG | THINK/ACT |
| **cognee** | 29,552 | AI memory for agents | THINK |
| **MetaGPT** | 69,600 | Multi-agent orchestration | ACT |
| **openai-agents-python** | 28,300 | Agent SDK from OpenAI | ACT |
| **letta** | 24,000 | Self-healing/memory agents | SELF |
| **siyuan-note/siyuan** | 45,485 | PKM with knowledge graph | THINK |
| **logseq/logseq** | 44,141 | Outliner-based PKM | THINK |

### Tier 2: Weird & Experimental (The Breakthroughs)

| Project | Stars | What It Does | Why It Matters |
|---------|-------|--------------|----------------|
| **genesis-agent** | 30 | AI that reads/modifies its own code, dreams in idle time | Self-aware agent architecture |
| **digital-twin-proxy** | 38 | Turns network traffic into personal memory | Every HTTP request becomes context |
| **cerebraos** | — | "Layer of Subconsciousness" — deliberately discards information | Forgetting as a feature |
| **anchor-memory** | 38 | Graph memory with Hebbian learning | Biological memory patterns |
| **openclaw-auto-dream** | 548 | Memory consolidation during downtime | Sleep for your AI |
| **WeClone** | 18,110 | Fine-tune LLMs with your chat logs | Digital self from conversations |
| **context-rot-detection** | 12 | Self-awareness about cognitive state | Meta-cognition for machines |
| **thinking-agents** | — | 4 parallel thinking threads, 4 models, shared subconscious | Multi-model consciousness |

### Tier 3: Glue Layer (Fusing Data)

| Tool | Stars | What It Fuses |
|------|-------|---------------|
| **semhash** | 954 | Multimodal semantic dedup — text, code, media |
| **context-mode** | 19,445 | Sandboxes tool output, persists session memory |
| **dedupe** | 4,487 | Entity resolution across heterogeneous sources |
| **agentic-local-brain** | 75 | Files, papers, emails, notes → unified knowledge graph |

### Tier 4: Sensory Organs (Watching Your System)

| Tool | Stars | What It Watches |
|------|-------|-----------------|
| **fswatch** | 5,568 | File system changes — the nervous system |
| **gosearch** | 3,524 | Your entire digital footprint across 300+ sites |
| **dogsheep** | 128 | Personal analytics aggregator |
| **VeloxClip** | 27 | Clipboard intelligence |

---

## The Missing Layer: DREAM

Most AI memory systems are just databases. They store, they retrieve. They never:
- **Consolidate** (reorganize during idle time)
- **Forget** (deliberately discard low-value information)
- **Dream** (find hidden connections during downtime)
- **Evolve** (restructure their own knowledge graph)

The DREAM layer is what separates a database from a living system.

**Tools that do this:**
- `openclaw-auto-dream` — Memory consolidation during downtime
- `cerebraos` — Deliberate forgetting as a feature
- `anchor-memory` — Hebbian learning (neurons that fire together wire together)
- `context-rot-detection` — Meta-cognition about cognitive degradation

---

## How This Connects to VinnyOS

### VinnyOS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VINNYOS ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  vinny-stack │  │  the-brain   │  │ dxv-agent-os │       │
│  │  (CAPTURE)   │  │  (THINK)     │  │ (ACT)        │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │               │
│         └────────┬────────┴────────┬─────────┘               │
│                  │                 │                          │
│                  ▼                 ▼                          │
│           ┌──────────────┐  ┌──────────────┐                 │
│           │   Octopus    │  │   forward-   │                 │
│           │ (orchestrate)│  │   executor   │                 │
│           └──────┬───────┘  │ (SELF)       │                 │
│                  │          └──────┬───────┘                 │
│                  │                 │                          │
│                  └────────┬────────┘                         │
│                           ▼                                  │
│                  ┌──────────────┐                            │
│                  │   DREAM      │                            │
│                  │ (consolidate)│                            │
│                  └──────────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Your Existing Repos as Parts

| Repo | Layer | What to Reuse |
|------|-------|---------------|
| **vinny-stack** | CAPTURE | Full pipeline: capture → OCR → memory → cache |
| **the-brain** | THINK | SQLite + vector search + knowledge graph + MCP |
| **dxv-agent-os** | ACT | Git-native multi-agent OS with 5 agents + GNAP |
| **forward-executor-system** | SELF | Adaptive meta-cycle + blocker classification |
| **Octopus** | ORCHESTRATION | Brain that coordinates everything |
| **create-context-graph** | THINK | Neo4j knowledge graph builder |
| **conductor-protocol-v2** | ACT | Provenance tracking + operator-router |
| **harmony-engine-protocol** | ACT | Distributed message passing |

---

## Key Anti-Patterns

1. **Don't** search for "the best tool for X" — search for the LAYER
2. **Don't** pick the first result — compare 5-10 candidates
3. **Don't** ignore low-star repos — the weird experimental ones often have the best ideas
4. **Don't** assume you need to build from scratch — someone already built 80% of what you need
5. **Don't** think in terms of "tools" — think in terms of "organs" that form a living system
6. **Don't** skip the DREAM layer — that's where evolution happens
7. **Don't** commit to one base before exploring all options — GitHub is vast

---

## File Structure

```
~/.claude/skills/github-ecosystem/
├── SKILL.md          # Skill instructions for discovery
├── agent.md          # Agent definition
├── mcp_server.py     # Extraction engine (6 layers)
└── HANDOFF.md        # This document

~/.vinnyos/
├── extracted/        # Extracted modules go here
├── cache/            # Cache for repeated extractions
└── stubs/            # Type stubs for IDE support
```

---

## Next Steps

1. **Clone and test** the 4 base repos:
   - vinny-stack (CAPTURE)
   - the-brain (THINK)
   - dxv-agent-os (ACT)
   - forward-executor-system (SELF)

2. **Wire them together** with MCP

3. **Build the DREAM layer** using:
   - openclaw-auto-dream (consolidation)
   - cerebraos (subconscious)
   - anchor-memory (Hebbian learning)

4. **Test the full system** with real data

5. **Iterate** — the system should improve itself

---

## The Ultimate Goal

A living system that:
- **Watches** everything (files, clipboard, browser, network)
- **Remembers** everything (semantic search, knowledge graphs)
- **Connects** everything (entity resolution, dedup, linking)
- **Acts** on everything (orchestration, execution, coordination)
- **Heals** itself (self-improvement, adaptation, learning loops)
- **Dreams** during downtime (consolidation, forgetting, reorganization)

This isn't just wiring tools together. It's building a **living organism** that watches, learns, dreams, and evolves.

---

## Contact

This system was built by Vinny Gilberti on 2026-07-26.
The insight: GitHub is not a code repository — it's a living ecosystem of composable ideas.
