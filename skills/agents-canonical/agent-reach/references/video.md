# Video / Podcast Transcripts

## YouTube (yt-dlp)

### Video metadata

```bash
yt-dlp --dump-json "URL"
```

### Subtitles (download only, no video)

```bash
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"
cat /tmp/VIDEO_ID.*.vtt
```

### Comments (best-effort)

```bash
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
```

### Search YouTube

```bash
yt-dlp --dump-json "ytsearch5:query"
```

### YouTube Subtitle Retry Chain

1. First try: `yt-dlp --write-sub --write-auto-sub` (above)
2. If bot-check/empty subs, and OpenCLI is connected:
   `opencli youtube transcript "URL" -f yaml`
3. If OpenCLI returns "Caption URL returned empty response" → retry up to 3×
   (expiring subtitle URL, not "no subtitles")
4. Still failing or genuinely no subs → `agent-reach transcribe "URL"` (Whisper audio transcription)

**Success = non-empty subtitle/transcript content**, not exit code or doctor version probe.

### Whisper Fallback (no subtitles)

```bash
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

> Requires Groq or OpenAI key: `agent-reach configure groq-key` (free at console.groq.com)

---

## Bilibili (bili-cli primary, OpenCLI for subtitles)

> **NEVER use yt-dlp for Bilibili** — fully 412-blocked. yt-dlp is for YouTube only.

### Search + video detail (no login needed)

```bash
bili search "query" --type video -n 5
bili hot -n 10
bili rank -n 10
bili video BVxxx
```

### Subtitles (OpenCLI, desktop Chrome)

```bash
opencli bilibili subtitle BVxxx
```

### Audio for transcription (when no subtitles)

```bash
bili audio BVxxx
```

### Zero-config fallback: direct search API

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

---

## Xiaoyuzhou Podcast (transcribe.sh)

```bash
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

### Prerequisites

1. `brew install ffmpeg`
2. Free Groq API key: `agent-reach configure groq-key`
3. `agent-reach install --env=auto --system --channels=xiaoyuzhou`

> `--polish` adds Llama 3.3 70B punctuation/paragraphing pass (~7s extra for 9 min podcast).

---

## Decision

| Scenario | Tool |
|---|---|
| YouTube subtitles | yt-dlp → OpenCLI (×3 retries) → agent-reach transcribe |
| Bilibili video/search | bili-cli |
| Bilibili subtitles | opencli bilibili subtitle |
| Podcast transcription | xiaoyuzhou transcribe.sh |
| Audio without subs | agent-reach transcribe (Bilibili: bili audio first) |
