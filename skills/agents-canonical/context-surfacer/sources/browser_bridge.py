#!/usr/bin/env python3
"""
browser_bridge.py — Import browser-based AI chat exports into sessions.sqlite.

Supports:
  - Z.AI HTML exports (chat-user / chat-assistant classes)
  - Gemini conversations (JSON/MD exports)
  - Generic HTML chat exports (detects role patterns)

Usage:
    python3 browser_bridge.py --import-zai ~/Downloads/02_WEB_SAVES/zai-chat-*.html
    python3 browser_bridge.py --import-gemini ~/Desktop/google-data-export/gemini-conversations.md
    python3 browser_bridge.py --list-sources
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / "sessions" / "sessions.sqlite"


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _file_hash(path: str) -> str:
    try:
        data = Path(path).read_bytes()[:1000]
        return hashlib.md5(data).hexdigest()
    except Exception:
        return ""


# ─── Z.AI HTML Parser ───

def parse_zai_html(file_path: str) -> list[dict]:
    """Parse Z.AI chat HTML export into turns.

    Z.AI format: <div class="chat-user ..."> and <div class="chat-assistant ...">
    """
    try:
        html = Path(file_path).read_text(errors="replace")
    except Exception:
        return []

    turns = []

    # Extract user messages
    user_pattern = re.compile(
        r'<div[^>]*class="chat-user[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL,
    )
    for m in user_pattern.finditer(html):
        content = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if content:
            turns.append({"role": "user", "content": content})

    # Extract assistant messages
    assistant_pattern = re.compile(
        r'<div[^>]*class="chat-assistant[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL,
    )
    for m in assistant_pattern.finditer(html):
        content = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if content:
            turns.append({"role": "ai", "content": content})

    return turns


# ─── Gemini MD Parser ───

def parse_gemini_md(file_path: str) -> list[dict]:
    """Parse Gemini conversations markdown export into turns."""
    try:
        text = Path(file_path).read_text(errors="replace")
    except Exception:
        return []

    turns = []
    # Gemini MD format: "## You" or "## User" for user, "## Gemini" for AI
    sections = re.split(r"^## (You|User|Gemini)\s*$", text, flags=re.MULTILINE)

    current_role = None
    for part in sections:
        part = part.strip()
        if part in ("You", "User"):
            current_role = "user"
        elif part == "Gemini":
            current_role = "ai"
        elif current_role and part:
            turns.append({"role": current_role, "content": part})

    return turns


# ─── Generic HTML Parser ───

def parse_generic_html(file_path: str) -> list[dict]:
    """Parse generic HTML chat export by detecting role patterns."""
    try:
        html = Path(file_path).read_text(errors="replace")
    except Exception:
        return []

    turns = []

    # Try common patterns
    for role, pattern_str in [
        ("user", r'<div[^>]*class="[^"]*user[^"]*"[^>]*>(.*?)</div>'),
        ("ai", r'<div[^>]*class="[^"]*(?:assistant|bot|ai)[^"]*"[^>]*>(.*?)</div>'),
        ("user", r'<div[^>]*data-role="user"[^>]*>(.*?)</div>'),
        ("ai", r'<div[^>]*data-role="assistant"[^>]*>(.*?)</div>'),
    ]:
        for m in re.finditer(pattern_str, html, re.DOTALL):
            content = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if content and len(content) > 10:
                turns.append({"role": role, "content": content})

    return turns


# ─── Import Functions ───

def import_zai(file_paths: list[str], dry_run: bool = False):
    """Import Z.AI HTML chat exports into sessions.sqlite."""
    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"  SKIP: {path} — not found")
            continue

        session_id = f"zai-{path.stem}"
        file_hash = _file_hash(str(path))

        # Check if already fed
        existing = conn.execute(
            "SELECT file_hash FROM fed_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if existing and existing[0] == file_hash:
            print(f"  SKIP: {session_id} — already indexed")
            continue

        turns = parse_zai_html(str(path))
        if not turns:
            print(f"  SKIP: {session_id} — no turns extracted")
            continue

        print(f"  {session_id}: {len(turns)} turns")

        if not dry_run:
            # Delete old data
            conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

            # Insert session
            conn.execute(
                """INSERT INTO sessions
                   (id, agent, title, source_file, started_at, ended_at,
                    turn_count, user_turn_count, ai_turn_count, noise_ratio, indexed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    "zai",
                    turns[0]["content"][:100] if turns else "",
                    str(path),
                    now,
                    now,
                    len(turns),
                    sum(1 for t in turns if t["role"] == "user"),
                    sum(1 for t in turns if t["role"] == "ai"),
                    0.0,
                    now,
                ),
            )

            # Insert turns
            for turn in turns:
                conn.execute(
                    """INSERT INTO turns
                       (session_id, role, timestamp, content, word_count)
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, turn["role"], now, turn["content"], len(turn["content"].split())),
                )

            # Mark fed
            conn.execute(
                "INSERT OR REPLACE INTO fed_sessions (session_id, file_hash, fed_at) VALUES (?, ?, ?)",
                (session_id, file_hash, now),
            )

    if not dry_run:
        conn.commit()
    conn.close()


def import_gemini(file_path: str, dry_run: bool = False):
    """Import Gemini conversations markdown export."""
    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    path = Path(file_path)

    if not path.exists():
        print(f"  SKIP: {path} — not found")
        return

    session_id = f"gemini-{path.stem}"
    file_hash = _file_hash(str(path))

    existing = conn.execute(
        "SELECT file_hash FROM fed_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if existing and existing[0] == file_hash:
        print(f"  SKIP: {session_id} — already indexed")
        return

    turns = parse_gemini_md(str(path))
    if not turns:
        print(f"  SKIP: {session_id} — no turns extracted")
        return

    print(f"  {session_id}: {len(turns)} turns")

    if not dry_run:
        conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        conn.execute(
            """INSERT INTO sessions
               (id, agent, title, source_file, started_at, ended_at,
                turn_count, user_turn_count, ai_turn_count, noise_ratio, indexed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                "gemini-browser",
                turns[0]["content"][:100] if turns else "",
                str(path),
                now,
                now,
                len(turns),
                sum(1 for t in turns if t["role"] == "user"),
                sum(1 for t in turns if t["role"] == "ai"),
                0.0,
                now,
            ),
        )

        for turn in turns:
            conn.execute(
                """INSERT INTO turns
                   (session_id, role, timestamp, content, word_count)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, turn["role"], now, turn["content"], len(turn["content"].split())),
            )

        conn.execute(
            "INSERT OR REPLACE INTO fed_sessions (session_id, file_hash, fed_at) VALUES (?, ?, ?)",
            (session_id, file_hash, now),
        )
        conn.commit()

    conn.close()


def list_sources():
    """List all browser chat sources found on this machine."""
    print("=== Browser Chat Sources ===\n")

    # Z.AI HTML exports
    zai_files = list((Path.home() / "Downloads" / "02_WEB_SAVES").glob("zai-chat-*.html"))
    print(f"Z.AI HTML exports ({len(zai_files)} files):")
    for f in zai_files:
        print(f"  {f.name} ({f.stat().st_size / 1024:.0f}KB)")
    print()

    # Gemini conversations
    gemini_md = Path.home() / "Desktop" / "google-data-export" / "gemini-conversations.md"
    gemini_json = Path.home() / "Desktop" / "google-data-export" / "gemini-conversations.json"
    print("Gemini conversations:")
    if gemini_md.exists():
        print(f"  {gemini_md} ({gemini_md.stat().st_size / 1024:.0f}KB)")
    if gemini_json.exists():
        print(f"  {gemini_json} ({gemini_json.stat().st_size / 1024:.0f}KB)")
    print()

    # Gemini IDE conversations
    gemini_ide = Path.home() / ".gemini" / "antigravity-ide" / "conversations"
    if gemini_ide.exists():
        dbs = list(gemini_ide.glob("*.db"))
        print(f"Gemini IDE conversations ({len(dbs)} databases):")
        for db in dbs:
            print(f"  {db.name}")
    print()

    # Chat exporter scripts
    exporters = list((Path.home() / "Downloads" / "04_CODE").glob("*-chat-exporter*.js"))
    print(f"Chat exporter scripts ({len(exporters)} scripts):")
    for e in exporters:
        print(f"  {e.name}")
    print()

    # zcode (Z.AI) database
    zcode_db = Path.home() / ".zcode" / "cli" / "db" / "db.sqlite"
    if zcode_db.exists():
        print(f"Z.AI zcode database: {zcode_db} ({zcode_db.stat().st_size / 1024:.0f}KB)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import browser AI chats into sessions.sqlite")
    parser.add_argument("--import-zai", nargs="+", help="Z.AI HTML files to import")
    parser.add_argument("--import-gemini", help="Gemini conversations MD file to import")
    parser.add_argument("--list-sources", action="store_true", help="List all browser chat sources")
    parser.add_argument("--dry-run", action="store_true", help="Parse but don't write")
    args = parser.parse_args()

    if args.list_sources:
        list_sources()
    elif args.import_zai:
        import_zai(args.import_zai, dry_run=args.dry_run)
    elif args.import_gemini:
        import_gemini(args.import_gemini, dry_run=args.dry_run)
    else:
        parser.print_help()
