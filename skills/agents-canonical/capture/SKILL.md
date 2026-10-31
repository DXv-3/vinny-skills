---
name: capture
description: End-of-session capture checklist for Vinny's agent ecosystem. Run at session close (or when the user says "capture" / "close out"). Enforces the eco router's CAPTURE contract — every session output lands in exactly one ledger, dated, with nothing lost.
---

# Capture — session-close checklist

Run this at session end. Every output goes to **exactly one** place; when in doubt, ask rather than duplicate.

## The checklist (run in order, act on each)

1. **Ledgers updated (dated append)?**
   - Project state / next actions → append a dated line to `~/Projects/CONQUEST-PLAN.md` (what's next) or `~/Projects/BUILD-STATE-2026-09-21.md` (current builds) or `~/Projects/NIGHT-SHIFT-LOG.md` (history).
   - Never rewrite existing lines — append only.
2. **Memory additions recorded with source?**
   - Cross-session preferences/corrections → memory, each entry carrying the source session id or path.
3. **KB additions?**
   - Reusable domain knowledge → youtube-kb (text) or prompt_kb (prompts). Ingests are resumable; never re-ingest a mid-run channel.
4. **Pending gates changed?**
   - Re-check `~/Projects/CONQUEST-PLAN.md` money/gate lines; surface changes as one line each. A gate that moved gets a dated line in the ledger it lives in.
5. **Stale claims noticed?**
   - Follow Appendix E of the design doc: re-verify on disk with the owning query → update the canonical spine section + stamp `last-verified` → recopy canonical → copies (never edit copies) → log a dated line in NIGHT-SHIFT-LOG.
6. **Conflicting state docs?**
   - Precedence: CONQUEST-PLAN > BUILD-STATE > NIGHT-SHIFT-LOG; resolve toward newer mtime and note the resolution here.
7. **Print the CAPTURE: line** for the next session:
   `CAPTURE: <ledgers touched> · <gates changed> · <memory added> · <nothing | pending>`

## Hard rules (inherited, binding)

- Nothing auto-sends · nothing deletes · no credentials in code or logs.
- Session-scoped scratch stays in `.zwork/runs/` — never promoted.
- Ledger entries are append-only and dated; a crashed session's gap is backfilled from `.zwork/runs/` by the next capture.
