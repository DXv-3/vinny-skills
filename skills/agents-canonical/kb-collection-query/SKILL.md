---
name: kb-collection-query
description: Owns ALL prompt-KB questions — query the 4,596-record prompt KB (~/surface/prompt_kb.db) for counts, families, techniques, and specific records. Triggers include "how many", "which records", "show me prompts that", "what families", and any jailbreak/system-prompt/prompt-KB noun. NEVER answer collection questions from memory — always query live.
---

# Prompt KB — route every collection question through the KB

## When this skill fires
"How many…", "which records…", "show me prompts that…", "what families…",
any jailbreak / system-prompt / prompt-KB noun (or its legacy "waterhole"
codename), any question whose answer lives in `~/surface/prompt_kb.db`
(4,596 records). The KB is the source of truth — never memory, never a
stale snapshot.

## Name map — the collection is the prompt KB
The collection is the **prompt KB**. "Waterhole" is a legacy codename that
appears in four places — the folder `~/waterhole/`, the shim endpoint
`/api/waterhole`, the MCP server `kb-waterhole`, and the skill
`waterhole-ask` — and means the same collection every time. New artifacts
say **prompt KB** first. Three doors:

| Door | When | How |
|---|---|---|
| MCP `kb-waterhole` | first choice inside ZCode (already wired) | `kb_search` / `kb_get` / `kb_stats` |
| HTTP shim :8921 | scriptable, tailnet agents | curl + bearer token (ladder below) |
| SQLite read-only | counts, family/technique joins | `sqlite3 "file:$HOME/surface/prompt_kb.db?mode=ro"` |

## Invocation ladder (try top-down)
1. **kb-waterhole MCP tools** — first choice inside ZCode: `kb_search`
   (FTS5+tags), `kb_get` (full record), `kb_stats` (totals). Read-only,
   auto-connected.
2. **`/kb` command** — ZCode slash command wrapping the MCP tools.
3. **`rank.py` (this dir)** — the Item 7 recipe executable: FTS5 then
   tag-aware re-rank (`--family` +5, `--technique` +3, `--type` +2 on top of
   bm25). Example: `python3 rank.py '"GODMODE ENABLED"' --type jailbreak`.
4. **Shim curl** — `token=$(cat ~/opencode-shim/.token) && curl -s -H
   "Authorization: Bearer $token" "http://100.107.4.112:8921/api/waterhole?q=<fts5>&limit=10"`.
   Bearer token comes from `~/opencode-shim/.token` via command substitution
   only — never echo it, never log it.
5. **Direct sqlite (read-only)** — `sqlite3 "file:$HOME/surface/prompt_kb.db?mode=ro" "…SELECT…"`.
   Family/technique counts are joins of `tags` × `prompts`, never full-text.
6. **VM `ask.py`** — authoritative CLI on dxv-3. Currently DOWN (ssh
   refused; decision D5 open). Recheck when ssh returns.

## Tag-aware ranking recipe
Run FTS5 for recall, then re-rank by tag joins for precision:
```sql
SELECT p.id, p.type, t.family, t.technique, p.name,
       bm25(prompts_fts) AS rel
FROM prompts_fts f JOIN prompts p ON p.id=f.id
LEFT JOIN tags t ON t.id=p.id
WHERE prompts_fts MATCH :q ORDER BY rel LIMIT 300;
```
then boost family +5 / technique +3 / type +2 and cut at N — or just use
`rank.py`, which does exactly this.

## VERIFIED GROUND TRUTH (live-queried 2026-09-21 and 2026-09-25 — anything not freshly re-queried is [verify live])

