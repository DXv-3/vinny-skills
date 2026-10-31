---
name: code-doctor
description: "Forced chain for debugging, fixing, and reviewing code. Use when the user says 'review and fix', 'debug this', 'check my code', 'what's broken', or wants a thorough code audit. Runs a mandatory 7-phase chain — no skipping, no partial reviews."
version: 2.1.0
---

# Code Doctor

A systematic, non-optional chain for finding and fixing bugs in any codebase. Every phase must complete before the next begins. No shortcuts. No "looks good to me" without evidence.

---

## Phase 0: PROFILE (know what you're reviewing)

Run BEFORE Phase 1. Lightweight scan only — no file reads.

1. **Determine project type**: web app, CLI, library, mobile app, desktop app, serverless, or other.
2. **Identify languages**: scan top-level config files (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `*.xcodeproj`, `CMakeLists.txt`) and top-level file extensions. This is approximate — refine during Phase 1.
3. **Flag inapplicable Phase 3 items now**: items tagged `[Web]`, `[API]`, or `[Mobile]` that don't match this project type are N/A. Write them down as "N/A for [reason]".
4. **Plan Phase 1 scope**: if the file count is >100, decide: full read (small projects) or read entry points + configs fully, scan remaining files for exports/imports only.
5. **Add project-specific checklist items**: 3-5 common pitfalls for this platform (see Platform Pitfalls appendix at the bottom of this document). Write them under Phase 3.

**Checkpoint:** Project type, languages, N/A items, and scope decision written down. Phase 1 will reference this.

---

## The Chain

### Phase 1: READ (understand everything)

**Do not edit anything yet.**

1. List every file in the project. Use `git ls-files` if available, otherwise glob broadly excluding `node_modules/`, `.git/`, `build/`, `dist/`, `__pycache__/`, `DerivedData/`. Include: all source code (`.swift`, `.go`, `.rs`, `.py`, `.js`, `.ts`, `.kt`, `.java`, `.cpp`, `.c`, `.h`, `.m`, `.mm`), all config (`.plist`, `.yml`, `.yaml`, `.toml`, `.json`, `.xcconfig`, `.entitlements`), build files (`Makefile`, `Dockerfile`, `*.xcodeproj/project.pbxproj`), and docs (`.md`).
2. Read every file if the project is small (<100 files). For larger projects, read entry points + config files fully, scan remaining files for exports/imports.
3. For each file, answer:
   - What is its purpose?
   - What does it import/depend on?
   - What does it export/expose?
   - What external services does it call?
   - What version of each dependency is required? Is it in the manifest?
4. Build a **dependency map**: which files reference which other files. Write it down. Verify each edge resolves to a real file or installed package — flag broken imports now.
5. Refine the Phase 0 language list with any languages discovered during file reads.

**Checkpoint:** Output a file manifest (path + role + imports/exports). Phase 2 must cite from this list.

---

### Phase 2: MAP (trace the data flow)

Still no editing.

1. Trace the primary user flow from entry point to completion. Split into two halves:
   - **Input path**: entry point → parser/handler → processing. For a web app: request → handler → service. For a CLI: command → parser → action.
   - **Output path**: processing result → delivery. Does the output reach the user/screen/speaker/file/next-step? Or is it computed and silently discarded?
2. For each step, note:
   - What inputs does it expect?
   - What outputs does it produce?
   - What happens on error?
