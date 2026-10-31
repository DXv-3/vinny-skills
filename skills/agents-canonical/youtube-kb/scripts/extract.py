#!/usr/bin/env python3
"""
yt_kb.extract — Phase 3: turn transcripts into structured knowledge tables.

Reads every video's chunks from the KB and populates, fully offline:

  tools_mentions(tool, video_id, start_s, mentions, first_snippet)
  numbers_mentions(kind, value, video_id, start_s, snippet)      # money figures
  frameworks(name, video_id, start_s, snippet)                    # "X framework/method/..."
  claims_candidates(video_id, start_s, sentence)                  # advice-sentence candidates

Every row carries video_id + chunk-level start_s (±2-3 min granularity) as provenance.

Usage:
  python3 extract.py [--db data] [--channel CHANNEL_ID] [--video VIDEO_ID] [--fresh-tables]
  python3 extract.py --stats        # summary of what was extracted
"""
import argparse
import os
import re
import sqlite3
import sys
from collections import defaultdict

DB_PARENT_DEFAULT = os.path.join(os.getcwd(), "data")
DB_PATH = os.path.join(DB_PARENT_DEFAULT, "kb.sqlite")

# ------------------------------------------------------------------ patterns
# Curated tool dictionary. Patterns are case-insensitive regex with word
# boundaries; common-word traps (make, bolt) get tighter patterns.
TOOLS = {
    "ChatGPT": r"chat\s?gpt", "OpenAI": r"open\s?ai", "GPT-4": r"gpt[\s-]?4",
    "GPT-5": r"gpt[\s-]?5", "o1": r"\bo1\b", "o3": r"\bo3\b",
    "Claude": r"\bclaude\b", "Claude Code": r"claude\s+code",
    "Gemini": r"\bgemini\b", "Copilot": r"\bcopilot\b", "Llama": r"\bllama\b",
    "Mistral": r"\bmistral\b", "DeepSeek": r"deep\s?seek", "Grok": r"\bgrok\b",
    "Perplexity": r"\bperplexity\b", "Midjourney": r"mid\s?journey",
    "DALL-E": r"dall[\s-]?e", "Runway": r"\brunway\b", "ElevenLabs": r"eleven\s?labs",
    "HeyGen": r"\bhey\s?gen\b", "Synthesia": r"\bsynthesia\b", "Sora": r"\bsora\b",
    "Cursor": r"\bcursor\b", "Windsurf": r"\bwindsurf\b", "v0": r"\bv0\b",
    "Lovable": r"\blovable\b", "Bolt": r"\bbolt\b", "Replit": r"\breplit\b",
    "n8n": r"\bn\s?8\s?n\b", "Make.com": r"make\.com", "Zapier": r"\bzapier\b",
    "Airtable": r"\bairtable\b", "Notion": r"\bnotion\b", "Slack": r"\bslack\b",
    "Google Sheets": r"google\s+sheets", "Excel": r"\bexcel\b",
    "Canva": r"\bcanva\b", "Figma": r"\bfigma\b", "Webflow": r"\bwebflow\b",
    "WordPress": r"word\s?press", "Shopify": r"\bshopify\b", "Wix": r"\bwix\b",
    "Squarespace": r"squarespace",
    "HubSpot": r"\bhubspot\b", "GoHighLevel": r"go\s?high\s?level|\bGHL\b",
    "Salesforce": r"sales\s?force", "ActiveCampaign": r"active\s?campaign",
    "Mailchimp": r"\bmailchimp\b", "Klaviyo": r"\bklaviyo\b",
    "Instantly": r"\binstantly\.?(?:ai|\.com)?\b(?=[\s.,)]|$)", "Apollo": r"\bapollo\.?io\b",
    "Stripe": r"\bstripe\b", "PayPal": r"pay\s?pal", "Wise": r"\bwise\.com\b",
    "Deel": r"\bdeel\b", "Upwork": r"\bupwork\b", "Fiverr": r"\bfiverr\b",
    "OnlineJobs.ph": r"online\s?jobs", "Indeed": r"\bindeed\b",
    "Whop": r"\bwhop\b", "Skool": r"\bskool\b", "Kajabi": r"\bkajabi\b",
    "Teachable": r"\bteachable\b", "Circle": r"\bcircle\.so\b",
    "Calendly": r"\bcalendly\b", "Cal.com": r"cal\.com", "Typeform": r"\btypeform\b",
    "Descript": r"\bdescript\b", "Opus Clip": r"opus\s+clip", "CapCut": r"\bcap\s?cut\b",
    "Veo": r"\bveo\b", "Kling": r"\bkling\b", "Higgsfield": r"\bhiggsfield\b",
    "Manus": r"\bmanus\b", "Devin": r"\bdevin\b", "Sunshine": r"\bsunshine\b",
    "Ramp": r"\bramp\b", "Mercury": r"\bmercury\b",
}

