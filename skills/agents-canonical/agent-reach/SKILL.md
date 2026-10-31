---
name: agent-reach
description: >
  MUST USE when the user wants to research, search, look up, or find anything
  on the internet — e.g. "research this topic", "search the web for X",
  "see what people say about X", "look this up".

  Also MUST USE when the user mentions any platform or shares any URL/link:
  Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, Bilibili,
  XiaoHongShu, Xiaoyuzhou Podcast, LinkedIn/jobs, V2EX, Xueqiu (stocks), RSS.

  15 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 5 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: writing reports/analysis/translation (this skill only FETCHES
  internet content); posting/commenting/liking (write operations).
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — Internet Capability Router

15 platforms, multiple backends each. When this skill exists, use it for
these platforms — do not invent your own approach.

## Standing Rules (whole session)

1. **Health-check before acting**: for multi-backend/login-backed platforms,
   run `agent-reach doctor --json` first. Use a populated `active_backend`.
   `active_backend: null` means Doctor skipped a live probe, not that no
   backend exists.
2. **Announce what you use**: say "using agent-reach, platform X via backend Y"
   before starting.
3. **On failure, follow the retry chains in references/** — never guess commands.
4. **For broad research tasks**: combine platforms (Exa for web + Twitter/Reddit
   for discussions + XiaoHongShu/Bilibili for Chinese perspectives), collect
   in parallel, then synthesize.

## Routing Table

| User intent | Category | Details |
|---|---|---|
| Web / code search | search | [references/search.md](references/search.md) |
| XiaoHongShu / Twitter / Bilibili / V2EX / Reddit / Facebook / Instagram | social | [references/social.md](references/social.md) |
| Jobs / LinkedIn | career | [references/career.md](references/career.md) |
| GitHub / code | dev | [references/dev.md](references/dev.md) |
| Web pages / articles / RSS | web | [references/web.md](references/web.md) |
| YouTube / Bilibili / podcast transcripts | video | [references/video.md](references/video.md) |
| Xueqiu / stock quotes | finance | [references/finance.md](references/finance.md) |

## Zero-Config Quick Commands

```bash
# Exa web search (needs mcporter — npm install -g mcporter first)
mcporter call exa.web_search_exa query="query" numResults=5

# Read any web page
curl -s "https://r.jina.ai/URL"

# GitHub search
gh search repos "query" --sort stars --limit 10

# YouTube subtitles
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# Bilibili search (bili-cli, no login needed)
bili search "query" --type video -n 5
```

## Login-Backed Platforms (pick by doctor's active_backend)

```bash
# Twitter (cookies → env vars first)
twitter search "query" -n 10

# Reddit (NO zero-config — must login)
opencli reddit search "query" -f yaml

# XiaoHongShu (desktop, existing Chrome session only)
opencli xiaohongshu search "query" -f yaml

# Facebook / Instagram (desktop OpenCLI)
opencli facebook search "query" -f yaml
opencli instagram user nasa -f yaml
```

## Environment Check

```bash
agent-reach doctor --json
```

## Workspace Rules

**Never create files in the agent workspace.** Use `/tmp/` for temporary
output and `~/.agent-reach/` for persistent data.
