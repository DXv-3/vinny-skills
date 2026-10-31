#!/usr/bin/env python3
"""rank.py — FTS5 search with tag-aware re-ranking over the prompt KB.

The Item 7 recipe, executable: run FTS5 (porter), then re-rank by tag joins —
family match +5, technique match +3, type match +2 on top of bm25 relevance.

Usage:
  python3 rank.py '"GODMODE ENABLED"' --type jailbreak --limit 10
  python3 rank.py 'gogodode' --family gogodode --limit 5
  python3 rank.py 'airlock JSON CEO'

READ-ONLY: opens ~/surface/prompt_kb.db in sqlite ro-mode. Stdlib only.
"""
import argparse
import sqlite3
import sys

DB = "file:/Users/vinnygilberti/surface/prompt_kb.db?mode=ro"

ap = argparse.ArgumentParser(description="FTS5 + tag-aware re-rank over the prompt KB")
ap.add_argument("query", help="FTS5 query (quote phrases: '\"GODMODE ENABLED\"')")
ap.add_argument("--type", dest="ptype", help="boost a record type, e.g. jailbreak")
ap.add_argument("--family", help="boost a tag family, e.g. gogodode-l1b3rt4s")
ap.add_argument("--technique", help="boost a technique, e.g. divider-escalation")
ap.add_argument("--limit", type=int, default=10)
a = ap.parse_args()

con = sqlite3.connect(DB, uri=True)
sql = ("SELECT p.id, p.type, COALESCE(t.family,''), COALESCE(t.technique,''), "
       "p.name, snippet(prompts_fts, 4, '<<', '>>', ' … ', 8), "
       "bm25(prompts_fts), t.family, t.technique "
       "FROM prompts_fts f JOIN prompts p ON p.id = f.id "
       "LEFT JOIN tags t ON t.id = p.id WHERE prompts_fts MATCH ? "
       "ORDER BY rank LIMIT 300")
try:
    rows = con.execute(sql, (a.query,)).fetchall()
except sqlite3.OperationalError:
    # hyphens read as FTS5 column filters ("self-replication") — retry with
    # every token quoted; strip any user quotes first so multi-word
    # phrases survive the split (adversarial-review finding, 2026-09-26)
    clean = a.query.replace('"', " ")
    quoted = " ".join('"%s"' % tok for tok in clean.split())
    rows = con.execute(sql, (quoted,)).fetchall()

scored = []
for pid, typ, fam, tech, name, snip, bm25, fam_raw, tech_raw in rows:
    score = -bm25
    if a.family and fam_raw and a.family.lower() in fam_raw.lower():
        score += 5
    if a.technique and tech_raw and a.technique.lower() in tech_raw.lower():
        score += 3
    if a.ptype and typ == a.ptype:
        score += 2
    scored.append((score, pid, typ, fam, tech, name, snip))

scored.sort(key=lambda x: -x[0])
if not scored:
    print(f"no hits for {a.query!r}")
for score, pid, typ, fam, tech, name, snip in scored[: a.limit]:
    print(f"{pid} [{typ}] {fam or '-'}/{tech or '-'} (score {score:.2f}) — {name}")
    print(f"    {snip}")
    print()
