---
name: harvest-discipline
description: "Harvest discipline"
---

# Harvest discipline

Nine laws. Each exists because a real build broke without it (receipts in the post-mortem).

1. **Retest the blocker before it shapes the plan.** A lane that failed once is a hypothesis.
   Re-probe it in isolation before choosing architecture around it. A "platform blocks X"
   theory may actually be self-inflicted (M1: "datacenter IP class block" overturned in one
   1-second probe; M2: 429 came from requesting 7 subtitle variants when 3 worked).
2. **Count your own requests first.** When something rate-limits, multiply what YOU send
   per item (languages, formats, retries, redirects) before blaming the far side.
3. **Every batch prints a terminal line** — `DONE ok=X empty=Y skipped=Z` — and a coverage
   count after. No DONE line in the log = the job did not finish. Ever treat it as done.
4. **Majority-fail stops the queue.** If >30% of items fail with the same error class,
   halt and diagnose. A queue that's 64% empty is a bug report, not a workload.
5. **Artifacts land on owned soil immediately.** Local disk / git at production time —
   never only inside the sandbox/platform that's misbehaving. `ls` a path before running
   code that depends on it (M4: three `Errno 2` in a row on a bundle that never existed).
6. **Validate ids before they enter the queue.** Type-check per source (e.g. YouTube video
   ids = 11 chars `[A-Za-z0-9_-]`; `PL…` = playlist). One poisoned tab wasted 2/5 of a
   pilot and inflated a count by 88 (M5).
7. **Hunt zombie resources on provisioning errors.** "Limit reached" with nothing visible
   running = an invisible holder. Reap it platform-side; don't wait or build around it (M6).
8. **Two identical failed passes = escalate strategy.** No third pass of the same lane.
   Check the local research folder for an already-known fix first (M8: 4.5h of cooldown
   loops while the fix doc sat in ~/Documents/research/).
9. **Coverage leads with the denominator.** "19 of 1,194 transcripts" — never "57,430
   words" as a headline. Aggregate stats are how hollow builds cosplay as done (M7).
   Status words in reports/memory: BUILT / PARTIAL / BLOCKED / UNVERIFIED. Speed claims
   are projections until a DONE line exists (M9).

## Steal-worthy pattern (what the broken build got right)

Tiered lanes (cheap API → heavy fallback), atomic per-item writes + done-set resume,
one probe cell that measures every lane before committing, the work queue as an
inspectable file.
