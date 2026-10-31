# Phase 2: DISCOVER

Detailed steps for finding existing tools.

---

## Step 1: Multi-Surface Search

**Load:** `@vinnyos-engine`

**Do:**
1. Use Layer 1 (EXPLORE) to generate 12+ queries
2. Use Layer 2 (HARVEST) to search repos, code, issues, PRs
3. Use Layer 5 (DISCOVER) to search by layer
4. Use Layer 13 (GRAPH) to search local codebase

**Queries to generate:**
- Core topic (e.g., "knowledge graph codebase")
- Adjacent domains (e.g., "code intelligence", "AST analysis")
- Creative mashups (e.g., "graph database meets code search")

---

## Step 2: Deep Research

**Load:** `@deep-research`

**Do:**
1. Analyze top 5 candidates from Step 1
2. Check: stars, activity, documentation, license, compatibility
3. Extract: code snippets, patterns, mental models
4. Write findings to `~/Documents/[Topic]_Research_[YYYYMMDD]/`

**Research questions:**
- What problem does this solve?
- How does it solve it?
- What are its limitations?
- Can we reuse it directly?
- Do we need to modify it?

---

## Step 3: Web Search

**Load:** `@web-search`

**Do:**
1. Search for blog posts, tutorials, Stack Overflow answers
2. Find: hidden gems, unconventional approaches, real-world usage
3. Check: publication date, author credibility, code quality

**Search queries:**
- "<topic> tutorial"
- "<topic> best practices"
- "<topic> lessons learned"
- "<topic> alternative approaches"

---

## Step 4: Knowledge Graph

**Load:** `@vinnyos-engine` (Layer 13: GRAPH)

**Do:**
1. Search local codebase for related code
2. Find: existing implementations, reusable components
3. Check: last modified, test coverage, documentation

---

## Output

A curated list of existing tools with:
- Name and URL
- Stars and activity
- What it does
- How we can reuse it
- What we need to modify
