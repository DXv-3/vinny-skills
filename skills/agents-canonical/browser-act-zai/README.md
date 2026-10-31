# browser-act-zai

**Browser automation for Z.AI using BrowserAct — no API key required.**

Log into chat.z.ai or space-z.ai through a real browser. Select GLM models,
toggle Deep Think, Web Search, and Tools. Extract responses. All through
BrowserAct instead of raw Playwright.

---

## What this solves

Z.AI (GLM's coding platform) has a browser-based interface but no open API for
free/plus tier users. The existing OmniRoute `zai-web` executor uses raw Playwright
directly — this skill wraps that same workflow through BrowserAct, giving you:

- **Stealth fingerprints** — Z.AI's anti-bot detection is less likely to fire
- **Human handoff** — `remote-assist` hands off to a browser tab if login blocks
- **CAPTCHA solving** — `solve-captcha` handles verification challenges automatically
- **Session reuse** — import your real Chrome login state instead of re-authenticating
- **Multi-account isolation** — run Z.AI sessions in parallel in separate browsers
- **Proxy rotation** — route Z.AI traffic through residential proxies if needed

---

## What it can do

| Capability | Status |
|-----------|--------|
| Log into chat.z.ai | ✅ |
| Log into space-z.ai (coding workspace) | ✅ |
| Select GLM-5.3 / GLM-5.2 / GLM-5.3-Flash | ✅ |
| Configure Deep Think effort (Low / High / Max) | ✅ |
| Toggle Web Search on/off | ✅ |
| Toggle Tools (VLM) on/off | ✅ |
| Send messages and read streamed responses | ✅ |
| Extract full conversation as markdown | ✅ |
| Reuse existing Chrome login (profile import) | ✅ |
| Bypass anti-bot blocks (stealth mode) | ✅ |
| Handle CAPTCHAs automatically | ✅ |
| Remote human handoff when stuck | ✅ |
| Parallel multi-account sessions | ✅ |

---

## How it works

```
browser-act get-skills zai --skill-version 1.0.0   ← runtime workflow (always first)
         │
         ▼
browser-act browser list                         ← find existing browser or create new
         │
         ▼
browser-act --session zai browser open <id> https://chat.z.ai
         │
         ▼
browser-act --session zai state                 ← see indexed interactive elements
         │
         ▼
[login] input email → input password → click submit
         │
         ▼
[model selection] click model selector → click GLM-5.3 → configure toggles
         │
         ▼
[chat] input message → state → get markdown
         │
         ▼
browser-act session close zai
```

---

## Installation

```bash
# Install BrowserAct CLI (once)
uv tool install browser-act-cli --python 3.12

# Verify installation
browser-act --version

# This skill is at ~/.agents/skills/browser-act-zai/SKILL.md
# Your agent loads it automatically when it sees z.ai / chat.z.ai / GLM keywords.
```

---

## Quick login to Z.AI

```bash
# 1. Get the Z.AI skill workflow
browser-act get-skills zai --skill-version 1.0.0

# 2. List available browsers
browser-act browser list

# 3. Open Z.AI in a stealth browser (avoids anti-bot detection)
browser-act browser create \
  --type stealth \
  --name "zai-main" \
  --desc "Z.AI chat session"

# 4. Get the browser ID from the list output, then:
browser-act --session zai browser open <zai-browser-id> https://chat.z.ai

# 5. See what to interact with
browser-act --session zai state

# 6. Login (use indices from `state` output)
browser-act --session zai input 2 "your@email.com"
browser-act --session zai input 3 "your-password"
browser-act --session zai click 4

# 7. After login, select model — click the model selector shown in `state`
browser-act --session zai state
browser-act --session zai click <model-selector-index>

# 8. Send a message
browser-act --session zai input <input-index> "Hello GLM"
browser-act --session zai click <send-index>

# 9. Read the response
browser-act --session zai get markdown

# 10. Close when done
browser-act session close zai
```

---

## Reusing your existing Z.AI login

If you're already logged into Z.AI in Chrome:

```bash
# Import your Chrome profile (keeps your Z.AI session cookies)
browser-act browser list-profiles
browser-act browser import-profile <zai-browser-id> <profile-id>

# Now the browser session has your existing Z.AI session
browser-act --session zai browser open <zai-browser-id> https://chat.z.ai
```

---

## Handling login blocks

If Z.AI shows a CAPTCHA or blocks automated login:

```bash
# Try solving the CAPTCHA first
browser-act --session zai solve-captcha

# If that doesn't work, use remote assist — generates a live link a human opens
browser-act --session zai remote-assist --objective "Complete the Z.AI login at chat.z.ai"

# Agent waits. When the human finishes, the session continues.
```

---

## Multi-account Z.AI in parallel

```bash
# Create two separate stealth browsers
browser-act browser create --type stealth --name "zai-work" --desc "Z.AI work account"
browser-act browser create --type stealth --name "zai-personal" --desc "Z.AI personal account"

# Each browser is fully isolated — different cookies, fingerprints, proxies
browser-act --session zai-work browser open <work-browser-id> https://chat.z.ai
browser-act --session zai-personal browser open <personal-browser-id> https://chat.z.ai

# Run both in parallel — they never interfere with each other
```

---

## Model selection reference

Z.AI's model selector is a dropdown accessible via the `aria-label="Select a model"` element.
After clicking, a menu shows available models. Click the model's button by its label.

| Model | Display name in UI |
|-------|-------------------|
| glm-5.3 | GLM-5.3 |
| glm-5.2 | GLM-5.2 |
| glm-5.3-flash | GLM-5.3-Flash |

Deep Think effort: Low / High / Max — inside the "Deep Think" dropdown menu.
Web Search toggle: globe icon button in the chat bar.
Tools toggle: tools icon button in the chat bar.

Run `browser-act get-skills zai --skill-version 1.0.0` for the current element indices
— Z.AI's UI changes often and the indices in this doc may lag.

---

## Relation to OmniRoute zai-web

OmniRoute already has a `zai-web` executor at:
`open-sse/executors/zai-web/`

That executor uses **raw Playwright** to automate Z.AI's browser UI. This skill
provides the same capability through **BrowserAct**, which adds:

- Stealth mode (avoids anti-bot detection)
- Profile import (reuse real Chrome sessions)
- CAPTCHA solving
- Remote human handoff
- Parallel multi-account isolation

The OmniRoute integration path: swap `browserAutomation.ts` to call
`browser-act` commands instead of raw Playwright, or use this skill as a
pre-flight Z.AI session setup tool.

---

## Files

```
browser-act-zai/
├── SKILL.md   — Entry skill (for agents, follows BrowserAct two-layer format)
└── README.md  — This page (for humans)
```

---

## Links

- **BrowserAct Docs:** https://docs.browseract.com
- **Z.AI:** https://chat.z.ai / https://space-z.ai
- **BrowserAct GitHub:** https://github.com/browser-act/skills
- **OmniRoute zai-web:** `open-sse/executors/zai-web/` (Playwright-based, this skill is the BrowserAct alternative)
