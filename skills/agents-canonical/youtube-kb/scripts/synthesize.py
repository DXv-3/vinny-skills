#!/usr/bin/env python3
"""
yt_kb.synthesize — Phase 4: cross-channel intelligence reports.

Two report modes, both offline, both grounded in KB rows with provenance:

  compare <topic>   Find where channels agree/contrary on a topic. Draws claim
                    candidates + query hits per channel, with citations.
  map [CHANNEL_ID]  Channel knowledge map: topic clusters, tool footprint with
                    adoption timeline, volume by month, top frameworks.

Usage:
  python3 synthesize.py --db data compare "getting first clients"
  python3 synthesize.py --db data map
  python3 synthesize.py --db data map --channel UCui4jxDaMb53Gdh-AZUTPAg --top 8
"""
import argparse
import os
import re
import sqlite3
import struct
from collections import defaultdict

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def open_db(db_dir):
    path = os.path.join(db_dir, "kb.sqlite")
    if not os.path.exists(path):
        raise SystemExit(f"no DB at {path}")
    db = sqlite3.connect(path, timeout=60)
    db.execute("PRAGMA busy_timeout=60000")
    db.enable_load_extension(True)
    import sqlite_vec
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def embed(db_dir, text):
    cache_dir = os.path.join(db_dir, "fastembed_cache")
    from fastembed import TextEmbedding
    m = TextEmbedding("BAAI/bge-small-en-v1.5", cache_dir=cache_dir)
    v = list(m.embed([QUERY_PREFIX + text]))[0]
    return struct.pack("<%df" % len(v), *v)


def vec_hits(db, qvec, k=20, channel=None):
    sql = """SELECT cv.chunk_id, cv.distance FROM chunks_vec cv
             WHERE cv.embedding MATCH ? AND cv.k = ?"""
    if channel:
        sql = """SELECT cv.chunk_id, cv.distance FROM chunks_vec cv
                 JOIN chunks c ON c.chunk_id=cv.chunk_id
                 JOIN videos v ON v.video_id=c.video_id
                 WHERE cv.embedding MATCH ? AND cv.k = ? AND v.channel_id=?"""
        return db.execute(sql, (qvec, k, channel)).fetchall()
    return db.execute(sql, (qvec, k)).fetchall()


def fts_hits(db, topic, k=20, channel=None):
    toks = re.findall(r"\w+", topic)
    if not toks:
        return []
    try:
        if channel:
            return db.execute("""SELECT f.chunk_id FROM chunks_fts f
                JOIN chunks c ON c.chunk_id=f.chunk_id
                JOIN videos v ON v.video_id=c.video_id
                WHERE chunks_fts MATCH ? AND v.channel_id=? LIMIT ?""",
                (" OR ".join(toks), channel, k)).fetchall()
        return db.execute("SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT ?",
                          (" OR ".join(toks), k)).fetchall()
    except sqlite3.OperationalError:
        return []


def chunk_row(db, chunk_id):
    return db.execute("""SELECT c.body, c.start_s, v.video_id, v.title, v.upload_date,
                         v.channel_id, ch.name
                         FROM chunks c JOIN videos v ON v.video_id=c.video_id
                         JOIN channels ch ON ch.channel_id=v.channel_id
                         WHERE c.chunk_id=?""", (chunk_id,)).fetchone()


def fmt_ts(s):
    s = int(s or 0)
    return f"{s//60}:{s%60:02d}"


def cite(row):
    return f'"{row[3]}" ({row[4]}) at {fmt_ts(row[1])} — https://youtu.be/{row[2]}?t={int(row[1])}'


