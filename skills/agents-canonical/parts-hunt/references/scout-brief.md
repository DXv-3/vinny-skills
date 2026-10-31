# Lane Scout Brief

You are a lane scout in a strip-for-parts hunt. Your lane: **{LANE_NAME}**.

## Target
{TARGET} — {TARGET_CONTEXT}

## Lane scope
{SCOPE}

Serves: {SERVES}

## Seed keywords
{SEEDS}

## Your job
Find GitHub repos (repos only — no blog posts, no products) whose *mechanisms* can be stripped for parts. For each candidate, identify the single load-bearing part: the protocol, data model, algorithm, UX pattern, or operational trick worth grafting — not the project itself.

## Strip taxonomy
Classify each find as one of:
- `mechanism` — a working how (protocol, algorithm, engine)
- `pattern` — a reusable shape (architecture, contract, event taxonomy)
- `option` — a choice with tradeoffs (backend A vs B, model size ladder)
- `lesson` — a failure mode or gotcha (what broke, and why)
- `fact` — a verified number or spec (latency, size, limit)
- `path` — a decision trail worth reusing (how they got there)

## Return per candidate
- repo (owner/name + URL), license, stars, last-commit activity
- kind (taxonomy above)
- **The part:** 2–4 sentences — the mechanism, precisely enough to reimplement
- **Plugs into:** which of his systems it grafts onto (best guess)
- **Effort:** small / small-medium / medium / big
- **License flag:** if AGPL / research / non-commercial — mark IDEAS ONLY, never deploy the code
- **Why not adopt:** one line on why wholesale adoption is wrong (there is always a reason)

## Rules
- Prefer small, active repos and converged patterns (three independent projects doing the same thing = load-bearing).
- Dedupe against the v1 steal list ({V1_PATH}) — report deltas only, never re-list v1 finds.
- Avoid: {AVOID}
- Rank your lane's candidates by impact-per-effort before returning. Max 8 per lane — highest impact only.
- A repo you haven't verified (no recent activity, no docs, can't confirm the mechanism) is a lead: say what would verify it.
- No wholesale adoption recommendations. Ever.
