---
name: youtube-kb
description: Build and query a local, private knowledge base from YouTube channels — transcripts, vector + keyword search, timestamped deep links. Use when the user shares a YouTube URL (video, youtu.be link, @handle, channel) and wants to ingest, save, search, or ask questions about a channel's content; when the user asks what a YouTuber says about a topic, which video covers something, or wants channel transcripts turned into a searchable database / vector store / RAG source.
---

# YouTube Knowledge Base (youtube-kb)

Turn any YouTube channel into a hybrid-search SQLite knowledge base (vector + FTS5),
then answer questions from it with citations and second-precision deep links.

## Requirements (one-time setup)

macOS defaults; adjust paths for other OSes. System Python's SQLite cannot load
extensions — Homebrew Python is required.

```bash
pip3 install --user yt-dlp                                   # extractor (or brew install yt-dlp)
/opt/homebrew/bin/python3.12 -m pip install --user --break-system-packages sqlite-vec fastembed
```

## Ingest a channel (resumable, idempotent)

```bash
/opt/homebrew/bin/python3.12 scripts/ingest.py <any-youtube-url> [--db <dir>] [--limit N] [--fresh]
```

- Accepts watch URLs, youtu.be links, @handles, /channel/UC... URLs. A video URL ingests its whole channel.
- Default KB location: `./data/` relative to cwd. Pass `--db <dir>` to place it elsewhere. One DB holds many channels.
- Re-running skips videos already ingested (`status='ok'`) and retries the rest — safe to rerun after failures.
- Whole channels take 10–90 min depending on YouTube rate limiting. Expect HTTP 429 storms;
  the script backs off (6 retries, up to 5 min each). For long runs, launch with a background exec
  and poll `SELECT status, COUNT(*) FROM videos GROUP BY status;` in the DB for progress.
- `--limit N` ingests only the N newest videos (good for smoke tests). `--fresh` rebuilds the DB.

## Search / answer questions

Local web UI (recommended): `python3 scripts/ui.py --db data` → http://127.0.0.1:8765 —
search with channel filters, channel maps (volume/adoption timelines), and filterable
knowledge tables (tools / money / frameworks / claims), all with deep links.

```bash
/opt/homebrew/bin/python3.12 scripts/query.py --stats                  # channels, videos, chunks
/opt/homebrew/bin/python3.12 scripts/query.py "how to get clients" --n 8
/opt/homebrew/bin/python3.12 scripts/query.py "entropy" --video l6DKRf-fAAM   # within one video
```

To answer a user's question, run 2–3 query variants (paraphrases + exact keywords),
read the returned chunks, then synthesize an answer that cites
`video title (date)` + a deep link of the form `https://youtu.be/VIDEOID?t=SECONDS`.
Every chunk result already includes that link. Cite only what the chunks actually say.

## If things break

- Captions/metadata errors like "page needs to be reloaded" or missing PO token →
  YouTube changed something; update yt-dlp first (`pip3 install --user -U yt-dlp`).
  The scripts already force `player_client=android` (the client that still works).
- Videos marked `no_subs` have no captions at all — they are skipped, not errors.
- `error` rows are transient (usually rate-limit): rerun the same ingest command to fill them.
- DB schema: `channels`, `videos` (incl. full `transcript` text), `chunks` (body + start_s/end_s),
  `chunks_fts` (BM25), `chunks_vec` (384-dim bge-small-en-v1.5). Query any of it directly with sqlite3.
