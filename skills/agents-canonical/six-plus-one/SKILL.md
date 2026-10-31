---
name: six-plus-one
description: >
  Run a 6-variant then 1-synthesis pipeline: generate at most 6 diverse candidates
  (fidelity, structure, density, operational, literals, hybrid-draft), then produce
  a V7 best-of-all merge using coverage matrix, conflict log, contamination check,
  provenance, and audit — no invented requirements, no silent drops. Also exports
  DeepSeek paste packs, V7 worksheet template, pure conversation-to-skill and
  code-review skills, and ultra-dense system-prompt compiler. Use when the user
  says "six plus one", "6+1", "V7 synthesis", "best of all variants", "variant then
  synthesize", "DeepSeek 6 outputs", "coverage matrix", "don't invent requirements",
  or runs /six-plus-one.
---

# Six-Plus-One (6 variants → V7 synthesis)

You run a **hard-capped** generation loop and a **strict** merge step.

## Creed
> V7 may rearrange and densify; it may not renegotiate reality with SOURCE.  
> Coverage beats density. Always.  
> Max **6** generative variants. V7 is **synthesis only** (not a free 7th roll).

## When invoked

Parse user intent into one mode:

| Mode | Trigger | Action |
|------|---------|--------|
| `run` | has SOURCE, wants V1–V6 + V7 | Full pipeline |
| `v7-only` | already has V1–V6 | Synthesis only |
| `deepseek-pack` | wants paste for DeepSeek | Emit copy-paste messages |
| `template` | wants empty worksheet | Write/fill `V7_SYNTHESIS_TEMPLATE.md` |
| `split-skills` | mashup → pure skills | Emit conversation-to-skill + code-review |
| `compile` | densify a system prompt | TARGET TASK = ultra-dense compiler |

If SOURCE is missing and mode needs it, ask once for SOURCE (or path). Do not invent SOURCE.

## References (read as needed)

| Path | Use |
|------|-----|
| `references/STEP7_PROTOCOL.md` | Full Step-7 law |
| `references/DEEPSEEK_6_PLUS_1_SYNTHESIS_PIPELINE.md` | DeepSeek system + steps |
| `templates/V7_SYNTHESIS_TEMPLATE.md` | Empty matrix worksheet |
| `references/conversation-to-skill.md` | Pure skill A |
| `references/code-review.md` | Pure skill B |
| `references/ULTRA_DENSE_compiler_onescreen.md` | Compiler one-screen |

User copies also live under `~/Downloads/versions_from_deepseek/` (same content).

---

## Variant objectives (fixed labels — do not remix)

| Vi | Objective |
|----|-----------|
| **V1** | **Fidelity** — max surface faithfulness + command force; density secondary |
| **V2** | **Structure** — best headings/sections for LLM retrieval; full coverage |
| **V3** | **Density** — min tokens; **no** requirement loss (if tradeoff, keep requirement) |
| **V4** | **Operational** — clearest execution order; **do NOT invent gates/triggers** absent from SOURCE |
| **V5** | **Literals** — preserve every hard-constraint phrase, list item, deliverable line |
| **V6** | **Hybrid-draft** — best single-pass balance of V1–V5 (**not** final) |

---

## Mode: `run` (full pipeline)

### Step 0 — Lock job
Confirm:
- SOURCE (quoted or path)
- TARGET TASK (default: system-prompt densify / or user task)
- Mode: **compiler** (default) vs **product-split** (only if user authorizes)

Success criteria rank:
1. Semantic equivalence on enforceable requirements  
2. Zero invented requirements  
3. Zero dropped requirements  
4. Max density subject to 1–3  
5. Structure for retrieval when free  

### Steps 1–6 — Generate V1…V6
- Produce **exactly six** complete standalone candidates.
- Each optimizes its objective **without** violating: no omit / weaken / add vs SOURCE.
- Preserve quoted literals and exact refusal-like commands when present.
- Separate with `===== V1 =====` … `===== V6 =====` (or write six files if user wants files).
- **Stop generating after V6.** No V8 ever.

