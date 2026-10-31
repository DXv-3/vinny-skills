---
name: deep-research-free
description: >
  Use when the user requests deep research, exhaustive research, comprehensive
  report, thorough investigation, deep dive, multi-source SOTA review, or
  /deep-research-free — especially when Parallel auth/API is unavailable or they
  want zero-cost research. Not for simple lookups, debugging, or 1–2 search answers.
  Prefer parallel-deep-research only if user asks for Parallel and CLI is authed.
user-invocable: true
argument-hint: <topic>
---

# Free Deep Research (Parallel-pattern, zero auth)

Research topic: $ARGUMENTS

**Core principle:** Ship the *process UX and artifacts* of Parallel deep research using only built-in search/fetch/GitHub tools. No `parallel-cli`, no API key, no balance.

| Layer | Parallel does | Free does |
|-------|---------------|-----------|
| Engine | Hosted multi-agent retrieval | You + `web_search` / `web_fetch` / `open_page` / `gh` / X tools |
| Kickoff | Instant `run` + monitor URL | Announce plan + depth tier + filename; start parallel searches |
| Depth tiers | lite → ultra processors | Same tier names, mapped to search budget |
| Artifacts | `$NAME.md` + `$NAME.json` | Same dual files under `~/Documents/research/` |
| Follow-ups | `--previous-interaction-id` | `interaction_id` in JSON; reload prior artifacts |
| Cost | Paid / balance | Free |

**Also available:** full `deep-research` skill (evidence.jsonl / HTML / PDF) if user wants claim ledgers and packaging scripts.

---

## When to use / NOT use

**Use when** user wants deep/exhaustive/comprehensive multi-source research without Parallel (or Parallel is unauthenticated).

**Do NOT use when:**
- Simple lookup / fact-check → one or two `web_search` calls
- Parallel is requested *and* `parallel-cli` is authed → use `parallel-deep-research`
- User wants full claim-ledger HTML/PDF pipeline → use `deep-research`

---

## Depth tiers (reverse-engineered from Parallel processors)

Choose a tier from the request. Default: **pro**.

| Tier | When | Search budget | Primary fetches | Critique pass | Typical wall time |
|------|------|---------------|-----------------|---------------|-------------------|
| `lite` | Follow-ups, narrow drill | 3–4 queries | 0–1 | No | ~1–3 min |
| `base` | Simple comparative Q | 5–6 queries | 1–2 | No | ~3–6 min |
| `core` | Moderate multi-angle | 6–8 queries | 2–4 | Light | ~5–10 min |
| `pro` | **Default** exploratory | 8–12 queries across ≥4 surface types | 3–6 | Yes | ~8–15 min |
| `ultra` | Explicit multi-source / SOTA / “cover GitHub Reddit X arXiv” | 12–20+ queries, surface matrix mandatory | 5–10 | Yes + conflict table | ~15–30 min |

**Surface types** (cover as many as the topic needs; for `ultra` require all that apply):

1. Primary product/docs / official  
2. GitHub (repos, stars, license, recency via `gh`)  
3. Community (Reddit, HN, forums)  
4. Practitioner chatter (X/Twitter if relevant)  
5. Academic (arXiv, papers)  
6. Critical / contrarian (problems, failures, abandonment)

**Freshness:** prefer last 12–24 months; for “last day or two” news, bias fresh queries and note crawl lag.

---

## Report steering (Parallel `--text-description` analog)

Infer or accept a short **steer** string, e.g.:

- `Structured report under ~4000 words; sections: Exec Summary, Landscape, Community, Architecture, Risks, Build Path, Sources. Concrete names + do/don't.`

Write the steer into `run_manifest` and obey it. If user gave no steer, use the default report skeleton in Step 5.

---

## Step 0 — Kickoff (do this before long work)

1. **Filename** (hyphenated, lowercase): e.g. `local-activity-intelligence-stack-2026`  
   Output dir: `~/Documents/research/` (create if missing).  
   Final paths: `~/Documents/research/$FILENAME.md` and `~/Documents/research/$FILENAME.json`

1b. **Prior coverage + resume check:** scan `~/Documents/research/INDEX.md` and any `*-state.json` files for this topic before researching; surface prior reports instead of silently re-running covered topics. Write the report `.md` incrementally (stub + skeleton now, append per section) and checkpoint `next_actions` into a `$FILENAME-state.json` after each tier, so a killed session resumes instead of restarting. On completion, append one line to `~/Documents/research/INDEX.md`: `$FILENAME.md | topic | date`.

