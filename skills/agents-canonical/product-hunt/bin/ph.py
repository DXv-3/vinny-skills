#!/usr/bin/env python3
"""ph.py — Product Hunt v2 parts engine (stdlib only).

Browse launches, topics, and leaderboards through Product Hunt's GraphQL API,
framed for the parts-stealing workflow: what it does, the mechanism worth
stealing, traction signals, who built it, where it runs live.

Honest limits baked in:
  - The v2 API has NO text search on posts. The only keyword search is
    topics(query:). So "find launches for idea X" goes: topics X → launches
    in that topic → post detail. Never invent a posts(search:) argument.
  - Auth is an API Key + API Secret pair exchanged via OAuth client_credentials
    in-memory per run. Nothing is stored, printed, or logged.

Usage:
  ph.py hunt "ai video editors" [-n 5]   # one shot: idea → best topic → top launches
  ph.py topics "ai agents" [-n 10]
  ph.py launches --topic ai-agents [-n 10] [--order VOTES|NEWEST]
  ph.py leaderboard [--date 2026-09-14] [-n 10]
  ph.py post <slug-or-id> [--comments 3]
  ph.py auth            # verify credentials, prints OK/FAIL only
  ph.py save            # remember key+secret (0600 file, with your explicit OK)
  ph.py forget          # delete the saved credentials
  Global: --token T | --client-id ID --client-secret S | env PH_TOKEN,
          PH_CLIENT_ID, PH_CLIENT_SECRET.  --json for machine output
          (also accepted after the subcommand).
"""

import argparse
import datetime
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request

API = "https://api.producthunt.com"
TOKEN_URL = API + "/v2/oauth/token"
GRAPHQL = API + "/v2/api/graphql"
TIMEOUT = 30
CRED_PATH = os.path.expanduser("~/.config/product-hunt/credentials")

Q_TOPICS = """
query($query: String!, $first: Int) {
  topics(query: $query, first: $first) {
    edges { node { id name slug description followersCount postsCount } }
  }
}"""

Q_POSTS = """
query($first: Int, $after: String, $topic: String, $order: PostsOrder,
      $postedAfter: DateTime, $postedBefore: DateTime, $featured: Boolean) {
  posts(first: $first, after: $after, topic: $topic, order: $order,
        postedAfter: $postedAfter, postedBefore: $postedBefore, featured: $featured) {
    totalCount
    pageInfo { endCursor hasNextPage }
    edges { node {
      id name tagline slug description votesCount commentsCount
      website url createdAt
      thumbnail { url }
      makers { name username }
      topics { edges { node { name slug } } }
    } }
  }
}"""

Q_POSTS_LEAN = """
query($first: Int, $after: String, $topic: String, $order: PostsOrder,
      $postedAfter: DateTime, $postedBefore: DateTime, $featured: Boolean) {
  posts(first: $first, after: $after, topic: $topic, order: $order,
        postedAfter: $postedAfter, postedBefore: $postedBefore, featured: $featured) {
    totalCount
    pageInfo { endCursor hasNextPage }
    edges { node {
      id name tagline slug votesCount commentsCount url createdAt
    } }
  }
}"""

Q_POST = """
query($id: ID, $slug: String, $nComments: Int) {
  post(id: $id, slug: $slug) {
    id name tagline slug description votesCount commentsCount
    website url createdAt
    thumbnail { url }
    makers { name username headline }
    topics { edges { node { name slug } } }
    comments(first: $nComments) {
      edges { node { body votesCount user { name username } } }
    }
  }
}"""


class PHError(Exception):
    pass


def _http_json(url, payload, headers):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise PHError("auth rejected (401) — check key/secret or token; nothing was printed")
        if e.code == 429:
            raise PHError("rate limited (429) — Product Hunt uses complexity limits; wait and retry leaner")
        try:
            detail = e.read().decode()[:200]
        except Exception:
            detail = ""
        raise PHError("HTTP %s from %s %s" % (e.code, url, detail))


