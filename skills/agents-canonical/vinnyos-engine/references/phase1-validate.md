# Phase 1: VALIDATE

Detailed steps for stress-testing plans.

---

## Step 1: Write the Plan

**Load:** `@writing-plans`

**Do:**
1. Create implementation plan with exact file paths
2. Include code snippets for every step
3. Make every step 2-5 minutes (bite-sized)
4. Include test cases for every feature
5. Save to `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

**Check:**
- [ ] Every file path exists or will be created
- [ ] Every dependency is available
- [ ] Every integration point is tested
- [ ] Every error path is handled
- [ ] Plan follows DRY, YAGNI, TDD

---

## Step 2: Debug the Plan

**Load:** `@systematic-debugging`

**Apply phases 1-3 TO THE PLAN (not code):**

### Phase 1: Root Cause Investigation
- Read the plan carefully
- What could go wrong with this approach?
- What assumptions does the plan make?
- What dependencies does it assume?

### Phase 2: Pattern Analysis
- Find similar projects that succeeded
- What did they do differently?
- What patterns did they use?
- What pitfalls did they avoid?

### Phase 3: Hypothesis and Testing
- Form hypothesis: "This plan will fail because X"
- Test: "What evidence supports/refutes this?"
- Repeat for each major component

---

## Step 3: Validate

**Checklist:**
- [ ] Every file path exists or will be created
- [ ] Every dependency is available (pip install, npm install)
- [ ] Every integration point is tested (API calls, file I/O)
- [ ] Every error path is handled (try/catch, validation)
- [ ] Plan follows DRY (no duplication)
- [ ] Plan follows YAGNI (no unnecessary features)
- [ ] Plan follows TDD (tests before code)

**If any check fails:** Fix the plan, re-run validation.

---

## Output

A validated, debugged plan ready for execution.
