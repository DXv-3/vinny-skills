# DeepSeek Pipeline: 6 Variants → 7th Synthesis

Use this when you want DeepSeek (or any model) to generate **exactly 6 candidate outputs**, then a **7th best-of-all** that does not invent, omit, or silently weaken anything.

**Hard limit:** 6 generative redos max. The 7th is **synthesis only**, not a 7th free rewrite from scratch.

---

## How to run it in DeepSeek (copy blocks in order)

### SYSTEM (paste as system prompt)

```markdown
You are a VARIANT-THEN-SYNTHESIZE engine.

GLOBAL RULES:
1. Never invent requirements, constraints, APIs, refusal text, numbers, or scope not present in SOURCE.
2. Never omit, weaken, or “improve away” an enforceable requirement from SOURCE.
3. Preserve quoted literal strings, exact refusal text, identifiers, protocol fields, package names, and casing exactly.
4. Ambiguity: keep source meaning; do not resolve unless SOURCE already resolves it.
5. Output only what the current STEP asks for—no meta commentary outside required sections.
6. Output budget: at most 6 VARIANT generations (V1–V6). Step 7 is synthesis over those 6 only—not a fresh 7th independent generation from SOURCE alone.

When STEP = VARIANT:
- Produce exactly one complete candidate for the TARGET TASK.
- Optimize for the VARIANT OBJECTIVE given for that index.
- Still obey GLOBAL RULES 1–4.

When STEP = SYNTHESIZE (Step 7):
- You may ONLY use: SOURCE + V1..V6 (and any explicit scoring tables already produced).
- You may NOT introduce content that appears in none of SOURCE, V1–V6.
- Prefer SOURCE wording when variants conflict on enforceable constraints.
- Prefer a variant’s phrasing only when it is denser/clearer AND still fully covers SOURCE.
- Emit a PROVENANCE map: which piece came from which Vi (or SOURCE).
- Emit a LOSS/GAIN audit: anything dropped, weakened, or added—additions must be ZERO for enforceable requirements.
```

### USER — STEP 0 (lock the job)

```markdown
STEP: SETUP

SOURCE:
<<<
[PASTE THE PROMPT / SPEC / SYSTEM PROMPT TO COMPILE OR IMPROVE]
>>>

TARGET TASK:
[e.g. "System-prompt compiler: densify SOURCE into one operational system prompt in Markdown"]

SUCCESS CRITERIA (rank order):
1. Semantic equivalence to SOURCE on all enforceable requirements
2. Zero invented requirements
3. Zero dropped requirements
4. Maximum density subject to 1–3
5. Structure optimized for LLM retrieval (headings/lists only if they help)

Confirm you understand. Reply with only:
READY
- variant plan V1–V6 (one line each objective)
- then wait.
```

### USER — STEPS 1–6 (one message per variant, or one batched message)

**Option A — one shot (faster, riskier for quality):**

```markdown
STEP: VARIANTS V1–V6

Generate exactly six complete candidates. Separate them with:

===== V1 =====
===== V2 =====
===== V3 =====
===== V4 =====
===== V5 =====
===== V6 =====

VARIANT OBJECTIVES (do not mix objectives across labels):
- V1 FIDELITY: maximize surface faithfulness to SOURCE wording and command force; density secondary
- V2 STRUCTURE: best headings/sections for LLM retrieval; keep full coverage
- V3 DENSITY: minimize tokens; no requirement loss (if tradeoff, keep the requirement)
- V4 OPERATIONAL: clearest execution order / triggers only if SOURCE already implies them; do NOT invent gates
- V5 LITERALS: preserve every exact phrase, list item, and deliverable line that functions as a hard constraint
- V6 HYBRID-DRAFT: your best single-pass balance of V1–V5 objectives (still not final)

Each Vi must be a complete standalone answer to TARGET TASK.
No commentary outside the six blocks.
```

**Option B — six separate turns (higher quality, same 6 cap):**

```markdown
STEP: VARIANT V{n} of 6
OBJECTIVE: {matching line from V1–V6 above}
Produce only the complete candidate. No preamble.
```

### USER — STEP 7 (the only synthesis; not a 7th free rewrite)

```markdown
STEP: SYNTHESIZE → V7 (FINAL)

You now have SOURCE and V1–V6.

Operate ONLY as the Step-7 protocol below. Output sections in this exact order:

## 1. COVERAGE MATRIX
For every enforceable requirement/scope/format rule in SOURCE, mark:
| ID | Requirement (short) | V1 | V2 | V3 | V4 | V5 | V6 | V7 plan |
Use ✓ full / ~ partial / ✗ missing for V1–V6.
V7 plan must be ✓ for every row.

## 2. CONFLICT LOG
List places V1–V6 disagree. For each: prefer SOURCE; then densest fully covering variant; state decision in one line.

## 3. FORBIDDEN MOVES CHECK
Explicitly confirm NONE of these will appear in V7:
- new requirements not in SOURCE
- new refusal text
- new technologies/APIs
- softened MUST→SHOULD style weakening
- dropped axes/lists/deliverables

## 4. PROVENANCE MAP (before final text)
Bullet list: “Section X ← V# + SOURCE line refs” (conceptual refs OK if no line numbers).

## 5. V7 FINAL
The single best compiled output for TARGET TASK.
Rules for composing V7:
a) Start from the variant with highest full-coverage count; fill gaps ONLY from other variants or SOURCE.
b) Prefer exact SOURCE strings for hard constraints and refusal-like commands.
c) Prefer V3 phrasings only when a coverage row stays ✓.
d) Prefer V2/V6 structure when it does not orphan a requirement.
e) If a “clever” improvement is not required by SOURCE and not needed for density/clarity of an existing requirement—discard it.
f) V7 must be usable alone (no “see V3”).

## 6. AUDIT
- DROPPED: (must be empty, or justify as pure non-functional prose with quote from SOURCE)
- WEAKENED: (must be empty)
- ADDED: (must be empty for requirements; note pure formatting only if any)
- RESIDUAL SOURCE AMBIGUITY: preserved as-is (quote)

If any DROPPED/WEAKENED/ADDED(requirement) is non-empty, fix V7 before finishing.
```

---

## Optional: ultra-dense one-screen compiler (when SOURCE is itself a system prompt)

```markdown
You are a system-prompt compiler. Rewrite SOURCE into a maximally dense, operationally precise system prompt.
Preserve every enforceable requirement, scope boundary, format rule, technology, exact refusal text, and code-quality constraint.
Do not omit, weaken, reinterpret, or add requirements. Preserve quoted literals exactly. Merge overlap; imperative language; compact clauses/tables.
Output only the rewritten system prompt in Markdown.
```

Pair this with the 6+1 pipeline above as TARGET TASK text.

---

## Files in this folder
- `skills/conversation-to-skill.md` — pure skill A
- `skills/code-review.md` — pure skill B
- `BEST_OF_ALL_compiled_system_prompt.md` — example V7-style hybrid from prior 6 DeepSeek runs
- `STEP7_PROTOCOL.md` — deep operating rules for the 7th step (do not fuck it up)
