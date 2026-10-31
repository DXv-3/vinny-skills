#!/usr/bin/env python3
"""
yt_kb.ingest — build a hybrid (vector + full-text) SQLite knowledge base
from a YouTube channel (or any URL that resolves to one).

Usage:
  /opt/homebrew/bin/python3.12 tools/yt_kb/ingest.py <url> [--limit N] [--fresh]

Accepted URL forms (resolved via yt-dlp):
  https://youtu.be/VIDEOID              -> ingests that video's channel
  https://www.youtube.com/watch?v=ID    -> ingests that video's channel
  https://www.youtube.com/@handle       -> channel
  https://www.youtube.com/@handle/videos
  https://www.youtube.com/channel/UC...

Output: data/kb.sqlite  (tables: channels, videos, chunks, chunks_fts, chunks_vec)
Search: /opt/homebrew/bin/python3.12 tools/yt_kb/query.py "your question"
"""
import argparse
import json
import os
import re
import sqlite3
import struct
import subprocess
import sys
import time

PROJ = os.getcwd()
DATA_DIR = os.path.join(PROJ, "data")          # overridden by --db
DB_PATH = os.path.join(DATA_DIR, "kb.sqlite")
SUB_DIR = os.path.join(DATA_DIR, "raw_subs")
MODEL_CACHE = os.path.join(DATA_DIR, "fastembed_cache")
YTDLP = "yt-dlp"
EA = "youtube:player_client=android"
CHUNK_TARGET = 450   # words per chunk
CHUNK_OVERLAP = 60   # words carried into the next chunk
DIM = 384            # BAAI/bge-small-en-v1.5

CUE_LINE = re.compile(r"((?:\d{1,2}:)?\d{2}:\d{2}\.\d{3}) --> ((?:\d{1,2}:)?\d{2}:\d{2}\.\d{3})")
TAG_RE = re.compile(r"<[^>]+>")
BRACKET_RE = re.compile(r"^\[[^\]]*\]$")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


# ------------------------------------------------------------------ helpers
def info(msg):
    print(msg, flush=True)


def ytdlp(*args, timeout=300, retry=6):
    """Run yt-dlp with the working android client, retry hard on 429 storms."""
    env = dict(os.environ)
    env["PATH"] = os.path.expanduser("~/Library/Python/3.9/bin") + ":" + env.get("PATH", "")
    full = [YTDLP, "--extractor-args", EA, "--no-warnings"] + list(args)
    delay = 30
    for attempt in range(retry):
        p = subprocess.run(full, capture_output=True, text=True, timeout=timeout,
                           env=env, errors="replace")
        err = p.stderr or ""
        if p.returncode == 0:
            return p.stdout
        if "429" in err or "Too Many Requests" in err:
            info(f"    rate-limited, backing off {delay}s (attempt {attempt + 1}/{retry}) ...")
            time.sleep(delay)
            delay = min(delay * 2, 300)
            continue
        raise RuntimeError(err.strip().splitlines()[-1][:300] if err.strip() else "yt-dlp failed")
    raise RuntimeError("yt-dlp kept failing (rate limit?)")


def classify(url):
    u = url.lower()
    if "youtu.be/" in u or "watch?v=" in u:
        return "video"
    return "channel"


def resolve_channel(url):
    """Return (channel_id, channel_name, channel_url, profile_json_or_None)."""
    if classify(url) == "video":
        out = ytdlp("--skip-download", "--print",
                    "%(channel_id)s|%(channel)s|%(uploader_url)s", url)
        line = out.strip().splitlines()[-1]
        cid, name, curl = (line.split("|") + ["", "", ""])[:3]
        if not cid or cid == "NA":
            raise RuntimeError(f"could not resolve a channel from {url}")
        return cid, name, curl
    # already a channel URL
    out = ytdlp("--flat-playlist", "--playlist-items", "1", "--print",
                "%(channel_id)s|%(channel)s|%(uploader_url)s", url)
    line = out.strip().splitlines()[-1] if out.strip() else ""
    f = (line.split("|") + ["", "", ""])[:3]
    cid, name, curl = f
    if not cid or cid == "NA":
        # last resort: take first video's channel
        first = ytdlp("--flat-playlist", "--print", "%(id)s", url)
        first_vid = first.strip().splitlines()[0]
        return resolve_channel(f"https://youtu.be/{first_vid}")
    return cid, name, curl