2. **interaction_id:** generate once, e.g. `free-{YYYYMMDD}-{short-hash-or-uuid-fragment}`  
   If user is following up and prior JSON has `interaction_id`, set `previous_interaction_id` and load prior `.md`/`.json` for context (do not restate entire prior report).

3. **Tier + steer + sub-questions** (3–7 for pro; more for ultra).

4. **Immediately tell the user** (Parallel “monitor URL” analog):
   - Deep research kicked off (free engine)
   - Depth tier + expected wall-time range
   - Filename / output paths
   - `interaction_id`
   - Sub-question list (one line each)
   - They can keep chatting; you’ll return with executive summary when done

Do **not** dump raw search dumps into the chat.

---

## Step 1 — Decompose

Break the topic into focused sub-questions covering:

- Current state / recent developments  
- Key players / projects / concepts  
- Comparisons / trade-offs  
- Challenges / risks / criticisms (mandatory for `pro`+)  
- Future outlook / recommended path  

For software/SOTA topics add: stars/license/maintenance, community trust, install cost, what *not* to build.

---

## Step 2 — Parallel retrieve

Fire **parallel** tool calls (multiple `web_search` / `x_semantic_search` / `gh` in one turn).

Tool mapping for this environment:

| Intent | Tool |
|--------|------|
| Web / docs / Reddit / arXiv SERP | `web_search` |
| Full page primary source | `web_fetch` or `open_page` |
| GitHub stars/license/push | `run_terminal_command` + `gh api` / `gh search` |
| X/Twitter discourse | `x_semantic_search` / `x_keyword_search` |
| Local files if topic is machine-specific | disk tools / read paths user already has |

**Budget by tier** (from table above). Prefer primary sources over SEO blog spam.

**Vendor bias rule:** if one vendor dominates SERPs (e.g. product blog ranking for “best alternative”), deliberately query Reddit/HN/criticism + FOSS competitors.

Collect into a working list: `{url, title, surface, key_claims[], quote_or_snippet?}`.

---

## Step 3 — Triangulate + primary extract

For the highest-value URLs (tier table counts):

1. Fetch full content of primaries (GitHub README, paper HTML, official docs).  
2. Prefer **≥2 independent surfaces** before treating a claim as solid.  
3. Mark each major claim: **Confirmed** (2+ independent) / **Single-source** / **Vendor-only** / **Disputed**.  
4. Note conflicts explicitly (e.g. vendor “5% CPU” vs HN “thermal throttle”).

If a sub-question returns nothing usable: record **GAP** — do not invent.

---

## Step 4 — Optional critique pass (`pro`+ / `ultra`)

Before writing the final report, self-check:

- [ ] Did vendor marketing over-influence the recommendation?  
- [ ] Are licenses/stars/dates concrete?  
- [ ] Is community criticism represented?  
- [ ] Are recommendations actionable (do / don’t / phase)?  
- [ ] Would a skeptical engineer trust the citations?

If critique fails → one more **delta retrieve** (2–4 targeted queries), then proceed.

---

## Step 5 — Package dual artifacts (Parallel `.md` + `.json`)

### 5a. Markdown report — `$FILENAME.md`

Default skeleton (override with steer):

1. **Executive Summary** (2–3 paragraphs; also used as chat summary)  
2. **Key Findings** (themed; inline citations)  
3. **Detailed Analysis**  
4. **Comparisons / Trade-offs**  
5. **Risks & Challenges**  
6. **Recommendations / Build path** (phased when relevant)  
7. **Gaps & Open Questions**  
8. **Sources** (grouped: GitHub, Community, Academic, Vendor, Other)  
9. **Methodology notes** (tier, surfaces covered, tools, date, limitations)

Header:

```markdown
# [Topic] — Deep Research Report
Generated: [ISO date]
Engine: deep-research-free
Tier: [lite|base|core|pro|ultra]
interaction_id: [id]
```

Citation format: `[Source Name](URL)` inline after claims. Concrete numbers, dates, star counts. Label speculation vs confirmed.

### 5b. Basis JSON — `$FILENAME.json` (Parallel metadata analog)

**Copy from template** (fill every field; drop empty optional arrays only if truly unused):

- Template: `templates/run_manifest.json` (next to this SKILL.md)
- Report skeleton: `templates/report.md`

Required fields match the template: `interaction_id`, `engine`, `tier`, `topic`, `steer`, `filename`, `generated_at`, `sub_questions`, `surfaces_covered`, `sources[]`, `claims[]`, `conflicts[]`, `recommendations`, `gaps`, `follow_up_hooks`, `methodology`.

