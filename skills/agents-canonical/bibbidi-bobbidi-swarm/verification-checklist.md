# Verification Checklist (all must pass)

1. `npm test` (or project equivalent) green.
2. Production build succeeds.
3. Project's verify/screenshot harness green (if present); screenshots captured before/after.
4. Zero console errors in harness output.
5. `prefers-reduced-motion: reduce` → page renders in rest state, no blocking motion, content fully readable.
6. Rest state (no JS / first paint) looks complete on its own (Law 5).
7. Motion paths use transform/opacity only; no per-frame layout reads (Law 3).
8. Pointer-driven effects have touch listeners (Law 6).
9. Every Motion Spec inventory row: implemented, or in Deferred with reason.
10. Git diff confined to files owned in choreography.md; no new animation dependencies.
11. Visual-pass mode recorded (advisory default); kill-criteria watch clean; user feel-check pending before run closure.

**Bounce-back rule:** one fix round max. If a gate still fails after bounce-back, revert the failing file's changes and record the item as deferred.
