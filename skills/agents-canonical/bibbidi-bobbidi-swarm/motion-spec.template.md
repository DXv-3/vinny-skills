# Motion Spec — <project> (<date>)

**Intensity:** subtle | full life | cinematic · **Engine policy:** respect installed (found: <libs>)

## Element inventory
| Element / surface | File | Now | Spec'd motion | Trigger | Law cited |
|---|---|---|---|---|---|
| ... | ... | static / animated-badly | what it should do | enter / hover / focus / scroll / load / state-change | # |

## Guarantees
- `prefers-reduced-motion`: every spec'd motion has a reduced variant or is disabled → rest state.
- Rest state must look good static (Law 5) — nothing depends on motion to be readable.
- Touch parity for all pointer-driven motion (Law 6).
- Perf budget: no per-frame layout reads; cached geometry only (Law 3); transforms/opacity only.

## Explicitly deferred
| Item | Why |
|---|---|

## Acceptance (checked in verify)
- [ ] Every inventory row either implemented or listed under Deferred with a reason
- [ ] Harness green, zero console errors
- [ ] Reduced-motion pass
- [ ] 60fps spot check on scroll/hover paths
- [ ] `visual-pass: advisory | gating` recorded (gating only after noise calibration)
- [ ] Kill-criteria watch clean (any hit → demote visual checks to advisory)
- [ ] User feel-check delivered (gates green alone does not close a run)
