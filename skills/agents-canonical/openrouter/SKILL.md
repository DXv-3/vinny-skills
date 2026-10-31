---
name: openrouter
description: "Use Openrouter when the user asks for Openrouter or this provider's API."
---

# Openrouter

## Purpose
Use Openrouter with the user-connected `custom.openrouter` credential.

## Tooling
Add service-specific CLIs under `~/workspace/skills/openrouter/bin/`.
`bin/openrouter.py` -- generic REST CLI (get/post/put/patch/delete/put-file).
Run it with no args for usage. Auth is automatic via the authd
surrogate helper; the script never sees the real credential.
`bin/jev.py` -- TypeSafe Jev decision model via POST /api/alpha/decisions.
`choice` / `noul` / `score` subcommands, plus `raw --json` for full control.
Choice options and noul true/false come from the `criteria` record's keys;
score takes `criteria` as an ordered array. Live-tested 2026-09-20
(~$0.000013/decision).

Python CLIs must import `/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py` and call `add_surrogate_to_request(...)`, `url_with_surrogate_query_param(...)`, or `url_with_surrogate_path_segment(...)` before authenticated requests, matching where the provider reads the key. If they use `urllib`, read JSON responses with `read_json_response(resp)` from the same helper instead of calling `resp.read()` directly. They must send only `hsurr:*` values, and only to the hosts below.

## Auth
The credential is already stored; nothing here collects one. Never ask the user to paste a raw key in chat, set a secret environment variable, pass a secret flag, or write an auth file.

A 401 or 403 is a question about the request before it is a question about the key. Check that the credential was attached at all: a request built without the helpers named under Tooling carries nothing, and that looks exactly like a wrong or under-scoped token. Only once a request that did carry the credential is still rejected, call `credentials.request_api_access` with `reconnect` to replace it. The connector is stored as `custom.openrouter`.

## Operating Rules
1. Use this skill when the user asks for Openrouter or this provider's API.
2. Restrict authenticated requests to: openrouter.ai.
3. Do not print, log, or persist raw credentials.
4. If auth is missing or rejected, follow the Auth section rather than asking for a key.
