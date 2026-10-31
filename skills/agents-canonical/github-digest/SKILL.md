---
name: github-digest
description: "Digest a GitHub repo into a packaged parts brief: clone it, inventory the structure, name the stealable parts, and save a digest the user can revisit later. Trigger on 'digest this repo', 'package this github', 'look up this repo', or any GitHub link the user wants pulled apart for parts."
---

# GitHub Digest

## Purpose

Turn any GitHub repo the user points at into a packaged digest: what it is, what's inside, the stealable parts, what to skip, and a verdict. One digest per repo, saved where the user can find it later. This is the "strip it for parts" pipeline — never adopt, only extract.

## Workflow

1. **Get the repo.** Accept an owner/name, a full GitHub URL, or resolve ambiguity by asking (never guess among thousands of search hits). For public repos, `git clone --depth 1 <url>` into `/tmp/<repo>/`. For private repos or API metadata, use the `github` skill's `bin/gh.py`.
2. **Inventory.** File tree (excluding `.git`), line counts of the key files (`wc -l`), languages, README contents, repo size. Note the entry points (index.html, main.js, app entry, etc.).
3. **Read the key files.** Skim — don't dump. Entry page, main script, styles/config, and anything that looks like the core logic. Identify what each major piece does in one line.
4. **Judge.** Decide in plain words:
   - What it is (one line)
   - Stealable parts (concrete and named — a layout pattern, a style system, an asset pack, a mechanism)
   - Skip it (what's empty, stub, or beginner-level)
   - Verdict (what to take and what to leave)
5. **Write the digest.** Save to `~/workspace/your_files/github-digests/<repo-name>.md` using the template below. Plain words, no jargon, no tool talk.
6. **Report briefly.** Tell the user what it is and the 2–3 best parts in a few lines. Offer to extract a specific part into something reusable only if they want it.

## Output Contract

Every digest file follows this shape:

```markdown
# <repo-name> — repo digest

**Repo:** <owner>/<repo>
**Link:** <url>
**Digested:** <YYYY-MM-DD>

## What it is
<one plain line>

## What's inside
<file/structure inventory with line counts>

## Stealable parts
<concrete named parts>

## Skip it
<what's not worth taking and why>

## Verdict
<what to take, what to leave — one or two lines>
```

## Operating Rules

1. One digest per repo; overwrite the file if the user asks for a re-digest.
2. Never commit, push, or modify the repo — clone to `/tmp`, read only.
3. Clean up `/tmp/<repo>/` after the digest is written.
4. Keep digests in the user's voice: plain words, outcome-focused, no file paths as prose.
5. If the repo is huge, inventory the top two levels and read only the entry/key files — say what was skimmed.
6. Don't invent functionality — if the JS is a stub, say so.
