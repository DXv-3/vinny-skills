# BEST PRACTICES — full ability, minimum tokens

How to have all 290 skills + every plugin/MCP ability available on this machine without burning
the metered grant. Companion to `INDEX.md` (the lean map) — read that first, this second, and
nothing else by default.

## The prime rule: addressable ≠ loaded

Every skill is addressable by name at zero cost. **Loading is the only expensive part.**
Ability comes from knowing what exists (INDEX.md) and loading the right 1–2 files — never from
holding the library in context.

### The disclosure ladder (with real costs)

| Level | What | Cost | Rule |
|---|---|---|---|
| L0 | `INDEX.md` + memory + state files | ~4K, once per session | Always the entry point |
| L1 | Frontmatter of a candidate: `head -40 ~/.agents/skills/<name>/SKILL.md` | ~150 each | Screen 3–5 candidates here |
| L2 | Full SKILL.md of the 1–2 finalists | ~500–2,500 each | Only what you will execute |
| L3 | The skill's reference files/scripts/CSVs | varies | Only at execution time, only the cited file |

### The 1% rule, priced

`using-superpowers` says: if there's ≥1% chance a skill applies, invoke it. Follow it — but
invoke at L1 (screen the frontmatter), drop wrong skills fast, and spend L2 only on the chosen
one. The 1% rule governs *whether to consider*, never *how much to read*.

## When to skip skills entirely

A skill earns a load only if it adds net-new procedure or data you don't already have:
- Plain git/shell/python/SQL competence → no skill, just do it.
- The task is trivial or a one-line fix → no skill.
- A state file already answers it (BUILD-STATE, CONQUEST-PLAN, research INDEX) → read the file, not a skill.
- You want validation of something you already know → that's what the adversarial-review stage is for, not another load.

## Routing

- **Trivial + single-domain** → act directly. No orchestrator.
- **Non-trivial, multi-domain, or "which skills?"** → `skill-orchestrator`. Its real token value:
  it writes `AGENT-BRIEF.md` to the project root, so the executing agent (this session later, a
  subagent, a fresh session) reads the brief instead of re-deriving the plan from chat.
- **Research** → Lane C ladder, `deep-research-free` by default; checkpoint findings to
  `~/Documents/research/INDEX.md` the same turn, or the next session re-pays for the same search.
- **Never re-research what the INDEX covers.** That rule has saved more tokens than every other rule combined.

## Query, don't sweep

- Skill lookup: `~/bin/skills-indexer --query <term>` (0.003s). Never `find`/`grep -r` over
  `~/.agents/skills/` — 120s and a token flood for the same answer.
- Prompt KB (4,596 records): kb-waterhole MCP `kb_search`/`kb_get`/`kb_stats` — query it, cite
  record IDs. Never dump tables/DB contents into chat.
- Big lists (inventory 115KB, COVERAGE 56KB, catalog TSV 207KB) stay on disk; grep a line out,
  don't cat the file.

## Subagent discipline

- Offload broad sweeps to the Explore agent and ask for **verdicts + paths, not file dumps** —
  conclusions come back in a paragraph; dumps come back in 50K tokens.
- **ONE subagent at a time on this machine** (hard limit).
- Subagent prompts must be self-contained: objective, constraints, what to return, what NOT to do.
- Never have a subagent paste large file contents into its final message; have it write artifacts
  to disk and report the path.

## Token clock

- **ZCode daytime tokens are metered** (300M grant through 2026-09-27) — spend them on building
  and money moves, not bulk reading.
- **Nights 23:00–09:00 are free Flash** — schedule bulk reads, chat mining, catalog rebuilds,
  index regeneration there (night shift appends to `~/Projects/NIGHT-SHIFT-LOG.md`).
- **Second opinions / reviews** → OpenCode headless free REMOTE models only, chain order:
  `openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` first (live-verified;
  lightning + muse-spark left the free list 9/26), then kimi-k3-free (unverified), else skip.
- **Never** route work to local ollama or any local model — this MacBook Air cannot run them
  (standing rule). **Never** invoke paid slugs — anything needing a key or money is `[NEEDS USER]`.

## Output discipline (yours, not just the library's)

- Don't echo file contents back into chat — report the path, the line number, the verdict.
- Tables for short enumerable facts; prose for everything else.
- Drafts never auto-send; sends are by hand (standing rule).
- One reversible batch at a time: git baseline → build → tests green → checkpoint.

## The expensive six (anti-patterns)

1. Bulk-loading SKILL.mds "just in case" — screen at L1 instead.
2. `find`/`grep -r` over the library — `skills-indexer --query` instead.
3. Loading `SKILLS-INVENTORY.md` (≈29K tokens) when `INDEX.md` (≈4K) answers.
4. Re-running research the INDEX already covers.
5. Pasting KB/DB/catalog dumps into context — query + cite IDs instead.
6. Doing at 2pm what could wait for the free night window.

## Maintenance

- After skill add/remove: `~/bin/skills-indexer`, update lane counts in `INDEX.md` +
  `skill-orchestrator/SKILL.md`, regenerate `skill-orchestrator/COVERAGE.md`.
- Keep `INDEX.md` lean (hooks ≤ 8 words, grouped lines). If it starts growing past ~5K tokens,
  it's failing its one job — push detail back down to frontmatter and COVERAGE.
- New skill dirs go in `~/.agents/skills/<name>/SKILL.md` with a `name:` + one-paragraph
  `description:` frontmatter — that description IS the L1 screen, so write it as a hook,
  not a spec.
