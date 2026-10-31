---
name: chat-pattern-miner
description: Ingest Vinny's past AI chats (ZCode rollout JSONL or any exported chat text), extract his working patterns, preferences, and recurring frustrations, and convert them into concrete ZCode artifacts - hooks, commands, AGENTS.md rules, and skills. Analysis produces DRAFTS only; nothing is auto-installed or auto-sent.
---

# Chat Pattern Miner

Turn chat history into enforced configuration. You study how Vinny actually works, then propose machine-enforced versions of his habits: hooks that fire automatically, slash commands for repeated workflows, AGENTS.md rules for recurring corrections.

## Non-negotiable rules (from standing instructions)

- **Drafts only.** Never install a hook, edit config.json, or send anything. Output files go to `~/Projects/chat-mining/OUT/` and wait for Vinny's go.
- **New files only.** Never rename, move, or delete anything - not source chats, not existing config.
- **Never re-research what INDEX covers.** If `~/Projects/chat-mining/INDEX.md` exists, read it first; append findings, don't redo analysis.
- Respect token metering: do bulk file reading with cheap scripted extraction (the Python script), spend model tokens only on interpretation.

## Workflow

### 1. Gather transcripts

All sources land in the same corpus dir, so mining is identical regardless of origin. Check `corpus/_INDEX.txt` first - already-imported sources should not be re-imported.

- **ZCode's own history** (`~/.zcode/cli/rollout/`):
  `python3 "$ZCODE_SKILL_DIR/scripts/extract-chats.py" --source rollout --out ~/Projects/chat-mining/corpus/`
- **opencode history** (local db, hundreds of sessions):
  `python3 "$ZCODE_SKILL_DIR/scripts/import-chats.py" opencode --out ~/Projects/chat-mining/corpus/` (add `--limit N` for most recent N)
- **ChatGPT export**: Vinny downloads it himself (Settings → Data controls → Export data; arrives as zip with conversations.json - takes up to a day). Then:
  `python3 "$ZCODE_SKILL_DIR/scripts/import-chats.py" chatgpt ~/Downloads/conversations.json --out ~/Projects/chat-mining/corpus/`
- **Claude.ai export**: Vinny downloads it himself (Settings → Privacy → Export data). Then:
  `python3 "$ZCODE_SKILL_DIR/scripts/import-chats.py" claude ~/Downloads/<export-dir> --out ~/Projects/chat-mining/corpus/`
- **Any other uploads** (.txt/.md/.json dumps): point extract-chats.py at the directory.

Never ask Vinny for credentials or try to log into any account - exports are manual, by him.

The extractor writes one plain-text file per conversation, user/assistant turns labeled, tools and boilerplate stripped - cheap to read, no JSON parsing needed afterward.

### 2. Mine for patterns

Read the corpus looking for, in priority order:

1. **Corrections** - every time Vinny said "no, do X instead", "I told you", "stop doing Y". Each is a missing rule or hook.
2. **Repeated instructions** - things he re-types every session (context loading, standing rules he has to restate). Each is a SessionStart hook or AGENTS.md rule candidate.
3. **Repeated workflows** - sequences he triggers by hand 3+ times (audit → build → test → checkpoint). Each is a `/command` candidate.
4. **Frustrations** - "why does it never...", "it keeps...". Each is either a skill gap or a PostToolUseFailure hook candidate.
5. **Approval patterns** - what he always says yes to (safe reads) vs what he wants asked about (git push, deletes, sends). Feeds PreToolUse/PermissionRequest hooks.

### 3. Score and select

For each pattern, write one line: pattern, evidence (quote + file), frequency, and artifact type. Only propose an artifact if the pattern appeared **3+ times** - one-off requests are noise. Cap proposals at 10 per run; rank by (frequency × money-or-damage-avoided).

### 4. Emit drafts

Write each artifact as a ready-to-paste file in `~/Projects/chat-mining/OUT/` using `references/output-template.md`:

- `hook-<slug>.md` - exact JSON for the `hooks` block of `~/.zcode/cli/config.json` + the script it calls
- `command-<slug>.md` - markdown command file for `~/.zcode/commands/`
- `agents-rule-<slug>.md` - bullet text ready to append to `~/.zcode/AGENTS.md`
- `SUMMARY.md` - the ranked table of everything found, with a one-line "install?" checkbox per item

Remember in every hook draft: `"enabled": true` is required, matchers are case-sensitive regexes (`Bash` not `bash`), and only the seven real event names are valid.

### 5. Checkpoint

Append to `~/Projects/chat-mining/INDEX.md`: date, corpus size (chats/tokens mined), top findings, and which drafts are pending install. Update it BEFORE presenting results, so a dead session never loses the analysis.

### 6. Present, don't install

Show Vinny SUMMARY.md contents. End with the install batch ready to go on his word - one reversible batch at a time: baseline the current config, apply, verify the hook fires (see the diagnosing-hooks skill), checkpoint.
