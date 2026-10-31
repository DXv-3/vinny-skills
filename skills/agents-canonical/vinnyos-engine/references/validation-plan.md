# VinnyOS Engine Validation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stress-test and validate the VinnyOS Engine — a unified MCP server with 13 layers that orchestrates find-skills, github-ecosystem, and codebase-memory.

**Architecture:** Python MCP server that calls existing tools via subprocess. No porting. No rewriting. Just orchestration.

**Tech Stack:** Python 3, subprocess, JSON, GitHub CLI (`gh`), Node.js (find-skills pipeline), codebase-memory-mcp binary

---

## File Structure

```
~/.claude/skills/vinnyos-engine/
├── mcp_server.py              # Main server (1196 lines)
├── SKILL.md                   # Skill chain orchestrator
├── SKILL_CHAIN.md             # Visual overview
├── explode_wrapper.mjs        # Node.js wrapper for find-skills
└── references/
    ├── phase1-validate.md
    ├── phase2-discover.md
    ├── phase3-build.md
    └── context-map.md
```

---

## Task 1: Validate Layer 1 (EXPLORE)

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_explore.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Layer 1: EXPLORE"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import explore

def test_explore_returns_queries():
    result = explore("MCP server for autonomous coding agents", max_queries=12)
    assert result["count"] > 0, f"Expected queries, got {result['count']}"
    assert result["source"] == "find-skills", f"Expected find-skills source, got {result['source']}"
    assert len(result["queries"]) <= 12, f"Expected <=12 queries, got {len(result['queries'])}"
    print(f"✅ Layer 1: {result['count']} queries from {result['source']}")

if __name__ == "__main__":
    test_explore_returns_queries()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_explore.py`
Expected: PASS (already working)

- [ ] **Step 3: Verify edge cases**

```python
def test_explore_fallback():
    """Test fallback when find-skills is unavailable"""
    from mcp_server import _generate_queries_fallback
    queries = _generate_queries_fallback("knowledge graph")
    assert len(queries) > 0, "Fallback should generate queries"
    print(f"✅ Fallback: {len(queries)} queries generated")

def test_explore_max_queries():
    """Test max_queries limit"""
    result = explore("test", max_queries=5)
    assert len(result["queries"]) <= 5, f"Expected <=5, got {len(result['queries'])}"
    print(f"✅ Max queries: {len(result['queries'])} <= 5")

if __name__ == "__main__":
    test_explore_returns_queries()
    test_explore_fallback()
    test_explore_max_queries()
```

- [ ] **Step 4: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_explore.py`
Expected: All PASS

---

## Task 2: Validate Layer 2 (HARVEST)

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_harvest.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Layer 2: HARVEST"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import harvest

def test_harvest_returns_repos():
    queries = ["MCP server python", "autonomous coding agent"]
    result = harvest(queries, limit_per_query=3)
    assert result["total"] > 0, f"Expected repos, got {result['total']}"
    assert len(result["candidates"]) > 0, "Expected candidates list"
    print(f"✅ Layer 2: {result['total']} repos found")

def test_harvest_deduplicates():
    queries = ["MCP server", "MCP server python"]
    result = harvest(queries, limit_per_query=5)
    repos = [c["repo"] for c in result["candidates"]]
    assert len(repos) == len(set(repos)), "Expected unique repos"
    print(f"✅ Dedup: {len(repos)} unique out of {len(result['candidates'])}")

def test_harvest_sorted_by_stars():
    queries = ["knowledge graph"]
    result = harvest(queries, limit_per_query=10)
    stars = [c["stars"] for c in result["candidates"]]
    assert stars == sorted(stars, reverse=True), "Expected sorted by stars"
    print(f"✅ Sort: top repo has {stars[0]} stars")

if __name__ == "__main__":
    test_harvest_returns_repos()
    test_harvest_deduplicates()
    test_harvest_sorted_by_stars()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_harvest.py`
Expected: PASS (already working)

- [ ] **Step 3: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_harvest.py`
Expected: All PASS