Claim `support` enum: `confirmed` | `single-source` | `vendor-only` | `disputed` | `gap`.  
Source `surface` enum: `github` | `reddit` | `arxiv` | `vendor` | `hn` | `x` | `docs` | `other`.  
Source `role` enum: `primary` | `secondary` | `critical`.

This is the **basis** file: enough to chain follow-ups without re-reading the whole web.

Save both files with the write tool:

```
~/Documents/research/$FILENAME.md
~/Documents/research/$FILENAME.json
```

Create `~/Documents/research/` if missing.

---

## Step 6 — Present to user (Parallel response format)

**Share in chat (only):**

1. **Executive summary** (from the report — do not paste the full `.md`)  
2. **File paths** for `.md` and `.json`  
3. **`interaction_id`** + note that follow-ups can chain (“drill deeper into X”)  
4. Offer to open/read a section if they want  

**Do NOT:**
- Re-dump all sources into chat  
- Read the full report back into context unless the user asks  
- Claim Parallel ran when free ran  

---

## Step 7 — Multi-turn follow-ups (Parallel interaction chaining)

When user asks a follow-up on the same research:

1. Load prior `~/Documents/research/$FILENAME.json` (and skim `.md` headers/sections as needed).  
2. Use **lite** or **base** tier unless they ask for another full deep pass.  
3. Only retrieve for **new** sub-questions.  
4. Append a `## Follow-up — [date]` section to the `.md` **or** write `$FILENAME-followup-N.md`.  
5. Update JSON: new `interaction_id`, set `previous_interaction_id` to prior id, merge new sources/claims.  
6. Return a short delta summary + paths.

---

## Output quality rules

- Every major claim needs a citation  
- Prefer primary sources; flag vendor-only claims  
- Note conflicts; do not smooth them away  
- Concrete stars, licenses, dates, versions when available  
- If thin: say **thin** / **GAP**  
- No fabricated URLs or papers  
- Methodology honesty: list surfaces *not* covered  

---

## Fallback ladder

```
User wants deep research
  → parallel-cli authed AND user wants Parallel? → parallel-deep-research
       ↳ on auth/balance/CLI failure → THIS skill (auto; see parallel skill)
  → else → deep-research-free (this skill)
  → user wants evidence.jsonl + HTML/PDF? → deep-research
```

**Invoked from Parallel fallback:** keep the same topic and map processor→tier (pro-fast→pro, ultra-fast→ultra). Note in methodology: `fallback_from: parallel-deep-research`, `fallback_reason: …`.

If mid-run free tools fail for a surface, record GAP and continue other surfaces — never block the whole report on one dead API.

## Templates

| File | Purpose |
|------|---------|
| `templates/run_manifest.json` | Basis JSON skeleton (copy → fill → write as `$FILENAME.json`) |
| `templates/report.md` | Markdown report skeleton (copy → fill → write as `$FILENAME.md`) |

Resolve paths relative to this skill directory.

## Scripts (must stay green)

| Script | Purpose |
|--------|---------|
| `scripts/smoke_test.sh` | Packaging + mirror + prior artifacts + parallel detect |
| `scripts/validate_research_output.py` | Schema-check dual `$STEM.md` + `$STEM.json` |
| `scripts/parallel_status.py` | Exit 0 READY / 2 FALLBACK for Parallel routing |

```bash
# After any skill edit:
bash ~/.claude/skills/deep-research-free/scripts/smoke_test.sh

# After writing a research pair:
python3 ~/.claude/skills/deep-research-free/scripts/validate_research_output.py \
  ~/Documents/research/$FILENAME

# Before choosing Parallel vs free:
python3 ~/.claude/skills/deep-research-free/scripts/parallel_status.py
# exit 2 → run this free skill immediately
```

**After editing this skill:** rsync to agents mirror:

```bash
rsync -a --delete ~/.claude/skills/deep-research-free/ ~/.agents/skills/deep-research-free/
```

---

## Red flags (stop and fix)

- Writing the report from model memory without searches  
- Single-vendor SERP capture without criticism pass  
- Full report pasted into chat  
- Missing `.json` basis file  
- Follow-up that re-runs ultra from scratch without loading prior interaction  
- Calling this “Parallel research” in the user-facing summary  

---

## Minimal example (kickoff message)

> Deep research started (**free** engine, tier **pro**, ~8–15 min).  
> Topic: local activity intelligence stack  
> `interaction_id`: free-20260725-a1b2  
> Outputs: `~/Documents/research/local-activity-intelligence-stack-2026.md` (+ `.json`)  
> Angles: GitHub capture tools · AW/HPI/Takeout · Reddit/HN trust · arXiv privacy/hierarchy · recommended compose path  

Then run Steps 1–6.