def load_saved():
    """Key+secret the user explicitly approved saving (0600 file)."""
    try:
        with open(CRED_PATH) as f:
            d = json.load(f)
        return d.get("client_id"), d.get("client_secret")
    except (OSError, ValueError):
        return None, None


def resolve_token(args):
    """Direct developer token wins; otherwise exchange key+secret in-memory."""
    token = args.token or os.environ.get("PH_TOKEN")
    if token:
        return token.strip()
    cid = args.client_id or os.environ.get("PH_CLIENT_ID")
    csec = args.client_secret or os.environ.get("PH_CLIENT_SECRET")
    if not (cid and csec):
        cid, csec = load_saved()
    if not (cid and csec):
        raise PHError(
            "no credentials: pass --token, set PH_TOKEN / PH_CLIENT_ID+PH_CLIENT_SECRET, "
            "or run `ph.py save` once to remember them (0600 file, `ph.py forget` removes)")
    data = _http_json(TOKEN_URL, {
        "client_id": cid, "client_secret": csec, "grant_type": "client_credentials",
    }, {"Content-Type": "application/json", "Accept": "application/json"})
    tok = data.get("access_token")
    if not tok:
        raise PHError("token exchange failed: %s" % str(data)[:200])
    return tok


def gql(token, query, variables):
    data = _http_json(GRAPHQL, {"query": query, "variables": variables},
                      {"Content-Type": "application/json",
                       "Accept": "application/json",
                       "Authorization": "Bearer " + token})
    errs = data.get("errors")
    if errs:
        raise PHError("GraphQL error: %s" % str(errs[0].get("message", errs[0]))[:300])
    return data.get("data") or {}


def edges(data, *path):
    node = data
    for p in path:
        node = (node or {}).get(p, {})
    return [e["node"] for e in (node.get("edges") or []) if e.get("node")]


def fmt_date(iso):
    try:
        return iso[:10]
    except Exception:
        return "?"


def fmt_num(n):
    try:
        return "{:,}".format(int(n))
    except Exception:
        return "?"


def render_topic(t):
    d = textwrap.shorten((t.get("description") or "").strip().replace("\n", " "),
                         width=160, placeholder="…")
    return ("• %(name)s  (slug: %(slug)s)\n"
            "  %(desc)s\n"
            "  %(posts)s launches · %(fol)s followers" % {
                "name": t.get("name"), "slug": t.get("slug"), "desc": d or "—",
                "posts": fmt_num(t.get("postsCount")), "fol": fmt_num(t.get("followersCount"))})


def render_launch(p):
    makers = ", ".join("@%s" % m.get("username") for m in (p.get("makers") or [])
                       if m.get("username")) or "—"
    topics = ", ".join(t.get("slug") for t in edges(p, "topics") if t.get("slug"))
    what = textwrap.shorten((p.get("description") or p.get("tagline") or "").strip()
                            .replace("\n", " "), width=240, placeholder="…")
    lines = [
        "◆ %s — %s" % (p.get("name"), p.get("tagline") or ""),
        "  What it does: %s" % (what or "—"),
        "  Traction: %s votes · %s comments · launched %s" % (
            fmt_num(p.get("votesCount")), fmt_num(p.get("commentsCount")),
            fmt_date(p.get("createdAt"))),
        "  Who: %s" % makers,
        "  Live: %s" % (p.get("url") or "—"),
    ]
    if p.get("website"):
        lines.append("  Site: %s" % p.get("website"))
    if topics:
        lines.append("  Filed under: %s" % topics)
    return "\n".join(lines)


def render_post(p, n_comments):
    out = [render_launch(p)]
    desc = (p.get("description") or "").strip()
    if desc and len(desc) > 260:
        out.append("")
        out.append("  Full pitch:")
        for para in textwrap.wrap(desc, width=86, initial_indent="    ",
                                  subsequent_indent="    "):
            out.append(para)
    comments = edges({"comments": p.get("comments")}, "comments")
    if comments:
        out.append("")
        out.append("  Crowd says (top %d):" % len(comments))
        for c in comments[:n_comments]:
            who = (c.get("user") or {}).get("username") or "?"
            body = re.sub(r"<[^>]+>", " ", c.get("body") or "").strip()
            body = re.sub(r"\s+", " ", body)
            body = textwrap.shorten(body, width=180, placeholder="…")
            out.append("    @%s (%s↑): %s" % (who, fmt_num(c.get("votesCount")), body))
    return "\n".join(out)


