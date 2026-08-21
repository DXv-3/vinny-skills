# ContextOS Monorepo — Agent Law

## Architecture (non-negotiable)
ContextOS Core (pure deterministic spine)
  INSPECT → CURATE → COMPILE → EXECUTE → VERIFY → PROMOTE → compile_session
  + four hard-rule invariants
        ↓
Ground Truth Ingestion Layer
  STAGE 1/1b/2/3/4 → ground-truth-graph.json v2
  + manual_overrides + PII + snapshots
        ↓
GitReverse Surface
  Codebase/Website → grounded build prompt

## Four Hard Rules (runtime invariants)
1. No source truth → no trustworthy context
2. No context boundary → no bounded execution
3. No verification → no completion claim
4. No project-state update → no durable progress

## Coding Doctrine (Karpathy)
- Think before coding — surface assumptions
- Simplicity First — minimum code that solves the current goal
- Surgical Changes — touch only what the current task requires
- Goal-Driven Execution — every step ends with a verifiable success criterion

## Pure-function rules
- Every stage returns only structured JSON / dataclasses
- Zero disk writes after INSPECT
- Zero subprocess / git / repository mutation
- propose_patch always returns state="draft", applied=False
- Deterministic token basis = whitespace-split only

Never flatten the three layers. Never skip the hard rules.
Always update STATUS.md at the end of every step.
