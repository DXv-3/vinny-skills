---
name: site-teardown
description: "Deep technical teardown of any website: what it does, its tech stack and hosting, how it works under the hood (APIs, client vs server logic), and the business behind it. Trigger on 'tear down this site', 'deep scan this site', 'what is this site built on', or 'how does this site work'."
---

# Site Teardown

## Purpose
Reverse-engineer a website into a plain-English technical teardown: the product flow, the stack it runs on, how it works under the hood, and the business behind it.

## Workflow
1. Get the URL. Fetch the homepage with `browser.open` for the rendered surface and note what the site claims to do.
2. Fan out the recon. Delegate the deep dive to a subagent (farming work out is the standing move); the main agent orchestrates and presents.
   - **Product**: walk the flow a real user takes — entry point, inputs, outputs, how results are presented, every subpage and route.
   - **Tech stack**: page source / JS bundle analysis, framework fingerprints, response headers, cookies, analytics/tracking, DNS records, TLS cert issuer, hosting/CDN detection. Note anything whose state the evidence forces (e.g. rendered-pixel measurements or console-error capture prove a server-side headless browser, not client-side JS).
   - **Inner workings**: likely API endpoints (`/api/*` in bundles, observable network calls), client-side vs server-side logic, robots.txt, sitemap.xml, auth requirements, rate limits.
   - **Business**: pricing (free/paid), about page, footer, contact info, WHOIS/domain registrar, GitHub or open-source traces, maker info via `browser.search`.
   - **Verdict**: notable implementation choices, strengths, gaps, and how accurate the site's claims are.
3. Hand over the teardown in chat, short and scannable. Offer a fuller write-up only if asked.

## Output Contract
A structured rundown: what it is, how the flow works, what's under the hood (stack, hosting, APIs), the business model, and notable findings. Concrete details (bundle names, endpoints, headers, registrar) over guesses — label anything uncertain as uncertain.

## Operating Rules
1. Public surface only: never sign in, create accounts, submit forms, or bypass access controls.
2. Verify, don't guess: cite bundle names, headers, and endpoints actually found.
3. A thin rendered page is a signal, not a result — JS-driven sites need bundle and route digging.
4. Keep replies short; the teardown goes in chat, not a slide deck, unless the user asks.
