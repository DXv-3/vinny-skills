---
name: parts-hunt
description: "Run a strip-for-parts GitHub hunt: scout lanes in parallel, strip mechanisms and patterns (never adopt wholesale), verify licenses, file parts to the shelf, and compile a ranked steal list with build order."
metadata: { "includeInPrompt": true }
---

# Parts Hunt

## Purpose
Turn "make X more real" into a ranked steal list. GitHub is the quarry, the parts shelf is the workshop: scouts mine repos per lane, strip the load-bearing mechanisms and patterns, verify them, file them to the shelf, and rank them by impact-per-effort with a build order. Nothing is ever adopted wholesale.

## Workflow
1. **Target + lanes.** Name the target (the thing becoming "more real"). Pick lanes from `lanes.yaml` (v1 lanes = re-scout for deltas only; v2 = fresh). Add a lane if the target needs one.
2. **Scout.** Spawn one subagent per lane in parallel with `references/scout-brief.md`. Each returns candidates, not adoptions.
3. **Verify.** For each candidate: license check (AGPL / research / non-commercial = ideas only, never deploy the code — flag it), activity check (alive vs stale), and the "better than what he has" check. A trending repo is a lead, not a verified part.
4. **Shelf.** `shelf.py search` first (the shelf may already hold it). Then file verified parts:
   `python3 ~/workspace/parts-shelf/shelf.py add --title "<name>" --kind <mechanism|pattern|option|lesson|fact|path> --body "<the part + how to graft it; always include repo, license, stars, activity, date mined>" --tags "<lane>,<target>" --source "<repo URL>"`
5. **Rank.** Impact-per-effort. Write the steal list with `references/steal-list-template.md`: ranked steals, honorable mentions, skip pile (with reasons), build order.
6. **Radar (optional).** For ongoing targets, wire the weekly radar: cron watching trending + awesome-list commit feeds → candidates → shelf → digest. One-off hunts skip this.

## Output Contract
The steal list doc carries, per ranked steal: **Source** (repo / license / stars / activity), **The part** (2–4 sentences — the mechanism, not the product), **Plugs into** (his existing system), **Why it makes [target] more real** (one line), **Effort** (small / small-medium / medium / big). Then honorable mentions (small, take soon), the skip pile (impressive, wrong fit — with the reason), and a suggested build order (quick wins first). It closes with the constraint line: nothing requires a paid API, a cloud account, or his data leaving his machines.

## Operating Rules
1. Strip for parts, never adopt wholesale. The product is never the recommendation.
2. License flags are load-bearing: AGPL / research / non-commercial → strip the ideas, never ship the code. Say so in the entry.
3. `shelf.py search` BEFORE building anything; `shelf.py add` after finishing or learning something hard.
4. Capture as-we-use-it. Never bulk-scrape.
5. Free, local, private: free models, his Mac, Tailnet-only. If a part needs paid/cloud, it goes in the skip pile with the reason.
6. Verify before ranking. Unverified = honorable mention at best.
