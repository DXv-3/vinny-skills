# Career — LinkedIn

## LinkedIn (mcp-server-linkedin via mcporter)

### Profile, talent, company, jobs

```bash
# Install:
# brew install uv  (provides uvx)
# mcporter config add linkedin --command uvx --arg mcp-server-linkedin@latest --env UV_HTTP_TIMEOUT=300 --scope home

# First login (needs browser):
# uvx mcp-server-linkedin@latest --login

# Profile
mcporter call linkedin.get_person_profile linkedin_username="username" sections="experience,education"

# Search people
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"

# Company
mcporter call linkedin.get_company_profile company_name="openai" sections="posts,jobs"

# Jobs
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote" max_pages=2
```

## Fallback: Jina Reader (public pages only)

```bash
curl -s "https://r.jina.ai/https://linkedin.com/in/username"
```

> Full profiles, companies, and job search require the MCP server. Jina only reads
> public page content.
