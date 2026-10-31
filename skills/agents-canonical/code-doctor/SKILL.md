---
name: code-doctor
description: "Forced 7-phase chain for debugging, fixing, and reviewing code: use when the user says 'review and fix', 'debug this', 'debug this crash', 'check my code', \"what's broken\", 'find the bug', 'fix this error', or wants a thorough code audit. No skipping, no partial reviews; deterministic CLI tooling included."
---

# Code Doctor

A systematic, non-optional chain for finding and fixing bugs in any codebase. Every phase must complete before the next begins. Full spec + CLI live at:
`~/.config/opencode/skills/code-doctor/` (SKILL.md = the chain; `code_doctor.py` = the deterministic tooling; wrapper: `~/bin/codedoctor`).

Read the full chain there, then work it. Summary of the phases:

0. **PROFILE** — project type, languages, scope decision, platform pitfalls. (`codedoctor profile <dir>`)
1. **READ** — manifest + dependency map, broken imports flagged. (`codedoctor scan <dir>`)
2. **MAP** — trace input path → output path; verify core API contracts (does the API do what the code assumes?).
3. **CATEGORIZE** — checklist hunt: Critical / Functional / Quality. Findings from `scan` are candidates — verify each.
4. **FIX** — Critical first; single-file fixes, atomic multi-file only for same change; build between severities.
5. **VERIFY** — BUILD (syntax/imports/build) → FUNCTIONAL (one real user action, PASS/FAIL/BLOCKED; 3 same-cause failures = FUNDAMENTAL, stop looping) → RUNTIME (resource churn over 10-30s).
6. **REVIEW** — fix solves the original problem? new bugs? minimal? then `codedoctor report <dir>` for the structured report.

## Rules
- No editing before Phase 3 completes. No skipping phases, ever.
- Static findings are heuristics: verify before fixing; never weaken tests to pass.
- Loop guard: 3 consecutive smoke-test failures with the same root cause → classify FUNDAMENTAL, document, proceed.
- Deferred items get explicit reasons in the final report.