def cmd_topics(args, token):
    data = gql(token, Q_TOPICS, {"query": args.query, "first": args.n})
    items = edges(data, "topics")
    if args.json:
        return {"ok": True, "items": items}
    if not items:
        return "no topics match %r — try a broader keyword" % args.query
    return "\n\n".join(render_topic(t) for t in items)


def cmd_launches(args, token):
    order = (args.order or "VOTES").upper()
    if order not in ("VOTES", "NEWEST"):
        raise PHError("--order must be VOTES or NEWEST")
    variables = {"first": args.n, "topic": args.topic, "order": order,
                 "featured": args.featured or None}
    if args.after:
        variables["postedAfter"] = args.after
    if args.before:
        variables["postedBefore"] = args.before
    q = Q_POSTS_LEAN if args.lean else Q_POSTS
    items, total, after = [], None, None
    while len(items) < args.n:
        variables["first"] = min(args.n - len(items), 20)
        variables["after"] = after
        data = gql(token, q, variables)
        conn = data.get("posts") or {}
        if total is None:
            total = conn.get("totalCount")
        items += edges(data, "posts")
        page = conn.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        after = page.get("endCursor")
    if args.json:
        return {"ok": True, "totalCount": total, "items": items}
    if not items:
        return "no launches found — check the topic slug via `topics`"
    head = "top %d of %s launches" % (len(items), fmt_num(total))
    return head + "\n\n" + "\n\n".join(render_launch(p) for p in items)


def cmd_leaderboard(args, token):
    day = args.date or datetime.date.today().isoformat()
    try:
        datetime.datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        raise PHError("--date must be YYYY-MM-DD")
    variables = {"first": args.n, "order": "VOTES", "featured": True,
                 "postedAfter": day + "T00:00:00Z",
                 "postedBefore": day + "T23:59:59Z"}
    data = gql(token, Q_POSTS_LEAN if args.lean else Q_POSTS, variables)
    items = edges(data, "posts")
    if args.json:
        return {"ok": True, "date": day, "items": items}
    if not items:
        return "nothing on the leaderboard for %s" % day
    return "leaderboard · %s\n\n" % day + "\n\n".join(render_launch(p) for p in items)


def cmd_post(args, token):
    ref = args.ref
    variables = {"id": ref if ref.isdigit() else None,
                 "slug": None if ref.isdigit() else ref,
                 "nComments": args.comments}
    data = gql(token, Q_POST, variables)
    p = data.get("post")
    if not p:
        raise PHError("no launch found for %r" % ref)
    if args.json:
        return {"ok": True, "post": p}
    return render_post(p, args.comments)


def cmd_auth(args, token):
    data = gql(token, Q_TOPICS, {"query": "ai", "first": 1})
    n = len(edges(data, "topics"))
    return "auth OK — API answered (topics probe returned %d row%s)" % (n, "" if n == 1 else "s")


def cmd_save(args):
    cid = args.client_id or os.environ.get("PH_CLIENT_ID")
    csec = args.client_secret or os.environ.get("PH_CLIENT_SECRET")
    if not (cid and csec):
        raise PHError("nothing to save: set PH_CLIENT_ID and PH_CLIENT_SECRET first")
    os.makedirs(os.path.dirname(CRED_PATH), exist_ok=True)
    if os.path.exists(CRED_PATH) and not args.force:
        raise PHError("credentials already saved — `ph.py forget` first, or save --force")
    fd = os.open(CRED_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"client_id": cid, "client_secret": csec}, f)
    return "saved to %s (mode 600, never printed). `ph.py forget` removes it." % CRED_PATH


def cmd_forget(args):
    try:
        os.remove(CRED_PATH)
        return "forgotten — saved credentials removed."
    except FileNotFoundError:
        return "nothing saved."


