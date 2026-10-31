#!/usr/bin/env python3
"""
yt_kb.query — hybrid search over the knowledge base.

Usage:
  /opt/homebrew/bin/python3.12 tools/yt_kb/query.py "query text" [--n 8] [--video VIDEOID] [--stats]

Every result includes a deep link that opens the video at that moment.
"""
import argparse
import os
import re
import sqlite3
import struct

PROJ = os.getcwd()
DATA_DIR = os.path.join(PROJ, "data")          # overridden by --db
DB_PATH = os.path.join(DATA_DIR, "kb.sqlite")
MODEL_CACHE = os.path.join(DATA_DIR, "fastembed_cache")
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def open_db():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"no database at {DB_PATH} — run ingest.py first")
    db = sqlite3.connect(DB_PATH, timeout=60)
    db.execute("PRAGMA busy_timeout=60000")
    db.enable_load_extension(True)
    import sqlite_vec
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def embed_query(text):
    from fastembed import TextEmbedding
    m = TextEmbedding("BAAI/bge-small-en-v1.5", cache_dir=MODEL_CACHE)
    vec = list(m.embed([QUERY_PREFIX + text]))[0]
    return struct.pack("<%df" % len(vec), *vec)


def vec_search(db, qvec, k=30, video=None):
    sql = """
      SELECT chunk_id, distance FROM chunks_vec
      WHERE embedding MATCH ? AND k = ?
    """
    args = [qvec, k * 3 if video else k]
    if video:
        sql = """
          SELECT v.chunk_id, v.distance FROM chunks_vec v
          JOIN chunks c ON c.chunk_id = v.chunk_id
          WHERE v.embedding MATCH ? AND v.k = ? AND c.video_id = ?
        """
        args.append(video)
    return [(r[0], r[1]) for r in db.execute(sql, args)]


def fts_search(db, query, k=30, video=None):
    # sanitize: keep word chars, drop FTS operators to avoid syntax errors
    toks = re.findall(r"\w+", query, re.UNICODE)
    if not toks:
        return []
    def run(terms):
        sql = """
          SELECT chunk_id, bm25(chunks_fts) AS rank FROM chunks_fts
          WHERE chunks_fts MATCH ?
          ORDER BY rank LIMIT ?
        """
        args = [" ".join(terms), k * 3 if video else k]
        if video:
            sql = """
              SELECT f.chunk_id, bm25(chunks_fts) AS rank FROM chunks_fts f
              JOIN chunks c ON c.chunk_id = f.chunk_id
              WHERE chunks_fts MATCH ? AND c.video_id = ?
              ORDER BY rank LIMIT ?
            """
            args = [" ".join(terms), video, k * 3]
        try:
            return [(r[0], r[1]) for r in db.execute(sql, args)]
        except sqlite3.OperationalError:
            return []
    hits = run(toks)
    if not hits and len(toks) > 1:  # AND too strict -> OR
        hits = run([t + "*" for t in toks])
    return hits


def rrf_fuse(vec_hits, fts_hits, k=60):
    """Reciprocal Rank Fusion of the two ranked lists."""
    scores = {}
    for rank, (cid, _) in enumerate(vec_hits):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    for rank, (cid, _) in enumerate(fts_hits):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])


def fmt_ts(sec):
    sec = int(sec or 0)
    return f"{sec//60}:{sec%60:02d}"


def snippet(body, query, width=260):
    toks = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    low = body.lower()
    pos = -1
    for t in toks:
        p = low.find(t)
        if p >= 0 and (pos < 0 or p < pos):
            pos = p
    if pos < 0:
        return body[:width] + ("…" if len(body) > width else "")
    a = max(0, pos - width // 3)
    return ("…" if a else "") + body[a:a + width].strip() + "…"


def main():
    global DATA_DIR, DB_PATH, MODEL_CACHE
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="*", default=[])
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--video", default=None, help="restrict to one video id")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--db", default=None, help="KB directory (default: ./data)")
    args = ap.parse_args()
    if args.db:
        DATA_DIR = os.path.abspath(args.db)
        DB_PATH = os.path.join(DATA_DIR, "kb.sqlite")
        MODEL_CACHE = os.path.join(DATA_DIR, "fastembed_cache")
    q = " ".join(args.query).strip()

    db = open_db()
    if args.stats or not q:
        for r in db.execute("""
            SELECT ch.name, COUNT(DISTINCT v.video_id), COUNT(DISTINCT c.chunk_id),
                   MIN(v.upload_date), MAX(v.upload_date)
            FROM channels ch
            LEFT JOIN videos v ON v.channel_id = ch.channel_id AND v.status='ok'
            LEFT JOIN chunks c ON c.video_id = v.video_id
            GROUP BY ch.channel_id"""):
            print(f"channel: {r[0]}  videos={r[1]}  chunks={r[2]}  dates={r[3]}..{r[4]}")
        if not q:
            return

    print(f'query: "{q}"\n')
    qvec = embed_query(q)
    fused = rrf_fuse(vec_search(db, qvec, video=args.video),
                     fts_search(db, q, video=args.video))[: args.n]
    if not fused:
        print("no matches.")
        return
    for i, (cid, score) in enumerate(fused, 1):
        row = db.execute("""
          SELECT c.body, c.start_s, c.end_s, v.title, v.video_id,
                 v.upload_date, v.view_count
          FROM chunks c JOIN videos v ON v.video_id = c.video_id
          WHERE c.chunk_id=?""", (cid,)).fetchone()
        if not row:
            continue
        body, start, end, title, vid, date, views = row
        link = f"https://youtu.be/{vid}?t={int(start)}"
        views_s = f"{views/1e6:.1f}M views" if views and views >= 1e6 else (
                  f"{views/1e3:.0f}K views" if views else "")
        print(f"{i}. [{score:.4f}] {title}")
        print(f"   {date or '?'} | {views_s} | at {fmt_ts(start)}-{fmt_ts(end)}")
        print(f"   {link}")
        print(f"   {snippet(body, q)}")
        print()
    db.close()


if __name__ == "__main__":
    main()