def list_channel_videos(channel_url):
    """Newest-first listing of the channel's regular videos."""
    base = channel_url.rstrip("/")
    if "/videos" not in base:
        base += "/videos"
    out = ytdlp("--flat-playlist", "--print", "%(id)s\t%(title)s", base)
    vids = []
    for line in out.strip().splitlines():
        parts = line.split("\t", 1)
        if parts and parts[0]:
            vids.append({"id": parts[0], "title": parts[1] if len(parts) > 1 else ""})
    return vids


def fetch_video(url_or_id):
    """One network pass: metadata (single-line JSON) + English subs."""
    vid = url_or_id if re.fullmatch(r"[\w-]{11}", url_or_id) else url_or_id
    os.makedirs(SUB_DIR, exist_ok=True)
    tmpl = os.path.join(SUB_DIR, "%(id)s")
    args = [
        "--skip-download", "--no-simulate",  # --print implies simulate unless this is set
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en,en-orig,en-US,en-GB",
        "--sub-format", "vtt/srt/best",
        "-o", tmpl,
        "--dump-json",  # one JSON record per video on stdout (implies simulate; disabled above)
        f"https://www.youtube.com/watch?v={vid}",
    ]
    # clear stale subs for this id
    for f in os.listdir(SUB_DIR):
        if f.startswith(vid + "."):
            os.remove(os.path.join(SUB_DIR, f))
    out = ytdlp(*args)
    j = None
    for line in out.splitlines():
        ls = line.strip()
        if ls.startswith("{") and ls.endswith("}"):
            j = json.loads(ls)  # keep the last one (the video itself)
    if not j:
        raise RuntimeError("no metadata JSON in yt-dlp output")
    meta = {
        "video_id": j.get("id", vid),
        "title": j.get("title") or "",
        "upload_date": j.get("upload_date") or "",
        "duration": j.get("duration"),
        "view_count": j.get("view_count"),
        "like_count": j.get("like_count"),
        "description": (j.get("description") or "")[:4000],
        "channel": j.get("channel") or "",
        "channel_follower_count": j.get("channel_follower_count"),
    }
    # find the written sub file
    sub_file, sub_lang = None, None
    for fn in sorted(os.listdir(SUB_DIR)):
        if fn.startswith(vid + ".") and (fn.endswith(".vtt") or fn.endswith(".srt")):
            sub_file = os.path.join(SUB_DIR, fn)
            sub_lang = fn.split(".")[1]
            break
    cues = vtt_to_cues(sub_file) if sub_file else []
    return meta, cues, sub_lang


