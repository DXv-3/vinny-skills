---
name: connector-forge
description: "Build a reusable API connector for any service: capture the key in the Secure Vault, scaffold the skill, stamp a tested REST CLI. Trigger when the user says 'connect X', 'hook up X', 'wire up X', or 'make a connector for X'."
---

# Connector Forge

## Purpose
Turn any "connect &lt;service&gt;" request into a permanent, reusable connector: a stored credential (Secure Vault), a skill directory, and a tested REST CLI — the same pipeline that produced the github connector.

## Workflow
1. **Research the provider's docs.** Three questions, answered from their API reference (not memory):
   - How does it authenticate? → `auth_scheme`: `api_key` (preferred) or `oauth2_code`.
   - Which bare hostnames serve the API? → `api_hosts` (egress to anything unlisted is refused later).
   - Where does the key go? → `placement`: `bearer_header`, `custom_header:<Name>`, `query_param:<name>`, or `url_path_segment`.
2. **Capture the key.** Call `credentials.request_api_access` with `provider=<slug>`, `api_hosts`, `auth_scheme`, `placement`. Send the returned capture link to the user on its own line with one short reassurance (it goes straight to secure storage, you never see it). Then STOP — do not poll or ask them to confirm. The runtime resumes the conversation when they submit; abandoned pages resume when they next write.
3. **Scaffold.** `/opt/hatch/skills/skill-creator/bin/scaffold-connector-skill --provider custom.<slug>` reads the connector from authd and writes `~/workspace/skills/<slug>/SKILL.md` with Tooling/Auth filled in. If it fails, the connector isn't stored yet — go back to step 2.
4. **Stamp the CLI.** `~/workspace/skills/connector-forge/bin/forge.py --provider <slug> --name "<Display Name>" --hosts <host,...>` drops `bin/<slug>.py` (generic REST CLI: get/post/put/patch/delete/put-file) into the skill, updates its SKILL.md Tooling section, and compiles it.
5. **Test with a cheap read** (profile/user endpoint, a list call). The first real call is what validates the key — nothing before it does.
6. **Report.** What was connected, the test result, and two or three example commands.

## Auth
- Keys are collected ONLY via `credentials.request_api_access`. Never ask for a raw key in chat, an env var, a CLI flag, or a file.
- Replacing a dead/wrong/under-scoped key: same call with `reconnect: true`, then re-test.
- Debugging a rejected call, in order: (a) was the credential attached at all — a request built without the surrogate helper carries nothing and looks exactly like a bad key; (b) scopes/permissions on the provider side; (c) the key value last. GitHub lesson, 2026-09-16: a fine-grained token could read but not fork (POST /forks → 404); a classic `public_repo` token fixed it.

## Operating Rules
1. One connector per provider slug — reuse it, never re-capture for a new task.
2. Authenticated requests go only to the `api_hosts` named at setup.
3. Never print, log, or persist raw credentials. Only `hsurr:*` surrogates travel, and only to allowed hosts.
4. After the user submits the key, the conversation resumes on its own — pick the task back up at step 3.
5. Keep the CLI thin and generic; service-specific logic lives in later, separate skills that import the pattern.
