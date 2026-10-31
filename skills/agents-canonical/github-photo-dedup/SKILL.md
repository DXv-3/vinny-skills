---
name: github-photo-dedup
description: >
  Treat GitHub as a personal database to discover every repository related to
  photo/image deduplication—your repos, orgs, stars, and the wider ecosystem.
  Runs multi-query repo and code search via grok_com_github MCP, merges and
  deduplicates results, and ranks by relevance. Use when the user wants repos
  about deduping photos, duplicate images, perceptual hashing, imagededup,
  near-duplicate detection, or runs /github-photo-dedup. Triggers: photo dedup,
  image deduplication, find duplicate photos on github, github as database.
---

# GitHub Photo Dedup Discovery

Use **GitHub as the user's personal + global database**. Do not guess—run searches, merge results, and deliver a ranked report.

## Prerequisites

- MCP server: `grok_com_github`
- Before any `CallMcpTool`, read the tool schema under:
  `~/.grok/projects/*/mcps/grok_com_github/tools/<tool>.json`
- Required tools: `get_me`, `search_repositories`, `search_code` (optional: `get_file_contents` for README spot-checks on top hits)

If MCP calls fail (auth/rate limit), say so clearly and retry with fewer queries or smaller `perPage`.

## Workflow

### 1. Establish identity (personal database layer)

Call `get_me` on `grok_com_github`. Save `login` for scoped queries.

### 2. Search the user's GitHub footprint first

Run `search_repositories` with `minimal_output: false` when you need stars/description/topics. Paginate (`page` 1–3, `perPage` 100) until empty or rate-limited.

**Personal scope queries** (replace `LOGIN` with `get_me` login):

| Query | Purpose |
|-------|---------|
| `user:LOGIN (dedup OR dedupe OR duplicate) (photo OR image OR picture)` | Owned repos |
| `user:LOGIN (perceptual OR phash OR imagededup OR imagehash OR dhash OR pHash)` | Hash-based dedup |
| `user:LOGIN topic:deduplication` | Topic-tagged |
| `user:LOGIN (near-duplicate OR "duplicate image" OR "duplicate photo")` | Wording variants |

Also run `search_code` scoped to the user when repo search is thin:

- `user:LOGIN (dedup OR duplicate) (image OR photo) in:file`
- `user:LOGIN (ImageHash OR imagehash OR imagededup OR phash) language:python`

### 3. Search the global ecosystem

Run **all** repository queries below (paginate first 2 pages each). See `references/search-queries.md` for the full list and code-search variants.

Core global queries:

```
(photo OR image OR picture) (dedup OR dedupe OR deduplication OR duplicate)
topic:deduplication
(perceptual OR phash OR imagededup OR imagehash) (duplicate OR dedup) (image OR photo)
"duplicate photo" OR "duplicate image" OR "near duplicate" images
imagededup OR image-dedup OR photo-dedup in:name,description,readme
stars:>10 (dedup OR duplicate) (image OR photo)
```

Tune with user hints: `language:python`, `org:NAME`, `created:>2020-01-01`, `fork:false`, `archived:false`.

### 4. Merge, dedupe, and score

1. **Dedupe key**: `owner/login + repo name` (normalize URLs to `owner/repo`).
2. **Buckets**:
   - **Yours** — `user:LOGIN` or owner == LOGIN
   - **Starred / engaged** — only if search or user says to include; use `user:LOGIN` in code search on starred repos is not direct—prefer user-provided lists
   - **Ecosystem** — everything else
3. **Relevance score** (higher = better match):
   - +3 name/description/readme mentions dedup + photo/image
   - +2 topics or `imagededup` / perceptual hash libraries
   - +1 code search hit in README or main module
   - +0.5 per 100 stars (cap +2)
   - −2 if only generic "deduplication" (data/DB) with no image/photo signal
4. Drop repos with **no** image/photo signal unless user asked for broad "dedup" only.

### 5. Enrich top candidates (optional, top 10)

For the highest-scored repos, optionally `get_file_contents` on `README.md` to confirm: duplicate detection method (hash, CNN, EXIF, filesystem), languages, and maturity. One sentence per repo max.

### 6. Deliver the report

Use this structure:

```markdown
# Photo dedup repos on GitHub

## Summary
- Searched: [date], GitHub user: LOGIN
- Unique repos found: N (Y yours, M ecosystem)
- Best starting points: [1–3 repo links]

## Your repositories
| Repo | Stars | Why it matches |
|------|-------|----------------|
| owner/repo | … | … |

## Ecosystem (ranked)
| Repo | Stars | Updated | Why it matches |
|------|-------|---------|----------------|
| … | … | … | … |

## Code signals (optional)
Repos surfaced only via code search but weak metadata—list briefly.

## Suggested next steps
- Clone/evaluate top 3
- Star or fork for your "personal database"
- Narrow search: [concrete query if user wants subset]
```

Always use **full** `https://github.com/owner/repo` links.

## User refinements

If the user specifies, adjust before searching:

- **Scope**: only my repos / include forks / include archived
- **Tech**: Python, Rust, mobile, CLI, library vs app
- **Method**: perceptual hash, ML embeddings, filesystem metadata, cloud albums
- **Synonyms**: dedubing → deduping; "same photo", "copy images", "photo library cleanup"

## Constraints

- GitHub Search API: max **1000** results per query type; paginate but do not loop endlessly.
- `search_code` query max **256** characters—keep queries short.
- Prefer `search_repositories` for discovery; use `search_code` to catch repos with poor descriptions.
- Do not fabricate repos—every row must come from an MCP search result.

## Slash command

`/github-photo-dedup` — run the full workflow and produce the report.