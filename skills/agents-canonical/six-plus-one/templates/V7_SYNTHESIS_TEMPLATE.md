# V7 Synthesis Worksheet
**Fill this after V1–V6 exist. V7 is synthesis only — not a free 7th rewrite.**

| Field | Value |
|-------|--------|
| Date | |
| Job / TARGET TASK | |
| SOURCE location | |
| Variant files / paste IDs | V1…V6 |
| Operator | |
| Mode | ☐ Compiler (no invented gates) ☐ Product-split authorized by user |

---

## 0. Variant strength snapshot (optional but useful)

| Vi | Objective | Best at | Weak at | Contaminants? |
|----|-----------|---------|---------|---------------|
| V1 | Fidelity | | | |
| V2 | Structure | | | |
| V3 | Density | | | |
| V4 | Operational | | | |
| V5 | Literals | | | |
| V6 | Hybrid-draft | | | |

**Base skeleton pick (most ✓ after matrix):** V__  
**Why:**

---

## 1. SOURCE inventory (Pass A)
Add one row per **enforceable** atom. Unsure → keep.

| ID | Atom (short) | Type | Exact string required? | SOURCE quote / locus |
|----|--------------|------|------------------------|----------------------|
| R01 | | cmd / do-not / list / format / deliverable / scope / literal / id | Y / N | |
| R02 | | | | |
| R03 | | | | |
| R04 | | | | |
| R05 | | | | |
| R06 | | | | |
| R07 | | | | |
| R08 | | | | |
| R09 | | | | |
| R10 | | | | |
| R11 | | | | |
| R12 | | | | |
| R13 | | | | |
| R14 | | | | |
| R15 | | | | |

*Add rows as needed. Types: `cmd` `do-not` `list-item` `format` `deliverable` `scope` `literal` `identifier`*

---

## 2. Coverage matrix (Pass B)
Marks: **✓** full · **~** partial/risky paraphrase · **✗** missing

| ID | Atom | V1 | V2 | V3 | V4 | V5 | V6 | V7 must |
|----|------|----|----|----|----|----|----|---------|
| R01 | | | | | | | | ✓ |
| R02 | | | | | | | | ✓ |
| R03 | | | | | | | | ✓ |
| R04 | | | | | | | | ✓ |
| R05 | | | | | | | | ✓ |
| R06 | | | | | | | | ✓ |
| R07 | | | | | | | | ✓ |
| R08 | | | | | | | | ✓ |
| R09 | | | | | | | | ✓ |
| R10 | | | | | | | | ✓ |
| R11 | | | | | | | | ✓ |
| R12 | | | | | | | | ✓ |
| R13 | | | | | | | | ✓ |
| R14 | | | | | | | | ✓ |
| R15 | | | | | | | | ✓ |

**Full-coverage counts:** V1=__ V2=__ V3=__ V4=__ V5=__ V6=__

---

## 3. Conflict log (Pass C)
Default resolution = **SOURCE**. Never “sounds better.”

| # | Topic | Variants disagree | SOURCE says | Decision for V7 | Donor Vi |
|---|-------|-------------------|-------------|-----------------|----------|
| C1 | | | | | |
| C2 | | | | | |
| C3 | | | | | |

---

## 4. Contamination / invention hunt (Pass D)
Anything in V1–V6 **not** in SOURCE (new gates, refusals, APIs, deliverables, must/should drift).

| # | Found in | Contaminant | Action |
|---|----------|-------------|--------|
| X1 | V_ | | **EXCLUDE** from V7 |
| X2 | V_ | | **EXCLUDE** |
| X3 | V_ | | **EXCLUDE** (or ☐ formatting-only OK) |

---

## 5. Forbidden moves check (must all be NO before writing V7 body)

| Check | OK? |
|-------|-----|
| No 7th free generation from vibes | ☐ |
| No new requirements | ☐ |
| No new refusal text | ☐ |
| No new tech/APIs | ☐ |
| No must→should weakening | ☐ |
| No dropped list axes / teach items / deliverable | ☐ |
| No invented triggers/gates (unless product mode + user said so) | ☐ |
| No broken format contracts (fences, filename comments) | ☐ |

---

## 6. Provenance map (Pass E — write BEFORE V7 body)

| V7 section / block | Source of meaning | Source of wording/form |
|--------------------|-------------------|------------------------|
| Opener / hard commands | SOURCE | V__ / SOURCE |
| Do-not triad | SOURCE | V__ / SOURCE |
| Street / high-level | SOURCE | V__ |
| Silent analysis 1–5 | SOURCE | V__ |
| Framing / teach list | SOURCE | V__ |
| Output format | SOURCE | V__ |
| Code review axes 1–5 | SOURCE | V__ |
| Deliverable line | SOURCE | V__ / SOURCE |
| Headings / layout | n/a (format) | V__ |
| Other: | | |

**Graft plan (rows that were ~ or ✗ on base):**
- R__ ← take from V__ or SOURCE literal
- R__ ←
- R__ ←

---

## 7. V7 FINAL
Paste the standalone synthesized output below.

```markdown
[V7 body here]
```

---

## 8. Audit (after V7 body)

### DROPPED
| Item | Why allowed (must be non-functional prose only) |
|------|--------------------------------------------------|
| *(must be empty or justified)* | |

### WEAKENED
| Item | Was → Now | Fix |
|------|-----------|-----|
| *(must be empty)* | | |

### ADDED (requirements)
| Item | Fix |
|------|-----|
| *(must be empty)* | |

### ADDED (formatting only)
| Item | OK? |
|------|-----|
| headings / bullets | ☐ pure format |

### RESIDUAL SOURCE AMBIGUITY (preserved, not resolved)
> 

### Stop condition
- [ ] Every inventory row ✓ in V7  
- [ ] WEAKENED empty  
- [ ] ADDED(requirement) empty  
- [ ] V7 stands alone  
- [ ] No further polish for elegance  

**Status:** ☐ FAIL → patch V7 and re-audit · ☐ PASS → ship V7

---

## 9. Optional product split (only if user authorized)
If SOURCE was a mashup and user asked to split:

| Output | Path / name | Contents |
|--------|-------------|----------|
| Skill A | | |
| Skill B | | |

---

## Creed
> V7 may rearrange and densify; it may not renegotiate reality with SOURCE.  
> Coverage beats density. Always.
