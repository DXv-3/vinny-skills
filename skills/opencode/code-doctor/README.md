# Code Doctor Tooling

Executable implementation of the deterministic phases in [SKILL.md](SKILL.md).
Python 3, **stdlib only** — no dependencies to install, nothing to break.

## Install status

Already wired on this machine:

- CLI: `~/bin/codedoctor` (on PATH)
- Library: `~/.config/opencode/skills/code-doctor/codedoctor/`
- Tests: `python3 -m unittest discover tests` from this dir

## Quick start

```bash
codedoctor run ~/Projects/my-app      # full chain → .code-doctor/state.json
codedoctor scan ~/Projects/my-app     # profile + manifest + findings (human)
codedoctor scan --json <dir>          # same, machine-readable
codedoctor check-syntax a.py b.go     # Phase 5 gate after edits
codedoctor report ~/Projects/my-app   # Phase 6 markdown from saved state
```

Exit codes: `0` clean · `1` findings found · `2` error.

## What it covers

| Module | SKILL phase | Deterministic work |
|--------|-------------|--------------------|
| `profile.py` | 0 | project type, languages, scope decision, N/A flags, pitfall checklist |
| `manifest.py` | 1 | file walk (git-aware), imports/exports per language, entry points |
| `issues.py` | 3 | 17 rules: Swift force-unwrap/try!, Python mutable-default/bare-except/is-compare/open-without-with, Go blank-assign/defer-in-loop, Rust unwrap/expect, JS env-fallback/interval-leak/res.json-no-return, React index-key, secrets/localhost/TODO |
| `verify.py` | 5 | syntax gates: py(ast) js(node) swift(swiftc) go(gofmt) rs(rustc) c/cpp(cc) |
| `report.py` | 6 | markdown report skeleton with counts + findings |
| `state.py` | all | `.code-doctor/state.json` chains phases across invocations |

**Rules are heuristics.** A finding means "verify this", not "this is broken".
Phases 2 (API contract checks), 4 (fixing), and judgment calls stay with the agent.

## Library API

```python
import sys, os
sys.path.insert(0, os.path.expanduser(
    "~/.config/opencode/skills/code-doctor"))
from codedoctor import (
    profile_project, build_manifest, find_issues,
    verify_files, generate_report, SessionState,
)

findings = find_issues("~/Projects/my-app")
for f in findings:
    print(f["severity"], f["file"], f["line"], f["rule_id"], f["message"])
```

Add a rule in ~6 lines: build one with `line_rule(id, severity, langs, msg, regex)`
and append to `RULES` in `issues.py` — the test suite shows the pattern.

## Design

See [docs/design.md](docs/design.md). TDD throughout: every module's tests were
written and watched failing before implementation.
