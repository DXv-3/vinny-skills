# Draft Output Templates

Each draft in `~/Projects/chat-mining/OUT/` uses one of these formats. Drafts are never installed directly — Vinny reviews, then says "build" and the install happens as one reversible batch.

## hook-<slug>.md

```markdown
# Hook draft: <slug>
Event: <SessionStart|UserPromptSubmit|PreToolUse|PermissionRequest|PostToolUse|PostToolUseFailure|Stop>
Evidence: seen N times — "<short quote>" (<corpus file>)
Install target: hooks block of ~/.zcode/cli/config.json (merge into existing "hooks"; requires "enabled": true)

## config.json fragment
{
  "enabled": true,
  "events": {
    "<Event>": [
      {
        "matcher": "<case-sensitive regex, e.g. Bash>",
        "hooks": [
          { "type": "process", "command": "<absolute path>", "args": [], "timeoutMs": 10000,
            "statusMessage": "<what shows while it runs>" }
        ]
      }
    ]
  }
}

## script (save to ~/.zcode/hooks/<slug>.sh, chmod +x)
<complete script; exit 0 = pass, exit 2 = block; JSON on stdout only with recognized keys>

## Rollback
Remove the <Event> entry from config.json hooks.events; delete ~/.zcode/hooks/<slug>.sh.
```

## command-<slug>.md

```markdown
# Command draft: /<name>
Evidence: workflow requested N times — ...
Install target: ~/.zcode/commands/<name>.md

<full markdown command body with $ARGUMENTS placeholders where user input goes>

## Rollback
Delete ~/.zcode/commands/<name>.md
```

## agents-rule-<slug>.md

```markdown
# AGENTS.md rule draft: <slug>
Evidence: correction/repeat seen N times — "..."
Install target: append to ~/.zcode/AGENTS.md under the matching section

- <one imperative bullet, written as a standing rule>

## Rollback
Delete the bullet from ~/.zcode/AGENTS.md.
```

## SUMMARY.md (one per run)

| Draft | Type | Evidence (count) | Impact | Install? |
|---|---|---|---|---|
| hook-bash-guard | PreToolUse hook | 7 | blocks destructive cmds | [ ] |
| ... | | | | |

Followed by: proposed install order (one batch), and the verification step for each (how we'll confirm it fired, per diagnosing-hooks: check the hook run record in the ZCode log).
