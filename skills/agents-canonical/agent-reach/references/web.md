# Web Pages / Articles / RSS

## Jina Reader (any URL → clean Markdown)

```bash
curl -s "https://r.jina.ai/https://example.com/article"
```

**When**: most web pages — fast, free, no API key.

## Web Reader MCP (format control)

```bash
mcporter call web-reader.webReader url="https://example.com"
mcporter call web-reader.webReader url="https://example.com" retain_images=true
mcporter call web-reader.webReader url="https://example.com" return_format="text"
```

**When**: need image retention or text-only output.

## RSS (feedparser)

```bash
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

**When**: blogs, news feeds, podcast RSS.

## Decision

| Scenario | Tool |
|---|---|
| Generic web page | Jina Reader (`curl r.jina.ai`) |
| Need images/format control | web-reader MCP |
| RSS subscription | feedparser |