MONEY_RE = re.compile(
    r"\$\s?\d[\d,.]*\s?(?:k\b|thousand|m\b|million|b\b|billion)?|\b\d[\d,.]*\s?(?:million|billion)\s?(?:dollars|usd)\b",
    re.I)
CLAIM_MARKERS = re.compile(
    r"\b(you should|you need to|you have to|you gotta|i recommend|my advice|"
    r"the key is|what i do is|i suggest|do not|don't|never |always |"
    r"the secret|the trick is|the way to|the best way)\b", re.I)
FRAMEWORK_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9'&\-]*(?:\s+(?:of|the|[A-Z])[A-Za-z0-9'&\-]*){0,3}\s+"
    r"(?:framework|method|playbook|formula|blueprint|system))\b")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

MAX_CLAIMS_PER_VIDEO = 60


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


def ensure_tables(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS tools_mentions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tool TEXT NOT NULL, video_id TEXT NOT NULL, channel_id TEXT,
      start_s INTEGER, mentions INTEGER DEFAULT 1, first_snippet TEXT);
    CREATE TABLE IF NOT EXISTS numbers_mentions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL, value TEXT NOT NULL,
      video_id TEXT NOT NULL, channel_id TEXT, start_s INTEGER, snippet TEXT);
    CREATE TABLE IF NOT EXISTS frameworks(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL, video_id TEXT NOT NULL, channel_id TEXT,
      start_s INTEGER, snippet TEXT);
    CREATE TABLE IF NOT EXISTS claims_candidates(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      video_id TEXT NOT NULL, channel_id TEXT, start_s INTEGER, sentence TEXT);
    CREATE INDEX IF NOT EXISTS idx_tools_tool ON tools_mentions(tool);
    CREATE INDEX IF NOT EXISTS idx_tools_video ON tools_mentions(video_id);
    CREATE INDEX IF NOT EXISTS idx_numbers_video ON numbers_mentions(video_id);
    CREATE INDEX IF NOT EXISTS idx_claims_video ON claims_candidates(video_id);
    CREATE INDEX IF NOT EXISTS idx_fw_name ON frameworks(name);
    """)
    db.commit()


def snippet_at(body, pos, width=110):
    a = max(0, pos - width // 2)
    return ("…" if a else "") + body[a:a + width].strip() + "…"


def extract_video(db, vid, cid, chunks, claims=True):
    """chunks: ordered [(start_s, body)]. Fills aggregate rows for one video."""
    tool_hits = {}      # tool -> [count, first_start, first_snippet]
    number_rows = []
    fw_hits = {}
    claim_rows = []

    for start_s, body in chunks:
        low = body.lower()
        # tools
        for tool, pat in TOOLS.items():
            for m in re.finditer(pat, low, re.I):
                hit = tool_hits.setdefault(tool, [0, start_s, None])
                hit[0] += 1
                if hit[2] is None:
                    hit[2] = snippet_at(body, m.start())
        # money
        for m in MONEY_RE.finditer(body):
            val = m.group(0).strip()
            if len(val) <= 24:
                number_rows.append(("money", val, start_s, snippet_at(body, m.start())))
        # frameworks
        for m in FRAMEWORK_RE.finditer(body):
            name = re.sub(r"\s+", " ", m.group(1)).strip()
            key = name.lower()
            if key not in fw_hits:
                fw_hits[key] = [name, start_s, snippet_at(body, m.start())]
        # claim candidates (sentence level)
        if claims and len(claim_rows) < MAX_CLAIMS_PER_VIDEO:
            for sen in SENT_SPLIT.split(body):
                if len(claim_rows) >= MAX_CLAIMS_PER_VIDEO:
                    break
                s = sen.strip()
                if 30 <= len(s) <= 280 and CLAIM_MARKERS.search(s):
                    claim_rows.append((vid, cid, start_s, s))

    rows = []
    for tool, (cnt, first, snip) in tool_hits.items():
        rows.append(("tools_mentions", (tool, vid, cid, first, cnt, snip)))
    for kind, val, start_s, snip in number_rows:
        rows.append(("numbers_mentions", (kind, val, vid, cid, start_s, snip)))
    for _, (name, start_s, snip) in fw_hits.items():
        rows.append(("frameworks", (name, vid, cid, start_s, snip)))
    for r in claim_rows:
        rows.append(("claims_candidates", r))
    return rows


def main():
    global DB_PATH
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None, help="KB directory (default ./data)")
    ap.add_argument("--channel", default=None)
    ap.add_argument("--video", default=None)
    ap.add_argument("--fresh-tables", action="store_true",
                    help="delete previous extraction rows first")
    ap.add_argument("--no-claims", action="store_true")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    db_dir = os.path.abspath(args.db) if args.db else DB_PARENT_DEFAULT
    db = open_db(db_dir)
    ensure_tables(db)

    if args.stats:
        for t in ("tools_mentions", "numbers_mentions", "frameworks", "claims_candidates"):
            n = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"{t}: {n}")
        print("\ntop tools:")
        for r in db.execute("""SELECT tool, COUNT(*) v, SUM(mentions) m
                               FROM tools_mentions GROUP BY tool
                               ORDER BY v DESC LIMIT 12"""):
            print(f"  {r[0]}: {r[1]} videos, {r[2]} mentions")
        return

    if args.fresh_tables:
        for t in ("tools_mentions", "numbers_mentions", "frameworks", "claims_candidates"):
            db.execute(f"DELETE FROM {t}")
        db.commit()

    where, params = ["v.status='ok'"], []
    if args.channel:
        where.append("v.channel_id=?"); params.append(args.channel)
    if args.video:
        where.append("v.video_id=?"); params.append(args.video)
    vids = db.execute(f"""SELECT v.video_id, v.channel_id, v.title FROM videos v
                          WHERE {' AND '.join(where)} ORDER BY v.upload_date""",
                      params).fetchall()
    total = len(vids)
    print(f"extracting from {total} videos ...", flush=True)

    counts = defaultdict(int)
    for i, (vid, cid, title) in enumerate(vids, 1):
        chunks = db.execute(
            "SELECT start_s, body FROM chunks WHERE video_id=? ORDER BY chunk_id",
            (vid,)).fetchall()
        if not chunks:
            continue
        rows = extract_video(db, vid, cid, chunks, claims=not args.no_claims)
        # idempotent per video: clear this video's rows, then insert
        for t in ("tools_mentions", "numbers_mentions", "frameworks", "claims_candidates"):
            db.execute(f"DELETE FROM {t} WHERE video_id=?", (vid,))
        for t, vals in rows:
            cols = len(vals)
            db.execute(
                f"INSERT INTO {t} VALUES(NULL,{','.join('?' * cols)})", vals)
            counts[t] += 1
        db.commit()
        if i % 25 == 0 or i == total:
            print(f"  [{i}/{total}] {title[:50]}", flush=True)

    print("done.")
    for t in ("tools_mentions", "numbers_mentions", "frameworks", "claims_candidates"):
        print(f"  {t}: {counts[t]} rows")
    db.close()


if __name__ == "__main__":
    main()
