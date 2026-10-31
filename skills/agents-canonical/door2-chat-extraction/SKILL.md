---
name: door2-chat-extraction
description: "Door 2 — logged-in chat extraction, any site"
---

# Door 2 — logged-in chat extraction, any site

The proven recipe from the full Manus pull (2026-09-27: 65 conversations + 744 files,
45.9MB, zero failures, git `0cb70e8`). Works on any SPA that talks to a JSON API under
the user's session. Nothing auto-sends; everything is read-only GET-shaped; the user's
login is theirs — passwords/keys stay `[NEEDS USER]` forever.

## The pipeline (7 phases)

```
P0 preflight → P1 open + login check → P2 endpoint observation → P3 auth capture
→ P4 enumerate → P5 shape probe → P6 batched harvest → P7 files → P8 ingest+checkpoint
```

Browser control: run under the `browser-use:control-browser` skill (IAB backend).
**Every JS call re-bootstraps the runtime and re-selects the same backend.** State that
must survive across calls lives in `window.__*` page globals and on disk — never in
kernel variables (every call is a fresh kernel).

### P0 — Preflight
- Confirm the target site + that the user ordered extraction of **their own** account.
- `mkdir -p ~/SkillDrive/staging/<site>-web` — staging root. One subdir per conversation id.
- Set todos: enumerate → harvest → files → ingest. Announce visibility (browser pane shows).

### P1 — Open + login check
- `agent.browsers.getForUrl("https://<site>/")` → `tabs.new()` → `goto` → explicit
  `waitForLoadState({state:"domcontentloaded"})`.
- SPAs render late: if `domSnapshot()` is thin (<400 chars), wait 3–4s and re-snapshot
  before concluding anything. Still thin → screenshot branch (emit in same cell).
- Login wall → **stop, tell the user to log in, continue on their go.** Never touch credentials.
- Verify login from page facts (sidebar/account list renders, user info in localStorage).

### P2 — Endpoint observation (never guess)
```js
performance.getEntriesByType('resource').map(e => e.name)
  .filter(u => u.includes('api') || u.includes(host))
  .filter(u => !/\.(js|css|png|jpg|svg|woff2?|ico|mp4|webp)(\?|$)/.test(u))
```
- Lazy lists don't load until used: **click a conversation / scroll the sidebar**, then
  re-read resource entries. The real method names appear (e.g. Manus:
  `session.v1.SessionService/ListSessions`, `api/chat/getSessionV2?sessionId=`,
  `api/chat/getSessionFilesV2?sessionId=&type=private`).
- Also scan `localStorage` keys — SPAs often cache session lists (`sessions_detail`).
- Record: API host, auth style (Bearer header vs cookies), list method, per-item
  detail method, files/attachments method. **Observed facts only.** If a call 401s with
  "missing authorization header" → P3. Cookie-auth instead → always `credentials: 'include'`.

### P3 — Auth capture (page context only)
```js
// patch fetch to record the app's own header, then trigger one real API call (click something)
window.__authCapture = { last: null };
const orig = window.fetch.bind(window);
window.fetch = (...args) => { /* record args[1].headers.authorization, delegate */ };
```
- Keep the token in `window.__authCapture.last`. **Never return it to the model, never
  print, never write it to disk.** Every later in-page fetch passes it as a header.
- Sessions expire: if calls start 401ing mid-run, re-trigger the patch/capture once.

### P4 — Enumerate everything
- Call the observed list method from page context with the captured auth; paginate on
  its cursor/offset field until exhausted (cap ~50 pages); stash `window.__allSessions`.
- Return only `total` + 3 sample items + field names — not the list.
- Report the count to the user vs. any known subset before continuing.

### P5 — Shape probe (one conversation, defensively)
- Fetch detail + files/attachments for ONE id. Return **raw heads + sizes first** —
  do not pre-parse shapes you haven't seen. Wrap every access; a wrong assumption throws
  `undefined` deep in evaluate and costs a round-trip (Manus lesson: `files` was a list
  of file objects each holding `raw[]` entries — assumed flat, probe crashed).
- Identify per file entry: inline content fields (`fileContent`), URL fields (`url`,
  `inlineImageUrl`, `rawUrl`), path/filename fields. Message events: chat vs tool/action
  vs explanation types; attachment markers inside message `contents[]`.

### P6 — Batched harvest (resumable)
- Page-side accumulator `window.__buf`; fetch **9–12 conversations per evaluate call**,
  250–300ms sleep between items, push `{id, title, createdAt, <payloads>}`; return only
  per-item `{id, KB}` summaries + errors.
- Drain to disk in ≤4MB chunks: evaluate returns `JSON.stringify(bufChunk)` and shifts
  them off; Node side writes `~/SkillDrive/staging/<site>-web/<id>/{conversation,files,meta}.json`.
- Failure isolation: one bad conversation = one error entry, loop continues. Note the
  completed count after every batch so an interrupted run resumes from where it stopped.

### P7 — Files: inline + downloads
- Run `scripts/stage-to-files.py <staging_root> <files_root>` — writes inline content
  entries as real files preserving paths, downloads every URL-bearing entry (6 threads,
  60s timeout, per-file failure isolation), writes `_MANIFEST.json`.
- **Test one signed URL with plain curl first** — Manus CDN signed URLs returned 200
  without auth; downloading disk-side (no browser bridge, no base64) is 10× cheaper.
  If 401/403 → download via in-page fetch with credentials → base64 → Node fs.
- Manifest check: files on disk == file objects in manifests. Report MB + failures.

### P8 — Ingest + checkpoint
- Write/import a converter into `~/bin/skilldrive` (see `import-manus-web` for the
  pattern: frontmatter {source, id, title, date, models, url} → `### USER/AGENT` chat
  blocks → `> [tool]` action lines → attachment markers → `### FILES IN THIS TASK`
  inventory pointing at the extracted tree).
- `skilldrive import-<site>-web` → `scan` → `extract` → `index` → `stats`.
- `git -C ~/SkillDrive add -A && git commit` · append BUILD-STATE line · update memory.
- Supersession: if an older partial source covers the same chats, keep both rows, note
  which is authoritative (never delete).

## Field-tested gotchas (each one cost a round-trip on Manus)
1. Thin DOM snapshot ≠ broken page — SPA needs seconds; re-snapshot before screenshot.
2. Endpoint names must be **observed** (click to trigger lazy calls), never constructed.
3. 401 "missing authorization header" = Bearer API; capture from the app's own fetch.
4. Every evaluate is defensive or it dies on `undefined`: raw heads before shape logic.
5. Signed-URL downloads usually don't need the browser at all — curl-test first.
6. Add new commands to **every** dispatch point (choices + branch condition + map) — the
   Manus import silently no-op'd when one was missed.
7. Return summaries over the bridge; full payloads cross only during disk-drain chunks.
8. old-source supersession: keep, mark authoritative, never delete.

## Adapting to a new site (the actual work)
P2 and P5 are the only site-specific phases. For z.ai / DeepSeek / Qwen expect the same
shape: one authenticated list endpoint + one per-chat endpoint + file/attachment refs.
GraphQL sites: observe the operation names in resource entries, replay the exact query
strings the app sent. Sites without JSON APIs: fall back to DOM-walking each conversation
(slower — same staging + ingest contract).
