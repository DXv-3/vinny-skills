# Phase 3: BUILD (LLM's Choice)

Detailed steps for going rogue and building what they didn't ask for.

---

## Step 1: Brainstorm the Unasked

**Load:** `@brainstorming`

**Do:**
1. Ask: "What does this system need that they haven't thought of?"
2. Propose 2-3 approaches with trade-offs
3. Get user approval on each section
4. Write design doc to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`

**Questions to ask:**
- What happens when this scales?
- What happens when this fails?
- What happens when users misuse it?
- What security issues exist?
- What privacy concerns exist?
- What accessibility issues exist?

---

## Step 2: Doctor the Code

**Load:** `@code-doctor`

**Do:**
1. Apply phases 1-6 to the ENTIRE codebase
2. Find: bugs, dead code, missing features, security issues
3. Fix: critical issues first, then functional, then quality
4. Verify: syntax, imports, integration, tests

**Checklist:**
- [ ] Every file reviewed
- [ ] Every dependency checked
- [ ] Every integration tested
- [ ] Every error path handled
- [ ] Every security issue fixed

---

## Step 3: Test Everything

**Load:** `@test-driven-development`

**Do:**
1. Write tests for EVERY feature
2. Red-Green-Refactor cycle for each
3. No production code without a failing test first
4. Verify: test fails before implementation, passes after

**Rules:**
- Write test first
- Watch it fail
- Write minimal code to pass
- Watch it pass
- Refactor if needed
- Repeat

---

## Step 4: Build What's Missing

**Do:**
1. Implement the unasked features from Step 1
2. Fix the bugs found by code-doctor in Step 2
3. Add tests for everything in Step 3
4. Verify: all tests pass, no regressions

---

## Output

A complete, tested, production-ready system that:
- Solves the original problem
- Handles edge cases
- Has tests for everything
- Is documented
- Is secure
- Is accessible
