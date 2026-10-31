---
name: research-to-adults
description: "Research to Adults"
---

# Research to Adults

A finished deep-research folder (`research_notes/<slug>/` with `report.md` + `notes/`)
is raw material — a bright kid. Adults are what it grows into: documents that are
complete, honest about caveats, actionable, and dated. This skill is the repeatable
way to raise them. It runs in this model, start to finish.

## The four adults (always the same family)

1. **01-decision-brief.md** — the 2-minute read. Verdict up top, the pick in one
   breath, what it costs, what changed vs earlier advice (corrections stated out
   loud), the 5 highest-leverage facts, open questions condensed, and ONE named
   next action with an owner.
2. **02-build-playbook.md** — ordered steps a builder can execute. Copy-paste-real
   commands only; every command traceable to the report or flagged as standard
   practice. Each step: what, the command, how to verify it worked, the failure
   mode and its fallback.
3. **03-scorecard.md** — the report's tables as a standalone reference: per-tool
   scorecard (free ceiling, YouTube support, API, privacy grade, role) and the
   recommended architecture (layer, pick, why, fallback-if-it-dies).
4. **04-watchlist.md** — every volatile fact with its expiry date: allegations and
   legal deadlines, grants that expire, limits already slashed once, stalled
   maintainers, disputed tiers, renames. Each entry: what, the date, what to
   re-check and when.

## Pipeline

1. Read `report.md` fully; skim `notes/` for anything the report compressed.
2. Extract: the verdict, the volume math, layer picks + fallbacks, per-tool
   ceilings, the 5 highest-leverage facts, corrections to earlier advice given to
   the user, open questions, dated/volatile facts.
3. Write the four adults to `~/workspace/your_files/<slug>-adults/`.
4. Run the well-adjusted checklist below on each. Fix failures before shipping.

## The well-adjusted checklist (all four must pass)

- **Traceable:** every claim traceable to `report.md`. No new facts invented.
- **Honest:** caveats preserved, never smoothed. "Flagged uncertain" in the
  report stays flagged in the adult.
- **Actionable:** the playbook's commands run as written; the brief ends in one
  named next action with an owner (him or me), never "consider exploring".
- **Dated:** everything volatile carries its date. An adult that can't tell you
  when it expires isn't an adult.
- **Short:** the brief fits a 2-minute read. Detail lives in the playbook and
  scorecard, not the brief.

## After raising

- `shelf.py add` anything strip-worthy learned while raising (a new failure mode,
  a verification trick, a pricing catch).
- If the research corrected earlier advice, the corrections go in the brief's
  "what changed" section — stated out loud, never buried.
