# Step 7 Protocol — Synthesize V7 Without Fucking Anything Up

This is the operating manual for the **7th output only**.  
V1–V6 already exist. Step 7 is **not** “try again harder.”  
Step 7 is **audit → adjudicate → assemble → re-audit**.

---

## 0. Mental model (read first)

| Phase | Name | Allowed to invent content? | Goal |
|-------|------|----------------------------|------|
| 1–6 | Generate | No (vs SOURCE) | Explore *form* (fidelity, density, structure…) under fixed meaning |
| **7** | **Synthesize** | **No** | Maximize coverage + density + clarity using **only** SOURCE + V1–V6 |

**V7 is a collage with legal rules**, not a creative rewrite.

Think like a code merger:
- SOURCE = main branch (truth)
- V1–V6 = feature branches (presentation)
- V7 = merge commit with zero feature creep

---

## 1. What “truly looking at everything” means (mandatory passes)

Do **all five passes** before writing final V7 body. Skipping a pass is how requirements die.

### Pass A — SOURCE inventory (truth table)
From SOURCE only, list every **enforceable** atom:

- Commands / hard openers (“Stop. Before…”)
- Negations (“Do not…”)
- Must-teach / must-address lists (numbered axes, 7 teach items, etc.)
- Format contracts (fences, filename comments, deliverable shape)
- Scope boundaries (what task is / is not)
- Exact quotes that function as constraints (refusal text, REALLY-about question, deliverable paragraph)
- Identifiers (names, paths, protocols)—preserve casing

**Rule:** If it can cause a wrong agent behavior when missing → it is enforceable → it gets a row.

**Ignore as non-functional** (may drop only if no behavior depends on it):
- Throat-clearing, pure motivation, repeated synonyms of the same constraint already kept once

When unsure: **keep** (fail closed toward SOURCE).

### Pass B — Variant scan (V1…V6 each)
For each variant, mark every inventory row:

| Mark | Meaning |
|------|---------|
| ✓ | Fully present, not weakened |
| ~ | Partial / paraphrased risk / incomplete list |
| ✗ | Missing |

Also note **unique strengths** per Vi (e.g. V5 has exact Stop line; V3 shortest; V6 has REALLY-about).

### Pass C — Conflict detection
Wherever two variants disagree on:

- presence/absence of a requirement  
- strength (must vs should)  
- order that changes meaning  
- added triggers (“when code is provided”)  

Log a conflict. **Default resolution = SOURCE.**  
Never resolve by “sounds better.”

### Pass D — Contamination check (invention hunt)
Scan V1–V6 for content that is **not** in SOURCE:

- new modes, tools, APIs, safety policies  
- new gates/triggers  
- extra deliverables  
- softened language that replaces a hard command  

Tag as **CONTAMINANT**. Contaminants may **not** enter V7 unless they are pure formatting (heading names, bullet markers) with zero new semantics.

### Pass E — Assembly plan
Before writing V7 prose:

1. Pick **base skeleton** = variant with most ✓ rows (ties: prefer clearer structure, then density).
2. For every ~ or ✗ on the base: **graft** the missing atom from the best ✓ variant or from SOURCE literal.
3. Prefer **SOURCE exact string** for:
   - ritual commands  
   - refusal / stop language  
   - deliverable sentences  
   - named list labels that are part of the contract  
4. Prefer **dense paraphrase** only when Pass A row stays ✓ and no exact string was required.

Write the provenance map **before** the final body. If you can’t provenance a sentence, it doesn’t belong in V7.

---

## 2. Assembly rules (how to build V7 text)

### 2.1 Inclusion law
```
V7_atom is legal iff
  (atom ∈ SOURCE) OR (atom is non-semantic formatting)
```
Presentation may come from Vi. **Meaning** must be SOURCE-backed.

### 2.2 Strength law
Never downgrade:
- must → should  
- all → some  
- identify and fix → consider  

Never upgrade beyond SOURCE either (no new “always/never” not in SOURCE).

