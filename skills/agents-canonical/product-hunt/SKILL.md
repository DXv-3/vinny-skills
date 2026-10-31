---
name: product-hunt
description: "Browse Product Hunt launches by topic, daily leaderboard, and full launch teardown through the v2 GraphQL API — framed as a parts-stealing idea engine. Use when the user wants to see what's launching, find what was built in an idea space, or strip a launch for stealable parts. (The API has no keyword search on launches: go keyword → topics → launches.)"
---

# Product Hunt parts engine

## Purpose

Turn Product Hunt launches into stealable parts. Never start from scratch:
for each launch report what it does, the mechanism worth stealing, traction
signals, who built it, and where to see it live.

## Tooling

`~/workspace/skills/product-hunt/bin/ph.py` — stdlib-only Python CLI.

```bash
ph.py hunt "<idea>" [-n 5]                # EASY BUTTON: idea → best topic → top launches
ph.py topics "ai agents" [-n 10]          # keyword → topics (the ONLY keyword search)
ph.py launches --topic ai-agents [-n 10]  # top launches in a topic
ph.py leaderboard [--date 2026-09-14]     # what's hot on a day (default: today)
ph.py post <slug-or-id> [--comments 3]    # full teardown: pitch, links, makers, top comments
ph.py auth                                # verify credentials; prints OK/FAIL only
ph.py save / ph.py forget                 # remember / delete the key+secret (0600 file)
```

Flags: `--token` / `PH_TOKEN` for a developer bearer token; `--client-id` /
`--client-secret` or `PH_CLIENT_ID` / `PH_CLIENT_SECRET` for the OAuth exchange.
`--json` on any command for machine output. All human output is already framed
for parts-stealing: what it does / traction / who / live links / filed-under.

## Auth

No Secure Vault connector exists for Product Hunt: the API needs a Key+Secret
pair and the vault holds exactly one credential, so a connector was declined
(2026-09-14 — do not re-request it; the answer will not change).

1. User creates an app at https://www.producthunt.com/v2/oauth/applications
   ("Add an application") → API Key + API Secret. Must be the **Confidential**
   client type — Public (PKCE) issues no secret and cannot do the exchange.
2. Credential storage (their explicit choice, asked once): `ph.py save` writes
   the pair to `~/.config/product-hunt/credentials` (mode 600, never printed).
   `ph.py forget` deletes it — one-step revoke. Without a saved file, every
   session needs the pair pasted again (transient use only, never stored).
3. Or they hold a long-lived developer token (`phc_…`) → `PH_TOKEN`, and the
   CLI uses it directly as the bearer.

The CLI exchanges key+secret for a bearer token in-memory per run
(`POST /v2/oauth/token`, `grant_type=client_credentials`) and hits
`POST /v2/api/graphql`. Credentials are never logged or printed — errors say
"auth rejected (401)" without echoing anything.

## Operating Rules

1. **Never invent launch keyword search.** `posts` accepts no `query`/`search`
   argument — the call fails. Always resolve: keyword → `topics` → pick slug →
   `launches --topic`. Say so plainly when the user asks to "search launches".
2. Copy slugs and IDs from CLI output; never guess them.
3. Never print the key, secret, or bearer token. Redact on error.
4. Frame every result for parts-stealing: *What it does* (tagline + pitch),
   *Mechanism worth stealing* (read the description for the how),
   *Traction* (votes, comments, launch date), *Who* (makers as handles),
   *See it live* (producthunt URL + website).
5. Maker/user stats from the API are unreliable (counts return 0 or
   `[REDACTED]`); use them as handles, never as metrics.
6. Keep queries lean — Product Hunt rate-limits on query complexity. Default
   `-n 10`; raise it only when the user asks for more.
