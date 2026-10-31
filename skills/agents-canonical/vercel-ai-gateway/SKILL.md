---
name: vercel-ai-gateway
description: "Use Vercel AI Gateway when the user asks for it or its API."
---

# Vercel AI Gateway

## Purpose
Use Vercel AI Gateway with the user-connected `custom.vercel-ai-gateway` credential.

## Tooling
`bin/jev.py` -- TypeSafe Jev decision model via the TypeSafe-compatible endpoint
`POST /typesafe/v1/systemone`. `choice` / `noul` / `score` subcommands, plus
`raw --json` for full control.

Python CLIs must import `/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py`
and call `add_surrogate_to_request(...)`, `url_with_surrogate_query_param(...)`,
or `url_with_surrogate_path_segment(...)` before authenticated requests, matching
where the provider reads the key (bearer_header here). If they use `urllib`, read
JSON responses with `read_json_response(resp)` from the same helper instead of
calling `resp.read()` directly. They must send only `hsurr:*` values, and only to
the hosts below.

## Auth
The credential is stored via the Secure Vault connector; nothing here collects one.
Never ask the user to paste a raw key in chat, set a secret environment variable,
pass a secret flag, or write an auth file.

A 401 or 403 is a question about the request before it is a question about the key.
Check that the credential was attached at all: a request built without the helpers
named under Tooling carries nothing, and that looks exactly like a wrong or
under-scoped token. Only once a request that did carry the credential is still
rejected, call `credentials.request_api_access` with `reconnect` to replace it.
The connector is stored as `custom.vercel-ai-gateway`.

## Operating Rules
1. Use this skill when the user asks for Vercel AI Gateway or this provider's API.
2. Restrict authenticated requests to: ai-gateway.vercel.sh.
3. Do not print, log, or persist raw credentials.
4. If auth is missing or rejected, follow the Auth section rather than asking for a key.

## Notes
- Jev on this gateway: `POST https://ai-gateway.vercel.sh/typesafe/v1/systemone`,
  model `typesafe-ai/jev`, TypeSafe native request/response shape (drop-in for the
  OpenRouter Decisions endpoint). Free until 2026-09-25; afterwards billed at
  $0.042/MTok input through the team's gateway credits.
- Probabilities come back rounded to 2 decimals (gateway behavior, not the model).