# ------------------------------------------------------------------ compare
def do_compare(db, db_dir, topic, per_channel=3):
    qvec = embed(db_dir, topic)
    channels = db.execute("SELECT channel_id, name FROM channels WHERE channel_id IN "
                          "(SELECT DISTINCT channel_id FROM videos WHERE status='ok')").fetchall()
    print(f'# Cross-channel comparison: "{topic}"\n')
    print(f"Channels: {', '.join(n for _, n in channels)}\n")

    scored = defaultdict(lambda: defaultdict(list))  # ch -> score -> rows
    for cid, cname in channels:
        vh = {cid_: d for cid_, d in vec_hits(db, qvec, 40, channel=cid)}
        fh = fts_hits(db, topic, 40, channel=cid)
        scores = defaultdict(float)
        for rank, (chunk_id, d) in enumerate(sorted(vh.items(), key=lambda x: x[1])):
            scores[chunk_id] += 1.0 / (60 + rank + 1)
        for rank, (chunk_id,) in enumerate(fh):
            scores[chunk_id] += 1.0 / (60 + rank + 1)
        top = sorted(scores.items(), key=lambda x: -x[1])[:per_channel]
        for chunk_id, sc in top:
            row = chunk_row(db, chunk_id)
            if row:
                scored[cid][sc] = row

    for cid, cname in channels:
        hits = scored.get(cid, {})
        print(f"## {cname}")
        if not hits:
            print("  (no strong hits for this topic)\n")
            continue
        for sc, row in sorted(hits.items(), reverse=True):
            body = re.sub(r"\s+", " ", row[0])[:340]
            print(f"- [{sc:.4f}] {cite(row)}")
            print(f"  “{body}”")
        print()

    print("## Claim-candidate cross-reference (advice sentences matching topic keywords)")
    toks = [t for t in re.findall(r"\w{4,}", topic.lower())]
    found = False
    for cid, cname in channels:
        like = " OR ".join(f"sentence LIKE '%{t}%'" for t in toks)
        rows = db.execute(f"""SELECT v.title, v.upload_date, c.start_s, c.sentence, c.video_id
                              FROM claims_candidates c JOIN videos v ON v.video_id=c.video_id
                              WHERE v.channel_id=? AND ({like}) LIMIT 3""", (cid,)).fetchall()
        if rows:
            found = True
            print(f"\n### {cname}")
            for t, d, s, sen, vid in rows:
                print(f"- “{sen}”  [\"{t}\" ({d}) at {fmt_ts(s)} — https://youtu.be/{vid}?t={int(s)}]")
    if not found:
        print("(none)")
    print("\nNOTE: verdicts (agree/contradict) are yours to draw — this report pairs the "
          "strongest on-topic statements per channel side by side.")


# --------------------------------------------------------------------- map
def do_map(db, channel=None, top=6):
    where, params = "v.status='ok'", []
    if channel:
        where += " AND v.channel_id=?"; params.append(channel)
    ch = db.execute(f"""SELECT DISTINCT ch.channel_id, ch.name FROM videos v
                        JOIN channels ch ON ch.channel_id=v.channel_id
                        WHERE {where}""", params).fetchone()
    if not ch:
        raise SystemExit("no videos match")
    cid, cname = ch
    print(f"# Channel knowledge map: {cname}\n")

    n_vid, n_chunks, d1, d2 = db.execute(f"""SELECT COUNT(*), SUM(v.n_chunks),
                                          MIN(v.upload_date), MAX(v.upload_date)
                                          FROM videos v WHERE {where}""", params).fetchone()
    print(f"- {n_vid} videos, {n_chunks} chunks, span {d1} → {d2}")

    print("\n## Volume by month")
    for ym, n in db.execute(f"""SELECT substr(upload_date,1,6) ym, COUNT(*)
                                FROM videos v WHERE {where}
                                GROUP BY ym ORDER BY ym""", params):
        print(f"  {ym[:4]}-{ym[4:]}: {'#' * min(n, 40)} {n}")

    print(f"\n## Tool footprint (top {top}, with first-mention date = adoption timeline)")
    for tool, first, n in db.execute(f"""SELECT t.tool, MIN(v.upload_date), COUNT(DISTINCT t.video_id) AS nv
            FROM tools_mentions t JOIN videos v ON v.video_id=t.video_id
            WHERE {where} GROUP BY t.tool ORDER BY nv DESC LIMIT ?""", params + [top]):
        print(f"  {tool}: {n} videos, first mentioned {first}")

    print(f"\n## Named frameworks/methods (top {top})")
    for name, vdate in db.execute(f"""SELECT f.name, MIN(v.upload_date)
            FROM frameworks f JOIN videos v ON v.video_id=f.video_id
            WHERE {where} GROUP BY f.name ORDER BY f.name LIMIT ?""", params + [top]):
        print(f"  {name} (since {vdate})")

    print("\n## Biggest videos")
    for title, views, date, vid in db.execute(f"""SELECT title, view_count, upload_date, video_id
            FROM videos v WHERE {where} ORDER BY view_count DESC LIMIT 5""", params):
        print(f"  {views or 0:>10,.0f}  {date}  {title[:60]}  https://youtu.be/{vid}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["compare", "map"])
    ap.add_argument("topic", nargs="*", default=[])
    ap.add_argument("--db", default=None)
    ap.add_argument("--channel", default=None)
    ap.add_argument("--per-channel", type=int, default=3)
    ap.add_argument("--top", type=int, default=6)
    args = ap.parse_args()
    db_dir = os.path.abspath(args.db) if args.db else os.path.join(os.getcwd(), "data")
    db = open_db(db_dir)
    topic = " ".join(args.topic).strip()
    if args.mode == "compare":
        if not topic:
            raise SystemExit('compare needs a topic, e.g. compare "getting clients"')
        do_compare(db, db_dir, topic, per_channel=args.per_channel)
    else:
        do_map(db, channel=args.channel, top=args.top)


if __name__ == "__main__":
    main()