3. Identify **integration points** — where does this code talk to something external (API, filesystem, database, another process)?
4. **API contract check**: for each integration point, triage:
   - **Core APIs** (3-5 that define the project's purpose): read their documentation. Verify they actually do what the code assumes. Ask: does this API INTERCEPT, COPY, TRANSFORM, or PROXY the data?
   - **Infrastructure APIs** (auth, DB, cache): verify one key behavior.
   - **Utility APIs** (JSON parse, file read, string format): trust the name, move on.
5. Write a one-paragraph summary: "The system does X by calling Y, which produces Z. Every external API call is appropriate for its task."

**Checkpoint:** Output a flow diagram: A → B → C with function names + file:line. Confirm the output reaches a destination. Confirm each core API is being used for what it actually does, not what the code assumes.

---

### Phase 3: CATEGORIZE (find every issue)

Still no editing. Now you hunt.

For every file, check against this checklist. Write down every hit. Items tagged with a platform prefix only apply to that platform type.

#### Critical (will crash or silently corrupt)
- [ ] Import path won't resolve at runtime (wrong module name, wrong working directory)
- [ ] Missing required dependency not in manifest
- [ ] Type mismatch: function expects X, caller passes Y
- [ ] Unhandled exception that crashes the process
- [ ] Resource leak: file handle, connection, memory never released
- [ ] Race condition or thread safety issue
- [ ] **[ARC/RC]** Retain cycle: object A strongly references B, B strongly references A — neither deallocates
- [ ] **[GC]** Goroutine/thread leak: started, never stopped or joined
- [ ] **[JS]** Event listener or interval registered, never removed/cleared
- [ ] API capability mismatch: code assumes API does X, but the API actually does Y (or cannot do X at all)
- [ ] Broken output path: data is computed but the path to the user/screen/file/next-step is missing or severed
- [ ] Hardcoded value that breaks in production (localhost, absolute paths, dev tokens)

#### Functional (works but wrong)
- [ ] Logic error: code does A when it should do B
- [ ] Dead code: function defined but never called — FIRST check if it's infrastructure for a not-yet-wired feature (look for setup/teardown patterns, connections to other components). True dead code has no setup pattern, no connections.
- [ ] Dead import: module imported but never used
- [ ] Missing feature: comment/plan says "TODO" or "FIXME" or code skips a step
- [ ] Wrong API shape: endpoint expects X but client sends Y
- [ ] Error swallowed: except/pass/_ hides real failures
- [ ] Stale state: variable holds old value after it should update
- [ ] No state persistence: settings/state resets on every launch when users expect it to be saved

#### Quality (works, but will cause problems)
- [ ] No input validation on public-facing parameters
- [ ] No logging on error paths
- [ ] **[Web]** No rate limiting on public endpoints
- [ ] Memory leak: objects allocated but never freed (closures, event listeners, object URLs)
- [ ] **[All]** Resource churn: hot path creates >100 heap objects/sec, spawns >10 fire-and-forget tasks/sec, or shows monotonic allocation growth over 30 seconds
- [ ] Duplicate code: same logic in multiple places
- [ ] Unexplained magic numbers: numeric literals without named constants or explanatory context
- [ ] No documentation on non-obvious behavior
- [ ] **[Web]** CORS too wide
- [ ] Security: secrets in code
- [ ] **[Web]** No auth on sensitive endpoints

**Checkpoint:** List every issue with file:line reference. Group by severity. If the list is empty, you didn't look hard enough — re-read Phase 1. Mark any N/A items from Phase 0 explicitly as "N/A — [reason]".

---

### Phase 4: FIX (apply fixes in priority order)

Now you edit. One severity level at a time.

1. **Fix all Critical issues first.** Each fix should be minimal — change the smallest amount of code necessary.
2. **Then fix Functional issues.** Remove dead code, wire up missing connections, implement skipped features.
3. **Then fix Quality issues.** Add validation, logging, cleanup.

Rules during fixing:
- **Single-file fix**: edit one file → build → verify syntax → next file.
- **Atomic multi-file fix** (same change touches 2+ files simultaneously): list all affected files first → edit all → build once. Example: renaming an import across multiple files.
- **Never batch unrelated fixes** across files before building.
- After editing a file, verify its syntax. See Multi-Language Reference for commands.
- Never fix one thing by breaking another. Re-read the dependency map before changing imports.
- After each severity level completes, re-run the Phase 5 smoke test to catch regressions.

**Checkpoint:** Copy the Phase 3 issue list. Under each issue, write the fix applied + file:line. Nothing was skipped without a documented reason.

---

### Phase 5: VERIFY (prove it works)

Three sub-phases: BUILD, FUNCTIONAL, RUNTIME.

#### BUILD
1. **Syntax check** every edited file. All must pass.
2. **Import check**: verify that all import paths resolve, all file references are correct, all environment variables are documented.
3. **Build the project**. Must compile without errors.

#### FUNCTIONAL
4. **Smoke test**: Run the project. Exercise ONE core user action. Did it produce the expected result? Does a volume booster make audio louder? Does a CLI actually process the file? Ask: would a user be satisfied?
   - If the project CAN be run: run it. Record PASS or FAIL.
   - If the project CANNOT be run (requires hardware, paid API keys, enterprise VPN): document exact steps a human would need. Record BLOCKED.
   - **Loop guard**: if 3 consecutive smoke test failures have the same root cause, classify as FUNDAMENTAL. Document it. Proceed to Phase 6. Do not keep looping.

#### RUNTIME
5. **Resource churn check**: If the project has callback loops (audio buffers, network sockets, timers), run for 10-30 seconds and check: excessive allocations, runaway Task/goroutine creation, unbounded memory growth. Use Activity Monitor / Instruments / `htop` / `ps`.
6. **Re-read every edited file** one more time. Look for typos you introduced.

**Checkpoint:** BUILD passes. FUNCTIONAL result (PASS/FAIL/BLOCKED) recorded with evidence. RUNTIME shows no resource churn.

---

### Phase 6: REVIEW (the final pass)

One last read-through. This time, ask:

1. **Does the fix solve the original problem?** Re-read the original issue/bug report/feature request against the changed code. Confirm the fix addresses it.
2. **Did I check my assumptions?** Before removing "dead code," did I confirm it wasn't infrastructure? Before trusting an API, did I verify its contract?
3. **Did I introduce new bugs?** Re-check every edit against the original code's intent.
4. **Did I miss anything?** Re-scan the Phase 3 checklist one more time.
5. **Is the fix minimal?** Did I change more than necessary?
6. **Would a stranger understand this?** Are the changes self-documenting?
7. **What did I NOT fix and why?** Explicitly list deferred items with reason.

**Produce the final report:**

```
## Code Review: [project name]

### Profile
- Project type: [web/CLI/library/mobile/desktop]
- Languages: [list]
- Scope: [file count]

### Files reviewed: [count]
### Issues found: [count] (X critical, Y functional, Z quality)
### Issues fixed: [count]
### Files edited: [list with line counts]
### N/A items: [list with reasons]

### Critical fixes:
- [file:line] — [what was wrong] → [what you did]

### Functional fixes:
- [file:line] — [what was wrong] → [what you did]

### Quality fixes:
- [file:line] — [what was wrong] → [what you did]

### Deferred: [list with reasons]

### Smoke test: [PASS / FAIL / BLOCKED] — [evidence]

### Unfixable architectural issues: [list]
```

---

## Tooling (use it — don't redo this work by hand)

The deterministic parts of this chain are implemented in `~/bin/codedoctor`
(Python stdlib-only; library importable as `codedoctor` from the skill dir).
Run these instead of re-deriving results manually:

| Phase | Command | Replaces |
|-------|---------|----------|
| 0 PROFILE | `codedoctor profile <dir>` | manual config-file scan |
| 1 READ | `codedoctor scan <dir>` (manifest included) or `--json` for machines | manual file listing + import/export extraction |
| 3 CATEGORIZE | `codedoctor scan <dir>` — findings are **candidates**, verify each before fixing | regex hunting by hand |
| 5 BUILD gate | `codedoctor check-syntax <file>...` after every edit | ad-hoc syntax checks |
| 6 REVIEW | `codedoctor run <dir>` then `codedoctor report <dir>` | hand-written report skeleton |

Workflow integration:

1. Start with `codedoctor run <dir>` — saves `.code-doctor/state.json`.
2. Use its findings + manifest as Phase 1/3 evidence. Static rules are
   heuristics: a finding is a candidate to verify, not a verdict.
3. Phases 2 (API contracts), 4 (fixes), and the judgment parts of 6 remain YOUR
   responsibility — no tool substitutes for reading the code.
4. After each fix, re-run `check-syntax` on edited files and re-run `scan` to
   confirm findings cleared.

Library use (from any Python code):
```python
import sys; sys.path.insert(0, os.path.expanduser("~/.config/opencode/skills/code-doctor"))
from codedoctor import profile_project, build_manifest, find_issues, verify_files, SessionState
```

Tests: `python3 -m unittest discover tests` from the skill dir (69 tests).

---

## Trigger Phrases

| User says | What you do |
|-----------|-------------|
| "review and fix" | Run full chain |
| "debug this" | Run full chain, emphasize Phase 3 Critical |
| "check my code" | Run full chain |
| "what's broken" | Run full chain |
| "code review" | Run full chain |
| "audit" | Run full chain |
| "find bugs" | Run full chain, emphasize Phase 3 |
| "fix everything" | Run full chain |

---

## Rules

1. **Never skip a phase.** The chain is mandatory. Phase 0 aligns the checklist to the project. Phase 2 catches wrong-API assumptions. Phase 5 catches non-functional fixes.
2. **Never edit during Phase 0-3.** Reading and editing in the same pass causes tunnel vision.
3. **Never say "looks good" without the checklist.** Subjective review is not review. Every claim needs a file:line reference.
4. **Always produce the Phase 6 report.** The report is the artifact. It proves the chain ran.
5. **If >100 files, Phase 1 reads entry points + configs fully, scans remaining files.** Full reads come later for files referenced by entry points.
6. **Adapt the checklist to the project type.** Mark inapplicable items N/A. Add project-specific items from Phase 0.
7. **Verify API contracts during Phase 2.** Every core API call must be checked against its actual documented behavior. Never assume.
8. **Distinguish dead code from incomplete infrastructure.** Before deleting unused code, verify it's not a not-yet-wired component. Look for setup/teardown patterns.
9. **Guard against infinite loops.** 3 consecutive smoke test failures with the same root cause = FUNDAMENTAL issue. Document and proceed.
10. **Every checkpoint produces a verifiable artifact** that the next phase consumes. No self-assessment — output evidence.

---

## Multi-Language Quick Reference

| Language | Syntax check | Build | Profile (mem/churn) |
|----------|-------------|-------|---------------------|
| Swift | `swiftc -parse file.swift` | `xcodebuild build` or `swift build` | Instruments (Allocations) |
| Python | `python3 -c "import ast; ast.parse(open('f').read())"` | `python3 -m compileall .` | `memory_profiler` / `tracemalloc` |
| JS/TS | `node --check file.js` | `npm run build` | `node --inspect` + Chrome DevTools |
| Go | `go vet ./...` | `go build ./...` | `go test -bench=. -benchmem` / `pprof` |
| Rust | `rustc --edition 2021 --check file.rs` | `cargo build` | `cargo bench` / `valgrind` |
| C/C++ | `gcc -fsyntax-only file.c` | `make` / `cmake --build .` | `valgrind --leak-check=full` |
| Java | `javac -d /dev/null file.java` | `./gradlew build` or `mvn compile` | VisualVM / `jcmd` |
| Kotlin | `kotlinc -d /dev/null file.kt` | `./gradlew build` | VisualVM |

For any language not listed, find: (1) syntax checker, (2) type checker or linter, (3) build system. Add your language to this reference when you encounter it.

---

## Platform Pitfalls — Top 5 Per Language

Use these in Phase 0 step 5 to add project-specific checklist items.

### Swift
- [ ] Force-unwrap (**!**) on optional that can be nil at runtime
- [ ] **@Published** property updated from background thread
- [ ] Strong delegate reference cycle (use **weak**)
- [ ] Missing privacy description in Info.plist (**NSCameraUsageDescription**, etc.)
- [ ] **try!** or **try?** on throwing call that should propagate the error

### JavaScript / TypeScript
- [ ] Response sent but handler continues executing (missing **return** after **res.json()**)
- [ ] **useEffect** runs on every render (missing or empty dependency array)
- [ ] Event listener / **setInterval** registered, never cleaned up
- [ ] **await** missing on async function call
- [ ] **process.env** accessed without fallback

### Python
- [ ] Mutable default argument (**def f(x=[])**)
- [ ] **except:** or **except Exception:** without logging — swallows all errors
- [ ] Relative import that won't resolve (**from . import** outside a package)
- [ ] File handle not closed (use **with** statement)
- [ ] **is** used for value comparison instead of **==**

### Go
- [ ] Error returned but not checked (**_**, or ignored)
- [ ] Goroutine started, never stopped (no **context.Context** or **done** channel)
- [ ] Defer in loop — accumulates until function returns
- [ ] **nil** map or slice accessed without initialization
- [ ] Race condition on shared variable (run with **-race**)

### Rust
- [ ] **.unwrap()** or **.expect()** on **Result**/**Option** that can fail
- [ ] Blocking call inside **async** function without **spawn_blocking**
- [ ] **unsafe** block without safety documentation
- [ ] Clone in hot loop instead of reference
- [ ] Missing **Send + Sync** bounds on types crossing thread boundaries

### React (JSX/TSX)
- [ ] State update on unmounted component (missing cleanup in **useEffect**)
- [ ] Key prop missing or using index as key in lists
- [ ] Derived state not memoized (**useMemo** / **useCallback** missing)
- [ ] Effect runs on every render (missing dependency array)
- [ ] Controlled/uncontrolled input switching