---

## Task 3: Validate Layer 3 (DECOMPOSE)

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_decompose.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Layer 3: DECOMPOSE"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import decompose, _extract_parts_from_text

def test_decompose_extracts_parts():
    result = decompose("microsoft/graphrag")
    assert result["total"] > 0, f"Expected parts, got {result['total']}"
    assert len(result["parts"]) > 0, "Expected parts list"
    print(f"✅ Layer 3: {result['total']} parts extracted")

def test_extract_parts_from_text():
    text = """## Features
- Knowledge graph construction
- Entity extraction using LLMs

## Workflow
- Parse documents
- Extract entities
- Build graph
"""
    parts = _extract_parts_from_text(text, "test")
    assert len(parts) > 0, "Expected parts from text"
    types = [p["type"] for p in parts]
    assert "feature" in types or "workflow" in types, f"Expected feature/workflow types, got {types}"
    print(f"✅ Text extraction: {len(parts)} parts, types: {set(types)}")

if __name__ == "__main__":
    test_decompose_extracts_parts()
    test_extract_parts_from_text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_decompose.py`
Expected: PASS (already working)

- [ ] **Step 3: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_decompose.py`
Expected: All PASS

---

## Task 4: Validate Layer 4 (SYNTHESIZE)

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_synthesize.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Layer 4: SYNTHESIZE"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import synthesize

def test_synthesize_matches_parts():
    parts = [
        {"type": "feature", "text": "Knowledge graph construction from documents", "section": "Features"},
        {"type": "workflow", "text": "Entity extraction using LLMs", "section": "Pipeline"},
        {"type": "snippet", "text": "Vector embeddings for semantic search", "section": "Code"},
    ]
    idea = "Build a knowledge graph from my codebase for AI agents"
    result = synthesize(idea, parts)
    assert result["confirmed"] > 0 or len(result["wanted"]) > 0, "Expected matches"
    print(f"✅ Layer 4: {len(result['wanted'])} wanted, {result['confirmed']} confirmed")

def test_synthesize_identifies_gaps():
    parts = [{"type": "feature", "text": "Simple feature", "section": "Features"}]
    idea = "Complex system with multiple components"
    result = synthesize(idea, parts)
    assert len(result["gaps"]) > 0, "Expected gaps identified"
    print(f"✅ Gaps: {len(result['gaps'])} gaps found")

if __name__ == "__main__":
    test_synthesize_matches_parts()
    test_synthesize_identifies_gaps()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_synthesize.py`
Expected: PASS (already working)

- [ ] **Step 3: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_synthesize.py`
Expected: All PASS

---

## Task 5: Validate Layers 5-10 (GitHub Ecosystem)

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_github_ecosystem.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Layers 5-10: GitHub Ecosystem"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import discover, analyze, extract

def test_discover_finds_repos():
    result = discover("think", limit=5)
    assert result["total"] > 0, f"Expected repos, got {result['total']}"
    print(f"✅ Layer 5: {result['total']} repos in 'think' layer")

def test_analyze_repo():
    result = analyze("microsoft/graphrag")
    assert "info" in result, "Expected repo info"
    assert result["info"]["stargazerCount"] > 0, "Expected stars"
    print(f"✅ Layer 6: {result['info']['stargazerCount']} stars")

def test_extract_file():
    result = extract("microsoft/graphrag", "README.md")
    assert "file" in result, "Expected file path"
    assert result["lines"] > 0, "Expected content"
    print(f"✅ Layer 7: {result['lines']} lines extracted")

if __name__ == "__main__":
    test_discover_finds_repos()
    test_analyze_repo()
    test_extract_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_github_ecosystem.py`
Expected: PASS (already working)

- [ ] **Step 3: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_github_ecosystem.py`
Expected: All PASS

---

## Task 6: Validate Layers 11-13 (Self-Heal, Dream, Graph)

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_advanced.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Layers 11-13: Self-Heal, Dream, Graph"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import self_heal, dream, graph_search

