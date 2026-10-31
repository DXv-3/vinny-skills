---
name: sweep
description: Triage any folder with SWEEP — extracts all archives (including nested zips), pulls text out of every document (pdf/docx/xlsx/pptx/rtf/odt/plain code), compiles everything into one searchable corpus, then scores every file KEEP / MAYBE / TRASH with real reasons: exact-duplicate detection by hash, OS junk, temp/partial files, empty files, old installers, cache folders, content-based word counts. READ-ONLY on the target — nothing is ever deleted; output lands in one SWEEP-DATA folder (report, manifest CSV, verdicts JSON, text corpus). Moving TRASH items to a staging folder is a separate explicit step (--stage-trash) that writes an undo script, and requires Vinny's explicit go. Use when Vinny says sweep/triage/clean up a folder, asks what's in a directory, what's useful vs trash, or wants files extracted and compiled.
---

# SWEEP — folder triage

The script does the work. You read the report and give Vinny the verdict.

## Run it

```bash
python3 ~/.agents/skills/sweep/scripts/sweep.py TARGET_FOLDER
```

- Default output: `TARGET_FOLDER/SWEEP-DATA/`. Pass `--out DIR` to keep his folders
  untouched (report + caches land in DIR instead) — prefer this for his personal
  folders like `~/Downloads` or `~/Desktop`.
- `--no-extract` skips archive extraction (fast inventory only).

## After it runs

1. Read `SWEEP-DATA/SWEEP-REPORT.md` — it has the Overview table, TRASH list with
   reasons, MAYBE list, KEEP list, and duplicate groups.
2. Give Vinny the spread in 3 lines: X KEEP, Y MAYBE, Z TRASH, N GB reclaimable —
   plus the 3 most interesting things you found in the corpus.
3. Never run `--stage-trash` yourself. It moves files (reversibly, with
   `undo-trash.sh`). Name what it would move and let him pull the trigger:
   he runs it, or says "run it" and states the folder himself.

## Scoring logic (so you can explain any verdict)

- TRASH: OS junk (.DS_Store, ~$ locks, __MACOSX), temp/partial files, empty files,
  exact hash-duplicates (best copy kept), installers older than 90 days,
  regenerable/cache folders.
- KEEP: ≥200 extractable words, or ≥30 words and modified in the last 180 days.
- MAYBE: everything else — media, archives, short files. The report says why.

## Limits

- `.7z`/`.rar` need manual handling (noted in the report's extraction log).
- Scanned/image-only PDFs get flagged "no extractable text", not trashed.
- `.git` internals are skipped; project folders are kept whole.
- Extraction caps: 500 MB per archive, 2 GB total, nested zips 3 levels.
