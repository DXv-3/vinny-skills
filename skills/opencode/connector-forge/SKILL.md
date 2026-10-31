---
name: connector-forge
description: Build a reusable API connector for any service: research its auth, store the key in macOS Keychain, generate a tested REST CLI. Use when the user says "connect X", "hook up X", "wire up X", or "make a connector for X".
---

# Connector Forge (OpenCode edition)

## Purpose
Turn any "connect &lt;service&gt;" request into a permanent connector on this Mac: the key in the Keychain, a small CLI under `~/.config/opencode/connectors/&lt;slug&gt;/`, verified with a real call.

This is a port of a vault-backed pipeline. OpenCode cannot reach that vault, so keys live in the **macOS Keychain** instead — same rule, different safe: a key never appears in chat, files, env vars, logs, or shell history.

## Workflow
1. **Research the provider's docs.** Three questions, from their API reference (not memory):
   - How does it authenticate? API key preferred; OAuth2 only if the API demands it.
   - Which hostnames serve the API? (e.g. `api.stripe.com`)
   - Where does the key go? `bearer_header`, `custom_header:<Name>`, or `query_param:<name>`.
2. **Key into the Keychain.** Never have the user paste a key into chat. Have them run this themselves in a terminal — `-w` with no value prompts securely, nothing echoes, nothing lands in history:
   `security add-generic-password -s "connector-<slug>" -a "<slug>" -w`
   Sanity check without revealing it: `security find-generic-password -s "connector-<slug>" -w | wc -c` (nonzero = stored).
3. **Stamp the CLI.** `python3 ~/.config/opencode/skills/connector-forge/forge.py --provider <slug> --name "<Display Name>" --hosts <host,...> --placement <placement>` — writes `~/.config/opencode/connectors/<slug>/<slug>.py` (stdlib only: get/post/put/patch/delete, key read from Keychain at runtime).
4. **Test with a cheap read** (profile/user endpoint or a list call). The first real call is what validates the key — nothing before it does.
5. **Report.** What was connected, the test result, two or three example commands.

## Keychain rules
- Service name: `connector-<slug>`. Account: `<slug>`.
- Read pattern (what the generated CLI does): `security find-generic-password -s <service> -w`, strip the trailing newline.
- Rotate/replace: run the step-2 command again (it updates in place).
- Remove: `security delete-generic-password -s "connector-<slug>"`.
- First use of a new item can pop a macOS "allow access" prompt — that is the user approving their own key, once.

## Debugging a rejected call, in order
1. Is the key attached at all? A request built without the Keychain lookup carries nothing and looks exactly like a bad key.
2. Scopes/permissions on the provider side (a token that can read may not be allowed to write — re-issue with wider scopes).
3. The key value last — rotate via step 2.

## Operating Rules
1. One connector per service slug — reuse it, never re-capture for a new task.
2. Only call the documented API hosts.
3. Keep the CLI thin and generic; service-specific logic goes in later, separate skills.
4. The generated CLI never prints the key. If you need to confirm one is stored, use the `wc -c` check from step 2.
