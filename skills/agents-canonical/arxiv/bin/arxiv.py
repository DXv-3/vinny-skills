#!/usr/bin/env python3
"""arxiv.py -- thin CLI for the keyless arXiv query API (Atom XML -> JSON).

The public API needs no key, so there is no credential and nothing in the
Secure Vault. Pure stdlib: runs on my VM and on the Mac dispatcher alike.

Usage:
    arxiv.py search <query> [--field all|ti|au|abs|co|jr|cat]
                             [--sort relevance|lastUpdatedDate|submittedDate]
                             [--order ascending|descending]
                             [--start N] [--max N]
    arxiv.py get <arxiv-id>[,<arxiv-id>...]
    arxiv.py raw <path-with-query>     # pass the Atom XML through untouched

Prints one JSON array to stdout. Each entry:
    id, title, authors[], published, updated, summary,
    categories[], primary_category, abs_url, pdf_url

Be kind: arXiv asks for a modest pace (one request every ~3s); this script
does not throttle, so batch calls yourself.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://export.arxiv.org/api/query"
HOSTS = ["export.arxiv.org"]
UA = "muse-connector/arxiv (personal assistant; mailto:vinnygilberti@gmail.com)"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def _text(el, tag):
    node = el.find(tag, NS)
    return node.text.strip().replace("\n", " ") if node is not None and node.text else ""


def _entry_to_dict(entry):
    abs_id = _text(entry, "atom:id")
    links = {}
    for link in entry.findall("atom:link", NS):
        links[link.get("title") or link.get("rel") or ""] = link.get("href", "")
    authors = [
        _text(a, "atom:name") for a in entry.findall("atom:author", NS)
        if _text(a, "atom:name")
    ]
    return {
        "id": abs_id.rsplit("/", 1)[-1],
        "title": _text(entry, "atom:title"),
        "authors": authors,
        "published": _text(entry, "atom:published"),
        "updated": _text(entry, "atom:updated"),
        "summary": _text(entry, "atom:summary"),
        "categories": [
            c.get("term", "") for c in entry.findall("atom:category", NS)
        ],
        "primary_category": (
            entry.find("arxiv:primary_category", NS).get("term", "")
            if entry.find("arxiv:primary_category", NS) is not None else ""
        ),
        "abs_url": abs_id,
        "pdf_url": links.get("pdf", abs_id.replace("/abs/", "/pdf/") + ".pdf"),
    }


def call(query_params):
    qs = urllib.parse.urlencode(query_params)
    req = urllib.request.Request(BASE + "?" + qs)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/atom+xml")
    with urllib.request.urlopen(req, timeout=60) as resp:
        feed = ET.fromstring(resp.read())
    return [_entry_to_dict(e) for e in feed.findall("atom:entry", NS)]


def cmd_search(args):
    # arxiv.py search <query> [--field ...] [--sort ...] [--order ...] [--start N] [--max N]
    import argparse
    p = argparse.ArgumentParser(prog="arxiv.py search")
    p.add_argument("query")
    p.add_argument("--field", default="all",
                   choices=["all", "ti", "au", "abs", "co", "jr", "cat"])
    p.add_argument("--sort", default="relevance",
                   choices=["relevance", "lastUpdatedDate", "submittedDate"])
    p.add_argument("--order", default="descending",
                   choices=["ascending", "descending"])
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--max", type=int, default=10)
    ns = p.parse_args(args)
    params = {
        "search_query": f"{ns.field}:{ns.query}" if ns.field != "all" else f"all:{ns.query}",
        "start": ns.start,
        "max_results": min(ns.max, 100),
        "sortBy": ns.sort,
        "sortOrder": ns.order,
    }
    print(json.dumps(call(params), indent=2, ensure_ascii=False))


def cmd_get(args):
    # arxiv.py get 1706.03762,2103.00020
    ids = [i.strip() for i in ",".join(args).split(",") if i.strip()]
    if not ids:
        sys.exit("usage: arxiv.py get <arxiv-id>[,<arxiv-id>...]")
    print(json.dumps(call({"id_list": ",".join(ids)}), indent=2, ensure_ascii=False))


def cmd_raw(args):
    path = args[0] if args else "query?search_query=all:electron&max_results=1"
    if path.startswith("/"):
        path = path[1:]
    req = urllib.request.Request(f"https://export.arxiv.org/{path}")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/atom+xml")
    with urllib.request.urlopen(req, timeout=60) as resp:
        sys.stdout.write(resp.read().decode("utf-8", "replace"))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd, rest = argv[0], argv[1:]
    if cmd == "search":
        cmd_search(rest)
    elif cmd == "get":
        cmd_get(rest)
    elif cmd == "raw":
        cmd_raw(rest)
    else:
        sys.exit(f"unknown command {cmd!r}; try: search | get | raw")


if __name__ == "__main__":
    main(sys.argv[1:])
