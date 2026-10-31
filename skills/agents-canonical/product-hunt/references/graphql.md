# Product Hunt v2 GraphQL — working notes

Verified 2026-09-14 against the live schema via third-party introspection
reports (the API's own explorer + schema.graphql on GitHub). No live call was
made against the user's account, so re-verify with `ph.py auth` after setup.

## Endpoints

- Token: `POST https://api.producthunt.com/v2/oauth/token`
  body `{"client_id": KEY, "client_secret": SECRET, "grant_type": "client_credentials"}`
  → `{"access_token": "...", "token_type": "Bearer", "scope": "public", ...}`
- GraphQL: `POST https://api.producthunt.com/v2/api/graphql`
  header `Authorization: Bearer <access_token>`

## The one hard rule

**`posts` has no text search.** Schema-verified args only:
`(featured, postedBefore, postedAfter, topic, order, twitterUrl, url, after, before, first, last)`.
There is no `query:`/`search:` argument — asking for it fails every call.
The only keyword-searchable field in v2 is `topics(query:)`.

So the "idea → launches" path is always: keyword → `topics` → pick a slug →
`posts(topic:)` ordered by VOTES. There is no shortcut. Do not invent one.

## Orders

`PostsOrder`: `VOTES`, `NEWEST`, `RANKING`. Default `VOTES`.

## Data-quality caveats

- Nested user stats are unreliable: follower/following counts return 0 and
  some user fields come back `[REDACTED]`. Treat makers as handles, not metrics.
- Counts on user objects (made/submitted/voted) cap at 20.
- Client-credentials tokens are read-only, public scope. User-specific fields
  (`isVoted`, `viewer`, …) return defaults.
- Complexity-based rate limiting: keep queries lean; the CLI requests only the
  fields it prints.

## Developer token (optional)

Product Hunt also issues long-lived developer tokens (`phc_…`) via the API
dashboard. If the user has one, `ph.py` accepts it as `--token`/`PH_TOKEN` and
skips the OAuth exchange entirely.
