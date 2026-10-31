---
name: web-guest-manners
description: Use BEFORE any browser agent browses, fills forms, or scrapes any website. Front-door check first, own browser profile, human pacing, hard stops at CAPTCHAs and block pages, no disguise kits, logged visits. Makes agents reliable guests that don't get blocked, banned, or flagged — readiness, not invisibility.
---

# Web Guest Manners — how every browser agent behaves on other people's sites

One sentence: be the guest a site can't reasonably object to — real browser, polite pace,
stop when unwelcome — because sites now block agents by default, and a disguised agent
that gets caught looks like an attacker.

## Before you go (mandatory, in order)

1. **Front door first.** Check `~/Projects/WEB-GUEST-SITELIST.md` for the target site.
   API/RSS/export listed → use that instead of the browser. Automation = NO → stop, tell
   Vinny. Site not listed → don't guess: do one read-only look (fetch the page once, read
   robots.txt), then ask Vinny to mark the row.
2. **Own profile.** Never run an agent in Vinny's personal Chrome profile. One profile
   per agent, so no agent reads his logins or another agent's session:
   - browser-use / Playwright / Chrome flag: `--user-data-dir=$HOME/.agent-profiles/<agent-name>`
3. **Stay honest.** Never fake a human identity. The browser's real fingerprint stays as-is.

## While you're there

- **Pace like a human:** 2–5 randomized seconds between page loads, one page at a time
  per site, never parallel-hammer one host.
- **Respect the ropes:** robots.txt `Disallow` = no. Login walls and paywalls are
  boundaries, not puzzles.
- **Take only what the task needs.** No bulk vacuuming "while we're here."

## Hard stops (never cross, never retry around)

| Wall | Action |
|---|---|
| CAPTCHA / "verify you're human" | STOP. Save the URL and where you were. Hand to Vinny. NEVER auto-solve. |
| Login required | Stop — unless the sitelist row marks an account as approved for this task. |
| 403 / block page / "unusual traffic" | That is the site's answer. Log it, leave, done. NEVER rotate IPs or proxies to get back in. |
| robots.txt Disallow | Don't fetch that path. |

## Never install (the disguise kit)

Fingerprint spoofers · CAPTCHA solvers · residential-proxy rotators · User-Agent fakers.
This skill makes agents GOOD GUESTS, not hidden ones. A blocked agent is the system
working, not failing.

## Readiness self-check (once per agent setup, ~60 seconds)

Drive the agent's browser to `https://bot.sannysoft.com/` and compare against Vinny's
own Chrome:
- Goal: the setup behaves like a normal real Chrome (QA that the config is sound —
  not evasion tuning).
- A red row from an automation flag (e.g. `navigator.webdriver`) → fix by using the
  real-browser driver setup, never by patching flags over it.

## After every session

Append one line to the visit log in `~/Projects/WEB-GUEST-SITELIST.md`:
date · site · pages hit · walls hit · outcome. No log line = the session didn't happen.

## Background mode (windows bothering Vinny)

Visible real Chrome is the default — most reliable, fewest false blocks. Headless is
allowed only for background runs where a block wouldn't matter; headless raises
detection odds, and that trade is stated, not hidden.
