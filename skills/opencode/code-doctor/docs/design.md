# Code Doctor Tooling — Design

**Date:** 2026-08-22
**Status:** Approved (user delegated language/scope decisions)
**Spec:** `../SKILL.md` is the authoritative spec; this tooling makes its deterministic phases executable.

## Problem

Code Doctor exists as LLM instructions only. Deterministic work (profiling, file
manifests, pattern detection, syntax gates, report scaffolding) is re-done by hand
every run and varies between agents. The chain needs real code underneath it.

## Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Language | Python 3, **stdlib only** | Matches user's ecosystem (HELIOS, manus-lite); zero dep risk |
| Location | Inside skill dir | Self-contained: `~/.config/opencode/skills/code-doctor/` |
| Access | `~/bin/codedoctor` launcher + importable `codedoctor` package | CLI + library + skill enhancement = all three requested forms |
| Judgment work | Stays with the LLM (Phases 2/4/6 reasoning) | Regexes find candidates; agents verify contracts and fix |

## Architecture

```
codedoctor/
├── __init__.py     # public API surface
├── profile.py      # Phase 0: project type, languages, scope, N/A flags
├── manifest.py     # Phase 1: file walk + imports/exports/entry points
├── issues.py       # Phase 3: rule engine (Platform Pitfalls as regex rules)
├── verify.py       # Phase 5: per-language syntax-check dispatcher
├── report.py       # Phase 6: markdown report generator
└── state.py        # checkpoint persistence → <project>/.code-doctor/state.json
code_doctor.py      # CLI entry (argparse subcommands)
tests/              # stdlib unittest suite
```

### Data flow

`profile_project(dir)` → Profile dict
`build_manifest(dir)` → entries [{path, lang, imports[], exports[]}], entry_points[]
`find_issues(dir, manifest?)` → findings [{severity, file, line, col, rule_id, message}]
`verify_files(files)` → results [{file, ok, status, output}]
`generate_report(state)` → markdown string
`SessionState.save/load()` chains phases across invocations via JSON.

CLI: `codedoctor profile|scan|check-syntax|report|run <dir>` — `run` executes the
full deterministic chain. Output human-readable by default, `--json` for machines.
Exit codes: 0 clean / 1 findings / 2 error.

### Rules (Phase 3 engine)

Every deterministic item from SKILL.md Platform Pitfalls appendix:

- Swift: force unwrap, `try!`, `try?`
- Python: mutable default args, bare/broad except, `is True/False`, open() without with
- Go: discarded err assignments, defer inside loop
- Rust: `.unwrap()`, `.expect(`
- JS/TS: process.env without fallback, setInterval/addEventListener without cleanup,
  res.json without return
- React: index-as-key
- Generic: hardcoded secrets, hardcoded localhost, TODO/FIXME/HACK markers

Rules are heuristics: findings are candidates for the agent to verify, not verdicts.

## Error handling

- Unreadable files: skipped, counted in manifest.warnings
- Unknown languages in verify: status "unsupported" (not a failure)
- Missing toolchain (no node/swiftc/etc): status "tool-missing" (not a failure)
- All exceptions at CLI boundary → exit 2 with message on stderr

## Testing (TDD)

Stdlib unittest. Each module: tests written first, watched failing, then implemented.
Fixture projects constructed in tempdirs. Final smoke test runs the full chain on a
real project (`~/Projects/manus-lite`).
