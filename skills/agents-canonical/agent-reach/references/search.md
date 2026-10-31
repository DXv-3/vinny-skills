# Search — Exa AI

## Exa AI Search (via mcporter)

High-quality AI search engine — good for technical docs, official examples, and related web pages.

```bash
# Install if missing:
# npm install -g mcporter
# mcporter config add exa https://mcp.exa.ai/mcp --scope home

mcporter call exa.web_search_exa query="query" numResults=5
mcporter call exa.web_search_exa query="framework API example" numResults=5
```

### Use Cases

| Scenario | Parameters |
|---|---|
| Web search | `web_search_exa(query: "...", numResults: 5)` |
| Tech/code docs | `web_search_exa(query: "framework name API example", numResults: 5)` |

> `get_code_context_exa` is deprecated. Use `web_search_exa` for code questions;
> for precise repo content searches, use GitHub search in dev.md instead.

## Comparison

| Tool | Source | Best for |
|---|---|---|
| Exa | agent-reach | English/tech/code search |
| GitHub search | agent-reach (dev.md) | Repos/code search |
