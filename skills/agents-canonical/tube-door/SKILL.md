---
name: tube-door
description: Fire when Vinny says "harvest/scrape transcripts from <url or @channel>", "rebuild the KB", "backfill" (legacy VTT / Itssssss_Jack corpora into the KB), "watch <channel>" (incremental new-video queue), or asks what a channel talked about — query the KB before fetching. Multi-channel YouTube transcript pipeline on this Mac captions first (ONE subtitle variant per video), local ASR for caption-less videos, one searchable FTS5 kb.db, ask.py on top. Private/local — no paid APIs, no API keys, no cron/launchd. Files outside ~/Projects/tube-door are read-only (copy, never touch). Master doc — ~/Projects/TUBE-MASTER-2026-09-29.md.
---

# tube-door — harvest YouTube transcripts into the local KB

Everything runs from `~/Projects/tube-door` with its venv: `PY=.venv/bin/python3`.
Master doc: `~/Projects/TUBE-MASTER-2026-09-29.md` (read before changing anything).
Interfaces/schema: `CONTRACT.md` in the repo. The KB lives at
`~/Projects/tube-door/kb/kb.db` (SQLite FTS5, all channels, one db) with
greppable markdown at `kb/talks/<channel>/<id>.md`.

## Harvest a channel (the 4-step flow)

```bash
cd ~/Projects/tube-door && PY=.venv/bin/python3
$PY src/enumerate.py "https://www.youtube.com/@<handle>"   # 1. validated queue -> raw/queue/<channel>.tsv (ids 11-char or skipped; --cap N to cap)
$PY src/harvest.py  "https://www.youtube.com/@<handle>"    # 2. caption ladder, ONE variant/video, resumable
$PY src/build_kb.py                                        # 3. full idempotent rebuild: kb/kb.db + kb/talks/ + INDEX + missing_transcripts.txt
$PY src/ask.py 'query text' -n 5                           # 4. ask it (add --channel @handle, --lane <lane>)
```

Single-variant rule (the whole stealth stack): manual `--write-sub` preferred,
auto `--write-auto-sub` only as fallback, `--sub-lang en` — the string `en.*`
is FORBIDDEN (it once fetched 7 variants and self-inflicted 429s). Jitter
2–8 s between videos is automatic. Retest a blocker live with
`$PY src/harvest.py --ids <id> --limit 3` — verification fetches cap at 3 videos.

## Provenance lanes (ledger `lane`, closed vocab)

`captions-manual` | `captions-auto` | `asr-parakeet` | `asr-whisper` |
`asr-cloud` | `none` — plus backfill-only tags `legacy-vtt` | `legacy-jack`.
Cookies/impersonation are separate ledger columns, never lane names.
`raw/ledger.jsonl` is the resume + provenance record (append-only).

## Captions 429 — escalation order

1. **Cookies** — export `cookies.txt` to the project root (gitignored); the T1b
   rung auto-activates. If absent the log says `T1b rung disabled`.
2. **curl_cffi impersonation** — `--impersonate chrome` is already baked into
   every fetch (`src/harvest.py`); on repeat blocks escalate the client.
3. **bgutil POT provider** — ESCALATION ONLY, **NOT installed**, deliberately.
   Design doc: `~/Documents/research/github-tube-door-upgrades-2026-09-28.md`.
   Reached only after two identical failed passes (harvest-discipline law 8):
   check `~/Documents/research/` first, then escalate to Vinny.
   T3 audio→ASR is the guaranteed lane regardless of the caption wall.

## ASR lane (videos with no captions)

`$PY src/asr.py --from-ledger --limit 50` drains ledger rows with `lane=none`
(single ids: `--id <id> --channel '@handle'`; `--purge-audio` clears transient
opus). Engine order: parakeet-mlx → mlx-whisper → whisper.cpp (Metal, model at
`~/models/whisper/ggml-small.en.bin`) → cloud. The cloud engine is a **stub**:
it prints the exact house `speech_transcribe` MCP call and exits — it never
fakes a transcript or writes a file.

## Backfill (sources READ-ONLY — copy, never touch originals)

```bash
$PY src/backfill.py legacy-vtt    # ~/transcripts/*.en.vtt (10 files) -> tag legacy-vtt
$PY src/backfill.py legacy-jack   # ~/youtube-ingest/Itssssss_Jack (147) -> tag legacy-jack
$PY src/build_kb.py               # then rebuild
```

Deferred (documented, not coded — the manual item): drain
`~/Projects/ai-engineer-kb/reports/missing_subs.txt` ids through the ladder in
`--limit` batches, then `$PY src/asr.py --from-ledger`, then `build_kb.py`.

## Watch (incremental; no cron — the night shift invokes it)

`$PY src/watch.py` reads the watchlist from `CONFIG.json "channels"`
(one GET of the per-channel RSS feed each), appends new ids to
`raw/queue/<channel>.tsv` for the night harvest. `--dry-run` reports only.
Follow with harvest → build_kb.

## Discipline (enforced in code, non-negotiable)

Every batch prints `DONE ok=X empty=Y skipped=Z failed=W` (+ `coverage: N of M
(pct%)`). No DONE line = it didn't finish. >30% same-error failures print
`HALT majority-fail …` and exit 2. Offline audit: `$PY src/self_test.py`
(zero network, must exit 0). Query hits print score, title, snippet and
`https://youtu.be/<id>`.
