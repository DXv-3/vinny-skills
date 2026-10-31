# Social Media & Communities

XiaoHongShu, Twitter/X, Bilibili, V2EX, Reddit, Facebook, Instagram.

---

## XiaoHongShu (multi-backend)

**Always check `agent-reach doctor --json` first** — run `active_backend` for xiaohongshu to know which backend to use.

### Backend A: OpenCLI (desktop preferred)

```bash
opencli xiaohongshu search "query" -f yaml
opencli xiaohongshu note "NOTE_URL" -f yaml    # need full URL with xsec_token from search
opencli xiaohongshu comments NOTE_ID -f yaml
opencli xiaohongshu feed -f yaml
opencli xiaohongshu user USER_ID -f yaml
```

> Requires Chrome open with OpenCLI extension. OpenCLI only uses an existing
> user-controlled Chrome session — Agent Reach never auto-logs in or reads cookies.
> If no session exists, use Backend B/C with manual Cookie-Editor export.

### Backend B: xiaohongshu-mcp (server scenario)

```bash
agent-reach configure xhs-cookies          # manual Cookie-Editor import first
mcporter call xiaohongshu.check_login_status --timeout 120000
mcporter call xiaohongshu.search_feeds keyword="query" --timeout 120000
mcporter call xiaohongshu.get_feed_detail feed_id="..." xsec_token="..." --timeout 120000
```

> First call auto-downloads ~150MB headless browser — always use `--timeout 120000`.

### Backend C: xhs-cli (legacy, upstream unmaintained since 2026-03)

```bash
xhs search "query"
xhs read NOTE_ID_OR_URL     # must use URL from search results, not bare note_id
xhs comments NOTE_ID_OR_URL
xhs hot
xhs feed
```

### XHS Rules

- **xsec_token required**: never read with bare note_id — always search/feed first to get full URL/ID.
- **Rate limit**: 2-3 second gap between requests; high-frequency = captcha.
- **Write ops**: read-only recommended. xhs-cli v0.6.x writes may return 406.

---

## Twitter/X (twitter-cli)

### Auth

`agent-reach configure twitter-cookies` saves cookies for `doctor` checks only.
Before running any `twitter` command, explicitly set env vars in the same shell:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

### Stable Commands

```bash
twitter feed -n 20               # home timeline (most stable)
twitter tweet URL_OR_ID          # read single tweet + replies
twitter article URL_OR_ID        # read long-form X Article
twitter user-posts @username -n 20
twitter user @username
```

### Unstable Commands

```bash
twitter search "query" -n 10     # may 404 if Twitter changes GraphQL endpoints
twitter likes                    # 2024+ only shows own likes (platform limit)
```

### Twitter Search Retry Chain

1. Retry once: `twitter search "query" -n 10`
2. Upgrade then retry: `pipx upgrade twitter-cli && twitter search "query" -n 10`
3. Fallback to OpenCLI: `opencli twitter search "query" -f yaml`
4. All fail → use `twitter feed` or `twitter user-posts @somebody` to work around

### Twitter Notes

- **IP risk**: don't call from VPS/datacenter IPs frequently, especially followers/following — ban risk. Use residential proxy or local environment.
- **Output**: prefer `--yaml` or `--json` for structured output (friendlier for AI agents).

---

## Bilibili (bili-cli primary, OpenCLI for subtitles)

> **NEVER use yt-dlp for Bilibili** — fully 412-blocked by Bilibili (verified June 2026). yt-dlp is for YouTube only.

```bash
# bili-cli (search + detail, no login needed)
bili search "query" --type video -n 5
bili hot -n 10
bili rank -n 10
bili video BVxxx

# Subtitles (OpenCLI, desktop Chrome required)
opencli bilibili subtitle BVxxx
```

---

## V2EX (public API, no auth)

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

---

## Reddit (multi-backend, login mandatory)

Reddit has **no zero-config path** — anonymous `.json` endpoints blocked (403), official API gated. Both backends require login.

### Backend A: OpenCLI (desktop preferred)

```bash
opencli reddit search "query" -f yaml
opencli reddit read POST_ID -f yaml
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml
```

> Requires Chrome open and logged into reddit.com.

### Backend B: rdt-cli (server/legacy)

```bash
pipx install 'git+https://github.com/public-clis/rdt-cli.git'
rdt login
rdt search "query" --limit 10
rdt read POST_ID
```

---

## Facebook (OpenCLI, login mandatory)

```bash
opencli facebook search "query" -f yaml
opencli facebook profile zuck -f yaml
opencli facebook feed --limit 10 -f yaml
opencli facebook groups --limit 20 -f yaml
```

> Desktop only. Requires Chrome logged into facebook.com. Groups only shows
> visible groups/recent activity for current account — not arbitrary group posts.

---

## Instagram (OpenCLI, login mandatory)

```bash
opencli instagram search "query" -f yaml     # user search (not keyword post search)
opencli instagram profile nasa -f yaml
opencli instagram user nasa --limit 12 -f yaml   # recent posts
opencli instagram explore --limit 20 -f yaml
opencli instagram saved --limit 20 -f yaml
```

> Desktop only. Requires Chrome logged into instagram.com. If 429/login error,
> have user re-login in Chrome and lower request frequency.