def test_self_heal():
    result = self_heal()
    assert "status" in result, "Expected status"
    assert "issues" in result, "Expected issues list"
    print(f"✅ Layer 11: status={result['status']}, issues={len(result['issues'])}")

def test_dream():
    result = dream()
    assert "status" in result, "Expected status"
    assert "actions" in result, "Expected actions list"
    print(f"✅ Layer 12: status={result['status']}, actions={len(result['actions'])}")

def test_graph_search():
    result = graph_search("clipboard-manager", "clipboard")
    assert "raw" in result or "total" in result, "Expected results"
    print(f"✅ Layer 13: graph search returned results")

if __name__ == "__main__":
    test_self_heal()
    test_dream()
    test_graph_search()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_advanced.py`
Expected: PASS (already working)

- [ ] **Step 3: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_advanced.py`
Expected: All PASS

---

## Task 7: Validate Full Pipeline

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_full_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Test Full Pipeline"""
import sys
sys.path.insert(0, '/Users/vinnygilberti/.claude/skills/vinnyos-engine')
from mcp_server import full_pipeline

def test_full_pipeline():
    result = full_pipeline(
        topic="knowledge graph for codebase",
        idea="Build AI agent that understands code structure"
    )
    assert "steps" in result, "Expected steps"
    assert len(result["steps"]) >= 4, f"Expected >=4 steps, got {len(result['steps'])}"
    
    # Check each step
    for step in result["steps"]:
        assert "step" in step, f"Expected step name"
        assert "result" in step, f"Expected result for {step['step']}"
    
    print(f"✅ Full Pipeline: {len(result['steps'])} steps completed")

if __name__ == "__main__":
    test_full_pipeline()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_full_pipeline.py`
Expected: PASS (already working)

- [ ] **Step 3: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_full_pipeline.py`
Expected: All PASS

---

## Task 8: Run All Tests Together

**Files:**
- Test: `~/.claude/skills/vinnyos-engine/test_all.py`

- [ ] **Step 1: Create master test runner**

```python
#!/usr/bin/env python3
"""Master test runner for VinnyOS Engine"""
import subprocess
import sys

tests = [
    "test_explore.py",
    "test_harvest.py",
    "test_decompose.py",
    "test_synthesize.py",
    "test_github_ecosystem.py",
    "test_advanced.py",
    "test_full_pipeline.py",
]

passed = 0
failed = 0

for test in tests:
    print(f"\n{'='*60}")
    print(f"Running: {test}")
    print('='*60)
    result = subprocess.run(
        [sys.executable, test],
        capture_output=True,
        text=True,
        cwd="/Users/vinnygilberti/.claude/skills/vinnyos-engine"
    )
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode == 0:
        passed += 1
    else:
        failed += 1

print(f"\n{'='*60}")
print(f"RESULTS: {passed} passed, {failed} failed")
print('='*60)
```

- [ ] **Step 2: Run all tests**

Run: `python3 ~/.claude/skills/vinnyos-engine/test_all.py`
Expected: All PASS

---

## Validation Checklist

- [ ] Layer 1 (EXPLORE): Generates queries via find-skills
- [ ] Layer 2 (HARVEST): Finds repos via GitHub search
- [ ] Layer 3 (DECOMPOSE): Extracts parts from README
- [ ] Layer 4 (SYNTHESIZE): Matches ideas to parts
- [ ] Layer 5 (DISCOVER): Finds repos by layer
- [ ] Layer 6 (ANALYZE): Analyzes repo structure
- [ ] Layer 7 (EXTRACT): Extracts files from repos
- [ ] Layer 8 (ISOLATE): Generates safe wrappers
- [ ] Layer 9 (VALIDATE): Tests extracted code
- [ ] Layer 10 (INTEGRATE): Wires code to projects
- [ ] Layer 11 (SELF-HEAL): Detects system issues
- [ ] Layer 12 (DREAM): Consolidates knowledge
- [ ] Layer 13 (GRAPH): Queries knowledge graph
- [ ] Full Pipeline: End-to-end workflow