def cmd_hunt(args, token):
    """One shot: idea → best topic → top launches. The easy button."""
    tdata = gql(token, Q_TOPICS, {"query": args.idea, "first": 5})
    topics = edges(tdata, "topics")
    if not topics:
        raise PHError("no topics match %r — try a broader keyword" % args.idea)
    topic = topics[0]
    ldata = gql(token, Q_POSTS_LEAN if args.lean else Q_POSTS,
                  {"first": args.n, "topic": topic["slug"], "order": "VOTES"})
    items = edges(ldata, "posts")
    if args.json:
        return {"ok": True, "topic": topic, "alt_topics": topics[1:], "items": items}
    head = ("idea %r → topic: %s (%s launches)" % (
        args.idea, topic["name"], fmt_num(topic.get("postsCount"))))
    if len(topics) > 1:
        alts = ", ".join("%s (%s)" % (t["name"], t["slug"]) for t in topics[1:3])
        head += "\n  also matched: %s" % alts
    if not items:
        return head + "\n\nno launches found in %s" % topic["slug"]
    return head + "\n\n" + "\n\n".join(render_launch(p) for p in items)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ph.py",
                                 description="Product Hunt v2 parts engine (stdlib only)")
    ap.add_argument("--token", help="developer bearer token (or PH_TOKEN)")
    ap.add_argument("--client-id", help="API key (or PH_CLIENT_ID)")
    ap.add_argument("--client-secret", help="API secret (or PH_CLIENT_SECRET)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    # --json also accepted after the subcommand (people type it there)
    outp = argparse.ArgumentParser(add_help=False)
    outp.add_argument("--json", action="store_true", help="machine-readable output")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("topics", parents=[outp], help="keyword → topics (the only real keyword search)")
    s.add_argument("query")
    s.add_argument("-n", type=int, default=10)

    s = sub.add_parser("launches", parents=[outp], help="launches inside a topic")
    s.add_argument("--topic", required=False, default=None,
                     help="topic slug (from `topics`); omit for all launches")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--order", default="VOTES")
    s.add_argument("--after", help="postedAfter, e.g. 2026-01-01T00:00:00Z")
    s.add_argument("--before", help="postedBefore")
    s.add_argument("--featured", action="store_true")
    s.add_argument("--lean", action="store_true",
                     help="minimal fields (for large -n; avoids complexity limits)")

    s = sub.add_parser("leaderboard", parents=[outp], help="what's hot on a day (default: today)")
    s.add_argument("--date", help="YYYY-MM-DD")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--lean", action="store_true",
                     help="minimal fields (for large -n; avoids complexity limits)")

    s = sub.add_parser("post", parents=[outp], help="full teardown of one launch")
    s.add_argument("ref", help="slug or numeric id")
    s.add_argument("--comments", type=int, default=3)

    s = sub.add_parser("auth", parents=[outp], help="verify credentials (prints OK/FAIL only)")

    s = sub.add_parser("hunt", parents=[outp],
                       help="one shot: idea → best topic → top launches")
    s.add_argument("idea")
    s.add_argument("-n", type=int, default=5)
    s.add_argument("--lean", action="store_true",
                     help="minimal fields (for large -n; avoids complexity limits)")

    s = sub.add_parser("save", help="remember key+secret in a 0600 file (needs your OK)")
    s.add_argument("--force", action="store_true")

    s = sub.add_parser("forget", help="delete the saved credentials")

    args = ap.parse_args(argv)
    try:
        if args.cmd in ("save", "forget"):
            fn = {"save": cmd_save, "forget": cmd_forget}[args.cmd]
            result = fn(args)
        else:
            token = resolve_token(args)
            fn = {"topics": cmd_topics, "launches": cmd_launches,
                  "leaderboard": cmd_leaderboard, "post": cmd_post,
                  "auth": cmd_auth, "hunt": cmd_hunt}[args.cmd]
            result = fn(args, token)
    except PHError as e:
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
        else:
            print("error: %s" % e, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result if isinstance(result, dict) else
                         {"ok": True, "output": result}, indent=2, default=str))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