# --------------------------------------------------------------- vtt parsing
def ts_to_s(ts):
    parts = [float(x) for x in ts.strip().split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def collapse_repeats(cues, window=3):
    """YouTube auto-captions sometimes interleave two duplicate streams.
    Drop sentences (>=3 words) that repeat within the last `window` sentences."""
    recent, out = [], []
    for s, e, txt in cues:
        kept = []
        for sen in SENT_SPLIT.split(txt):
            sen = sen.strip()
            if not sen:
                continue
            if len(sen.split()) >= 3 and sen.lower() in [r.lower() for r in recent[-window:]]:
                continue
            kept.append(sen)
            recent.append(sen)
        if kept:
            out.append((s, e, " ".join(kept)))
        elif out:  # cue became empty -> extend previous cue's end time
            ps, pe, pt = out[-1]
            out[-1] = (ps, e, pt)
    return out


def vtt_to_cues(path):
    """VTT/SRT -> list of (start_s, end_s, text) with rolling duplicates removed."""
    cues, cur = [], None
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n").strip()
        m = CUE_LINE.search(line)
        if m:
            if cur and cur[2]:
                cues.append(cur)
            cur = [ts_to_s(m.group(1)), ts_to_s(m.group(2)), []]
            continue
        if cur is None or not line or "-->" in line or line.isdigit():
            continue
        txt = TAG_RE.sub("", line).strip()
        if not txt or BRACKET_RE.match(txt):
            continue
        if cur[2] and txt == cur[2][-1]:
            continue  # rolling-caption duplicate
        cur[2].append(txt)
    if cur and cur[2]:
        cues.append(cur)
    return collapse_repeats([(c[0], c[1], " ".join(c[2])) for c in cues if c[1] > c[0]])


# ----------------------------------------------------------------- chunking
def collapse_ngram_stream(words, max_l=16, min_l=1):
    """Auto-caption tracks often interleave two duplicate text streams.
    Collapse the word stream by dropping any run of words that exactly
    repeats the tail of the already-emitted stream (n-gram length 2..16)."""
    out = []
    i, n = 0, len(words)
    low = lambda ws: [w.lower() for w, _, _ in ws]
    while i < n:
        dropped = False
        for L in range(max_l, min_l - 1, -1):
            if len(out) >= L and i + L <= n and low(out[-L:]) == low(words[i:i + L]):
                i += L
                dropped = True
                break
        if not dropped:
            out.append(words[i])
            i += 1
    return out


def cues_to_chunks(cues):
    """~450-word chunks with real timestamps; 60-word overlap between chunks."""
    words = []  # (word, start, end)
    for s, e, txt in cues:
        for w in txt.split():
            words.append((w, s, e))
    words = collapse_ngram_stream(words)
    chunks = []
    i, n = 0, len(words)
    while i < n:
        j = min(i + CHUNK_TARGET, n)
        body_words = words[i:j]
        chunks.append({
            "body": " ".join(w for w, _, _ in body_words),
            "start": int(body_words[0][1]),
            "end": int(body_words[-1][2]),
        })
        if j >= n:
            break
        i = j - CHUNK_OVERLAP  # carry tail into next chunk
        if i <= 0:
            i = j
    return chunks


# ----------------------------------------------------------------- database
def open_db(fresh=False):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if fresh and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH, timeout=60)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=60000")
    db.enable_load_extension(True)
    import sqlite_vec
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS channels(
      channel_id TEXT PRIMARY KEY, name TEXT, url TEXT,
      description TEXT, subs TEXT, updated TEXT
    );
    CREATE TABLE IF NOT EXISTS videos(
      video_id TEXT PRIMARY KEY,
      channel_id TEXT REFERENCES channels(channel_id),
      title TEXT, description TEXT, upload_date TEXT,
      duration INTEGER, view_count INTEGER, like_count INTEGER,
      transcript TEXT, n_chunks INTEGER DEFAULT 0, status TEXT
    );
    CREATE TABLE IF NOT EXISTS chunks(
      chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
      video_id TEXT REFERENCES videos(video_id),
      body TEXT, start_s INTEGER, end_s INTEGER
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(chunk_id UNINDEXED, body);
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
      chunk_id INTEGER PRIMARY KEY, embedding float[%d]);
    """ % DIM)
    db.commit()
    return db


def remove_video(db, vid):
    """Clean every trace of a video before re-ingesting it."""
    ids = [r[0] for r in db.execute(
        "SELECT chunk_id FROM chunks WHERE video_id=?", (vid,)).fetchall()]
    for cid in ids:
        db.execute("DELETE FROM chunks_fts WHERE chunk_id=?", (cid,))
        db.execute("DELETE FROM chunks_vec WHERE chunk_id=?", (cid,))
    db.execute("DELETE FROM chunks WHERE video_id=?", (vid,))
    db.execute("DELETE FROM videos WHERE video_id=?", (vid,))


def get_embedder():
    from fastembed import TextEmbedding
    return TextEmbedding("BAAI/bge-small-en-v1.5", cache_dir=MODEL_CACHE)


def vec_blob(vec):
    return struct.pack("<%df" % len(vec), *vec)


# ------------------------------------------------------------------- ingest
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--limit", type=int, default=0, help="max videos to ingest")
    ap.add_argument("--fresh", action="store_true", help="rebuild the DB from scratch")
    ap.add_argument("--db", default=None, help="KB directory (default: ./data)")
    args = ap.parse_args()
    if args.db:
        global DATA_DIR, DB_PATH, SUB_DIR, MODEL_CACHE
        DATA_DIR = os.path.abspath(args.db)
        DB_PATH = os.path.join(DATA_DIR, "kb.sqlite")
        SUB_DIR = os.path.join(DATA_DIR, "raw_subs")
        MODEL_CACHE = os.path.join(DATA_DIR, "fastembed_cache")

    info(f"resolving channel from: {args.url}")
    cid, cname, curl = resolve_channel(args.url)
    info(f"channel: {cname} ({cid}) {curl}")

    listing = list_channel_videos(curl or args.url)
    if args.limit:
        listing = listing[:args.limit]
    info(f"videos in listing: {len(listing)}")

    db = open_db(fresh=args.fresh)
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    db.execute("""INSERT INTO channels(channel_id,name,url,description,subs,updated)
                  VALUES(?,?,?,?,?,?)
                  ON CONFLICT(channel_id) DO UPDATE SET name=excluded.name,
                    url=excluded.url, updated=excluded.updated""",
               (cid, cname, curl, None, None, now))
    db.commit()

    embedder = None  # lazy: only load if at least one transcript arrives
    stats = {"ok": 0, "no_subs": 0, "error": 0}

    for idx, item in enumerate(listing, 1):
        vid, vtitle = item["id"], item["title"]
        have = db.execute("SELECT status FROM videos WHERE video_id=?", (vid,)).fetchone()
        if have and have[0] == "ok":
            info(f"[{idx}/{len(listing)}] SKIP (already ingested) {vtitle[:60]}")
            continue
        info(f"[{idx}/{len(listing)}] {vtitle[:70]}")
        try:
            meta, cues, slang = fetch_video(vid)
            title = meta["title"] or vtitle
            if not cues:
                info("    no captions -> skipped")
                remove_video(db, vid)
                db.execute("""INSERT INTO videos(video_id,channel_id,title,status)
                              VALUES(?,?,?,'no_subs')""", (vid, cid, title))
                db.commit()
                stats["no_subs"] += 1
                continue
            chunks = cues_to_chunks(cues)
            if embedder is None:
                info("    loading embedding model (one-time, ~1 min) ...")
                embedder = get_embedder()
            vectors = list(embedder.embed([c["body"] for c in chunks]))
            remove_video(db, vid)
            db.execute("""INSERT INTO videos(video_id,channel_id,title,description,
                          upload_date,duration,view_count,like_count,transcript,
                          n_chunks,status) VALUES(?,?,?,?,?,?,?,?,?,?, 'ok')""",
                       (vid, cid, title, meta["description"], meta["upload_date"],
                        meta["duration"], meta["view_count"], meta["like_count"],
                        " ".join(c["body"] for c in chunks), len(chunks)))
            # backfill channel profile from video metadata (listings lack it)
            if meta.get("channel"):
                db.execute("""UPDATE channels SET name=?
                              WHERE channel_id=? AND (name IS NULL OR name='' OR name='NA')""",
                           (meta["channel"], cid))
            if meta.get("channel_follower_count"):
                db.execute("""UPDATE channels SET subs=?
                              WHERE channel_id=? AND (subs IS NULL OR subs='')""",
                           (str(meta["channel_follower_count"]), cid))
            for c, v in zip(chunks, vectors):
                cur = db.execute(
                    "INSERT INTO chunks(video_id,body,start_s,end_s) VALUES(?,?,?,?)",
                    (vid, c["body"], c["start"], c["end"]))
                db.execute("INSERT INTO chunks_fts(chunk_id,body) VALUES(?,?)",
                           (cur.lastrowid, c["body"]))
                db.execute("INSERT INTO chunks_vec(chunk_id,embedding) VALUES(?,?)",
                           (cur.lastrowid, vec_blob(v)))
            db.commit()
            stats["ok"] += 1
            info(f"    {len(chunks)} chunks, {len(cues)} cues, lang={slang}")
        except Exception as e:
            info(f"    ERROR: {e}")
            try:
                remove_video(db, vid)
                db.execute("""INSERT INTO videos(video_id,channel_id,title,status)
                              VALUES(?,?,?,'error')""", (vid, cid, vtitle))
                db.commit()
            except Exception:
                pass
            stats["error"] += 1
        time.sleep(4)  # be polite to YouTube (429s are aggressive on shared IPs)

    total_chunks = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    total_videos = db.execute("SELECT COUNT(*) FROM videos WHERE status='ok'").fetchone()[0]
    db.close()
    info("")
    info(f"DONE. ok={stats['ok']} no_subs={stats['no_subs']} error={stats['error']}")
    info(f"DB: {DB_PATH}")
    info(f"videos with transcripts: {total_videos}, chunks total: {total_chunks}")
    q = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query.py")
    info(f'search it: {sys.executable} "{q}" "your question here"')


if __name__ == "__main__":
    main()
