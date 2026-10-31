"""
Generic HTML chat exporter adapter.
Handles Perplexity, DeepSeek, TwinMind, and any HTML chat export
that uses role-based class names or data attributes.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / "sessions" / "sessions.sqlite"

# Known role class patterns for each exporter
ROLE_PATTERNS = {
    "perplexity": [
        (r'<div[^>]*data-testid="userMessage"[^>]*>(.*?)</div>', "user"),
        (r'<div[^>]*data-testid="assistantMessage"[^>]*>(.*?)</div>', "ai"),
        (r'<div[^>]*class="[^"]*prose[^"]*"[^>]*>(.*?)</div>', "ai"),
    ],
    "deepseek": [
        (r'<div[^>]*class="[^"]*ds-chat-message[^"]*user[^"]*"[^>]*>(.*?)</div>', "user"),
        (r'<div[^>]*class="[^"]*ds-chat-message[^"]*assistant[^"]*"[^>]*>(.*?)</div>', "ai"),
    ],
    "twinmind": [
        (r'<div[^>]*class="[^"]*message-content[^"]*"[^>]*data-role="user"[^>]*>(.*?)</div>', "user"),
        (r'<div[^>]*class="[^"]*message-content[^"]*"[^>]*data-role="assistant"[^>]*>(.*?)</div>', "ai"),
    ],
    "generic": [
        (r'<div[^>]*class="[^"]*(?:user|human|me)[^"]*"[^>]*>(.*?)</div>', "user"),
        (r'<div[^>]*class="[^"]*(?:assistant|bot|ai|model)[^"]*"[^>]*>(.*?)</div>', "ai"),
        (r'<div[^>]*data-role="user"[^>]*>(.*?)</div>', "user"),
        (r'<div[^>]*data-role="assistant"[^>]*>(.*?)</div>', "ai"),
    ],
}


def _file_hash(path: str) -> str:
    try:
        data = Path(path).read_bytes()[:1000]
        return hashlib.md5(data).hexdigest()
    except Exception:
        return ""


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _detect_exporter(html: str) -> str:
    """Detect which exporter generated this HTML."""
    if "perplexity" in html.lower() or "data-testid=\"userMessage\"" in html:
        return "perplexity"
    if "ds-chat-message" in html or "deepseek" in html.lower():
        return "deepseek"
    if "twinmind" in html.lower() or "data-role=\"user\"" in html:
        return "twinmind"
    return "generic"


def parse_html_chat(file_path: str) -> list[dict]:
    """Parse any HTML chat export into turns."""
    try:
        html = Path(file_path).read_text(errors="replace")
    except Exception:
        return []

    exporter = _detect_exporter(html)
    patterns = ROLE_PATTERNS.get(exporter, ROLE_PATTERNS["generic"])

    turns = []
    for pattern_str, role in patterns:
        for m in re.finditer(pattern_str, html, re.DOTALL):
            content = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if content and len(content) > 5:
                turns.append({"role": role, "content": content})

    return turns


def import_html_chat(file_path: str, dry_run: bool = False) -> bool:
    """Import an HTML chat export into sessions.sqlite."""
    path = Path(file_path)
    if not path.exists():
        print(f"  SKIP: {path} — not found")
        return False

    session_id = f"chat-{path.stem}"
    file_hash = _file_hash(str(path))

    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()

    # Check if already fed
    existing = conn.execute(
        "SELECT file_hash FROM fed_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if existing and existing[0] == file_hash:
        print(f"  SKIP: {session_id} — already indexed")
        conn.close()
        return False

    turns = parse_html_chat(str(path))
    if not turns:
        print(f"  SKIP: {session_id} — no turns extracted")
        conn.close()
        return False

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
                "browser-chat",
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
    return True


def import_all_html_chats(dry_run: bool = False) -> int:
    """Import all HTML chat exports from known locations."""
    count = 0

    # Z.AI chats
    zai_dir = Path.home() / "Downloads" / "02_WEB_SAVES"
    if zai_dir.exists():
        for f in zai_dir.glob("zai-chat-*.html"):
            if import_html_chat(str(f), dry_run):
                count += 1

    # Perplexity, DeepSeek, TwinMind — check Downloads
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        for pattern in ["*perplexity*chat*.html", "*deepseek*chat*.html", "*twinmind*chat*.html"]:
            for f in downloads.glob(pattern):
                if import_html_chat(str(f), dry_run):
                    count += 1

    return count


if __name__ == "__main__":
    import sys

    if "--import-all" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        count = import_all_html_chats(dry_run=dry_run)
        print(f"Imported {count} HTML chat files")
    elif len(sys.argv) > 1:
        import_html_chat(sys.argv[1], dry_run="--dry-run" in sys.argv)
    else:
        print("Usage: python3 chat_exporters.py <file.html>")
        print("       python3 chat_exporters.py --import-all [--dry-run]")
