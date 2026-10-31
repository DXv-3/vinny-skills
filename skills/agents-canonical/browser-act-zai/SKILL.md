---
name: browser-act-zai
description: "Browser automation for Z.AI using BrowserAct. Use when working with z.ai, space-z.ai, chat.z.ai, GLM models, the Z.AI coding plan, or any workflow that needs to log into or interact with Z.AI through a real browser session. Triggers on: z.ai, space-z.ai, chat.z.ai, GLM, Z.AI login, Z.AI browser, browser-act zai. Never run browser-act commands directly via Bash — always invoke this skill first."
metadata:
  author: DXv-3 / BrowserAct
  homepage: https://www.browseract.com
  install: uv tool install browser-act-cli --python 3.12
  permissions:
  - Network access — for Z.AI website navigation and API calls
  - Filesystem read/write — browser profiles, session logs
  - CDP connection — chrome-direct mode for reusing local Chrome login state
  requires:
    runtime: Python 3.12+, uv package manager, browser-act-cli
  user-confirmation-required:
  - Browser creation (first time with a new browser type)
  - Login to Z.AI (credentials entry)
  - 'Sensitive operations: profile import, cookie management'
  version: 1.0.0
---

# browser-act-zai

Browser automation skill for **Z.AI** (chat.z.ai, space-z.ai) powered by BrowserAct.

Use this skill to:
- Log into Z.AI through a real browser (no API key needed)
- Select GLM models (glm-5.3, glm-5.2, glm-5.3-flash)
- Configure Deep Think / reasoning effort (Low / High / Max)
- Toggle Web Search and Tools on/off
- Extract chat responses and streamed output
- Maintain authenticated sessions across tasks

## Quick Start

After loading this skill, the first command is always:

```bash
browser-act get-skills zai --skill-version 1.0.0
```

This pulls the full runtime workflow — state-aware commands, Z.AI-specific element
indices, and dynamic directives. Do not skip this step.

## What this skill covers

| Task | Approach |
|------|----------|
| Log into Z.AI (space-z.ai) | Full browser session with login flow |
| Select a model (GLM-5.3, etc.) | Indexed DOM click via `state` + `click` |
| Configure Deep Think effort | Dropdown menu interaction via `state` + `click` |
| Toggle Web Search | Toggle button via `state` + `click` |
| Toggle Tools | Toggle button via `state` + `click` |
| Send a message and read the response | `input` + `state` + `get markdown` |
| Extract streamed response | `get markdown` or `network requests` for SSE |
| Maintain session across calls | Reuse same `--session` name |
| Bypass login blocks | `stealth` browser type + `solve-captcha` if needed |

## Z.AI URLs

| URL | Purpose |
|-----|---------|
| `https://chat.z.ai` | Main chat interface |
| `https://space-z.ai` | Z.AI coding / workspace |
| `https://api.z.ai` | API endpoints (not needed for browser login) |

## Workflow Summary

```
1. browser-act get-skills zai --skill-version 1.0.0
2. browser-act browser list          # find or create a browser
3. browser-act --session zai browser open <id> https://chat.z.ai
4. browser-act --session zai state   # see login form / chat UI
5. [if logged out] login flow → input email → input password → click submit
6. [after login] state → click model selector → select model → configure toggles
7. input message → state → get markdown / get text
8. browser-act session close zai     # when done
```

For the full command reference, element indices for Z.AI's current UI, and
troubleshooting guidance, always run `browser-act get-skills zai --skill-version 1.0.0`
first.
