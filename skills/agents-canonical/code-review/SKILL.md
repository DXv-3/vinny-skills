---
name: code-review
description: Perform comprehensive code reviews of diffs, patches, PRs, or file changes. Use when asked to review, audit, or check code for bugs, regressions, security issues, performance problems, data integrity risks, or missing tests; also use for reviewing refactors, migrations, config changes, and infra changes.
---

# Code Review

## Overview

Deliver risk-focused code reviews that prioritize correctness, safety, and test coverage. Produce findings with severity and file/line references, then summarize residual risks and follow-up steps.

## Workflow

### 1) Set scope and context

Confirm what is being reviewed (diff, branch, files, or a specific feature). If scope is unclear, ask for the base branch, target branch, or file list. Note any assumptions in the review output.

### 2) Gather evidence

Prefer diffs and open only the relevant files. Use fast search to trace changes across the codebase.

- Use `git status`, `git diff`, and `git diff --stat` to understand scope.
- Use `rg` to find related call sites, configs, and tests.
- Inspect new/modified files and any touched dependencies.

### 3) Review by risk category

Focus on issues that can break behavior, data, or security.

- Correctness and logic: edge cases, null handling, boundary checks.
- Data integrity: persistence, migrations, transactional guarantees, idempotency.
- Security and privacy: authZ/authN, injection, unsafe deserialization, secrets.
- Reliability: retries, timeouts, error handling, cleanup, resource leaks.
- Performance: hot paths, N+1, unbounded loops, large allocations.
- Compatibility: API/contract changes, backward compatibility, config drift.
- Observability: logs, metrics, tracing, error reporting.

### 4) Tests and validation

Check for test coverage of new behavior and failure modes. Identify missing tests, flaky assumptions, or outdated snapshots. If tests were not run, state that clearly.

### 5) Report clearly

Put findings first and order by severity. Each finding should include file/line references, evidence, and a concise suggestion or question.

#### Severity scale

- Blocker: likely data loss, security breach, or broken core behavior.
- High: incorrect behavior or high-risk regression in typical usage.
- Medium: edge-case bugs, reliability gaps, or maintainability risks.
- Low: minor issues, clarity gaps, or cleanups.

#### Output template

Use this structure unless the user specifies otherwise:

1) Findings (ordered by severity)
   - `<severity>` `path:line` - Issue summary. Evidence. Suggested fix.
2) Questions/assumptions
3) Summary (brief)
4) Testing (what ran, what did not)
5) Suggested next steps (numbered if multiple)

## Review etiquette

- Avoid style-only nits unless asked or they obscure correctness.
- Avoid speculative issues; tie claims to evidence in the code.
- If no issues found, say so explicitly and call out residual risks or testing gaps.