### 2.3 Completeness law
Every Pass A row must be ✓ in V7.  
Partial lists (4 of 5 security examples, 6 of 7 teach items) = **failure**. Re-graft.

### 2.4 Density law
After full coverage:
- merge duplicate statements of the same requirement (once is enough)
- delete pure non-functional prose
- keep command force of hard openers even if slightly longer

**Coverage beats density. Always.**

### 2.5 Structure law
Use headings/sections only to improve retrieval of existing requirements.  
Do not add sections that imply new capabilities.

### 2.6 Dual-task mashups
If SOURCE concatenates unrelated tasks (e.g. skill extraction + code review):

- **Compiler mode (default for this pipeline):** keep both; do not invent a gate  
- **Product mode (only if user explicitly asks):** split into two outputs—and label that as a **user-authorized scope change**, not a silent V7 invention

Step 7 alone does **not** get to “fix” the mashup without user say-so.

---

## 3. Forbidden moves (instant V7 fail)

1. **Seventh free generation** from vibes (“here’s a cleaner rewrite”) without matrix  
2. **Cherry-picking style** while dropping a hard list item  
3. **Smart triggers** not in SOURCE (“when code is provided”, “if user asks”)  
4. **Safety theater** or extra refusals not in SOURCE  
5. **Synonym swaps** on terms that are part of a contract (`skill.md`, filename comment shape, axis names)  
6. **Averaging** two paraphrases into a third that matches neither SOURCE nor any Vi  
7. **Resolving SOURCE ambiguity** creatively  
8. **Declaring victory** with non-empty DROPPED / WEAKENED / ADDED(requirement)

---

## 4. Required Step-7 output shape

Always emit in order:

1. **COVERAGE MATRIX** (SOURCE atoms × V1–V6 + V7 target ✓)  
2. **CONFLICT LOG** (decision per conflict)  
3. **FORBIDDEN MOVES CHECK** (all clear)  
4. **PROVENANCE MAP**  
5. **V7 FINAL** (standalone)  
6. **AUDIT** (DROPPED / WEAKENED / ADDED / RESIDUAL AMBIGUITY)

If AUDIT shows a problem → fix V7 and re-run AUDIT (still Step 7; does **not** consume a new variant slot).

---

## 5. How Step 7 “looks at everything” without thrashing

### Time budget (practical)
- 40% inventory + matrix  
- 20% conflicts + contaminants  
- 25% assemble V7  
- 15% audit + surgical fix  

Do **not** spend the budget rewriting V7 three times from scratch.  
Patch like a merge: base + grafts.

### Dual attention (street + high)
Same as skill extraction, applied to variants:

| Level | On Step 7 |
|-------|-----------|
| Street | Every list item, deliverable, exact quote, format marker across all 6 |
| High | Which variant best carries the *real* job (compiler fidelity vs density vs structure)—without changing the job |

### Stop condition
Stop when:
- every Pass A row is ✓ in V7  
- AUDIT ADDED(requirement)=empty, WEAKENED=empty  
- DROPPED only contains proven non-functional prose (or empty)  
- V7 stands alone  

Do **not** keep polishing for elegance after stop condition.

---

## 6. Failure modes we already saw (and the fix)

| Failure from the 6 DeepSeek runs | Step-7 response |
|----------------------------------|-----------------|
| v3 drops command force of “Stop…” | Graft SOURCE/v5 opener verbatim |
| v4 invents “when code is provided” | Tag CONTAMINANT; exclude unless user product-mode |
| v4 broken fence | Don’t copy broken format; use v6/v2 format contract |
| v1 too prose-heavy | Use as coverage donor, not as base skeleton |
| v6 misses exact Stop ritual | Base structure v6, graft v5 opener |
| All keep mashup of two tasks | Keep mashup in compiler mode; split only if user asks |

---

## 7. One-line creed

> **V7 may rearrange and densify; it may not renegotiate reality with SOURCE.**

Look at everything = full inventory + full matrix + full audit.  
Don’t fuck it up = no invention, no silent omission, no strength drift, stop at coverage.
