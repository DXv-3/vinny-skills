---
name: arxiv
description: "Search arXiv papers and fetch paper metadata through the keyless arXiv query API."
---

# arXiv

## Purpose
Search papers, look up papers by arXiv ID, and pull full metadata (title,
authors, abstract, categories, PDF link) from arXiv. The public query API
needs no account and no key.

## Tooling
`bin/arxiv.py` -- thin CLI (stdlib only; works on my VM and on the Mac).
Atom XML is parsed to JSON so callers never touch XML.

    arxiv.py search <query> [--field all|ti|au|abs|co|jr|cat]
                            [--sort relevance|lastUpdatedDate|submittedDate]
                            [--order ascending|descending]
                            [--start N] [--max N]
    arxiv.py get <arxiv-id>[,<arxiv-id>...]
    arxiv.py raw <path-with-query>   # Atom XML straight through

Field prefixes: `ti` title, `au` author, `abs` abstract, `co` comment,
`jr` journal reference, `cat` category. Default `--field all` searches
everything. `--max` caps at 100 per call; page with `--start`.

Each result: `id, title, authors[], published, updated, summary,
categories[], primary_category, abs_url, pdf_url`.

Live-tested 2026-09-20: `search "quantum machine learning" --field ti`
returned 2 results; `get 1706.03762` returned "Attention Is All You Need".

## Auth
None. The query API at export.arxiv.org is keyless by design, so there is
no Secure Vault entry, no `custom.arxiv` connector, and no surrogate helper.
This differs from connector-forge skills on purpose, not by accident.

## Operating Rules
1. Use this skill when the user asks for arXiv papers or the arXiv API.
2. Restrict requests to: export.arxiv.org (and arxiv.org for the PDF/abs
   links the API itself returns).
3. Be kind to arXiv: one request every ~3 seconds; don't hammer pages.
4. Rate-limit and the Atom format are the two things most likely to break a
   caller; handle empty results (`[]`) as a normal outcome, not an error.