**prompts.type (all 13 types — the listed values sum to the total):**
user prompt 1248 · other 944 · instruction set 397 · system prompt 385 ·
template 345 · prompt discussion 264 · agent config 246 · jailbreak 245 ·
meta-prompt 227 · paper 149 · persona 126 · tool 11 · transcript 9.
Total 4596.
**tags.content_type:** payload 3711 · other 260 · reference 238 ·
transcript 236 · paper 149 · defensive 2.
**Backends (everything tagged):** dispatcher-ollama-qwen2.5:7b-instruct 3996 ·
pilot-manual 245 (authoritative for jailbreaks) · dispatcher-ollama-qwen25-7b
195 · catalog-ingest 160.
**Families (whole KB):** gogodode-l1b3rt4s **142** · vinny **19** · pliny
**18** · companion-lite **16** · emancipation-protocol **7** · bt6 **6** ·
rebel **5** · gpt4-roleplay-kit **5**.
**Techniques — jailbreak-scoped / whole-KB (always cite the scope):**
persona-activation 53/261 · divider-escalation 39/46 · token-injection 27/427 ·
predicted-followup 25/183 · hypothetical-framing 22/90 · multi-turn-ladder
16/153 · godmode-variant 15/45 · roleplay 9/84 · encoding-obfuscation 3/14.
**FTS5 (measured):** unquoted terms are implicit AND — `godmode enabled`
unquoted → **226** records; quoted `"godmode enabled"` as an exact phrase →
**63**; bare `godmode` → **375**; `pliny` → **61**; `"zero push back"` phrase
→ **10**. Quote the phrase for precision, go unquoted for recall — always
state which.
**Words:** 4,531,515 total · 4,402,730 across the 4,351 non-jailbreak rows.
**Copies:** both on-disk copies verified IDENTICAL (2026-09-21) — prefer
`~/surface/prompt_kb.db` (newer mtime); `~/waterhole/waterhole.db` is the
shim's copy.
**Key IDs:** high-candor cluster P002 P004 P015 P016 (surrounding family
P008 P009 P011 P013 P014 P018) · vendor shelf P019 Grok 4 (xAI), P050 AURA
Core CEO (TwinMind), P058/P059 Nosey Neighbor pre/post-rewrite, P047–P049
GitLegos decomposer/composer · not-payload shelf P017 and P001.
**Vocabulary wrinkle:** the MCP's family vocabulary differs from the SQLite
`tags` taxonomy (`none-detected`/`CUPT`/`Agent Zoo` vs
`gogodode-l1b3rt4s`/`vinny`/`pliny`) — always cite which door a number came
from.

## Ten worked examples (Q → pattern → invocation → result shape)
1. "How many jailbreaks are in the collection?" → type count → `kb_stats` →
   jailbreak=245.
2. "What families exist, how big?" → GROUP BY family → shelf docs or SQL →
   gogodode 142, vinny 19, pliny 18…
3. "Show me prompts that say GODMODE ENABLED" → quoted-phrase FTS →
   `rank.py '"GODMODE ENABLED"' --type jailbreak` → 63 records, IDs + snippets.
4. "Which records are Pliny?" → FTS `pliny` + family join → 61 FTS hits /
   18 family-tagged (the difference is textual mention vs family membership).
5. "What techniques does the collection use?" → GROUP BY technique → the
   two-scale numbers above (always cite the scope).
6. "Map the system-prompt shelf" → type='system prompt' family axes →
   `~/surface/shelves/SYSTEM-PROMPTS-SHELF.md`.
7. "Find the leaked Grok 4 prompt" → FTS `Grok` → **P019** → `kb_get` full
   text (tool inventory, pricing-redirect clauses).
8. "Anything like an autonomous CEO agent?" → FTS `airlock CEO JSON` →
   **P050** AURA Core (triple-context, JSON-only airlock).
9. "Self-replicating prompts?" → family `quine` / FTS `quine` → **P1827**
   PromptQuine; see also P760 (self-updating).
10. "How did the high-candor spec evolve?" → known-ID walk P002 → P004 →
    P015 → P016 → `~/surface/shelves/SYSTEM-PROMPTS-RUNDOWN.md` §1.

## Pilot regex lessons (2026-09-21, encoded — do not re-derive)
`/pliny|plinian/` never bare `/pliny/` · rebel =
`accelerator-rebel|zero push back|chaotic-inverted rebel|rebel family` ·
family patterns match **name+note** · TSVs parse with the csv module (real
tabs, `""` escapes) · `load_tags.py` upserts by ID · dedup notes are
analytical — source records never collapse.

## Hard rules
- READ-ONLY. Never write to the DB, never modify records, never collapse
  duplicates.
- Every claim carries its record ID.
- Every number carries the query that produced it and its date; anything not
  freshly queried is `[verify live]`.