Prefer writing artifacts to a working dir the user names, else:
`~/Downloads/versions_from_deepseek/runs/<timestamp>/V1.md` … `V6.md`

### Step 7 — Synthesize V7
**Mandatory order** (do not skip sections):

1. **SOURCE inventory** — every enforceable atom (cmd, do-not, list, format, deliverable, scope, literal, id)
2. **Coverage matrix** — each atom × V1–V6 as ✓ / ~ / ✗; V7 plan must be ✓ for all
3. **Conflict log** — default resolve = SOURCE
4. **Contamination hunt** — exclude inventions (new gates, APIs, refusals, must/should drift)
5. **Forbidden moves check**
6. **Provenance map** — *before* final body
7. **V7 FINAL** — standalone; base = most ✓ rows; graft gaps from other Vi or SOURCE; prefer SOURCE wording for hard constraints; densify only if row stays ✓
8. **Audit** — DROPPED / WEAKENED / ADDED(requirement) must be empty (or DROPPED only non-functional prose)

If audit fails: **patch V7 and re-audit** (still Step 7). Do not open a new variant slot.

Also fill `templates/V7_SYNTHESIS_TEMPLATE.md` (copy into the run folder as `V7_worksheet.md`) so the matrix is durable.

### Laws (non-negotiable)
- **Inclusion:** meaning SOURCE-backed; Vi supplies form only  
- **Strength:** no must→should; no silent upgrades  
- **Completeness:** partial lists = fail  
- **Density after coverage**  
- **No 7th free gen** from vibes without matrix  

---

## Mode: `v7-only`

User provides SOURCE + V1–V6 (paste or paths).  
Skip generation. Execute Step 7 only.  
Use the worksheet template. Emit V7 + full audit.

---

## Mode: `deepseek-pack`

Output three copy-paste blocks for DeepSeek:
1. SYSTEM (from pipeline reference)
2. SETUP + VARIANTS V1–V6 user message
3. SYNTHESIZE → V7 user message  

Point user at `PASTE_INTO_DEEPSEEK.md` if present under Downloads. Keep cap language explicit: 6 redos max; V7 = merge.

---

## Mode: `template`

1. Copy `templates/V7_SYNTHESIS_TEMPLATE.md` to user-chosen path (default: current dir or Downloads run folder).
2. Pre-fill date + TARGET TASK if known.
3. Tell user: fill inventory → matrix → then ask `/six-plus-one` with `v7-only`.

---

## Mode: `split-skills`

When SOURCE (or conversation) mixes unrelated capabilities:

1. Extract pure **conversation-to-skill** and pure **code-review** (see references).
2. Do **not** silently invent cross-triggers unless user asks product mode.
3. Write two files with `<!-- filename: … -->` headers.

---

## Mode: `compile`

TARGET TASK = ultra-dense system-prompt compiler (`references/ULTRA_DENSE_compiler_onescreen.md`).  
Then `run` or emit DeepSeek pack with that TARGET TASK.

---

## Output contract (when producing V7 for the user)

Always show:
1. Brief base + graft summary (3–8 lines)
2. Coverage matrix (or path to worksheet)
3. V7 FINAL in one fenced block
4. AUDIT (must claim empty WEAKENED / ADDED requirements)

Never claim PASS if any enforceable row is ~ or ✗ in V7.

---

## Anti-patterns
- Averaging two paraphrases into a third that matches neither SOURCE nor any Vi  
- “When code is provided” style gates not in SOURCE (compiler mode)  
- Picking V3 density and losing Stop/ritual command force  
- Shipping broken fences / incomplete filename contracts  
- Opening V7 without inventory  

## Slash
`/six-plus-one`  
`/six-plus-one v7-only`  
`/six-plus-one deepseek-pack`  
`/six-plus-one template`  
`/six-plus-one split-skills`  
`/six-plus-one compile`
