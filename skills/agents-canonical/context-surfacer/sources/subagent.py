"""
Parse ~/.ai-memory/subagent-sessions/**/*.md files into sessions.sqlite.
Each file has: # Session, ## Prompt, ## Result, ## Files Referenced, ## Key Decisions.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_DIR = Path.home() / ".ai-memory" / "subagent-sessions"
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


def parse_subagent_md(file_path: str) -> dict | None:
    """Parse a subagent session markdown file.

    Returns dict with title, prompt, result, files_referenced, decisions.
    """
    try:
        text = Path(file_path).read_text(errors="replace")
    except Exception:
        return None

    result = {"title": "", "prompt": "", "result": "", "files_referenced": "", "decisions": ""}

    # Extract title from # Session: <name> or filename
    m = re.search(r"^#\s+Session:\s*(.+)$", text, re.MULTILINE)
    if m:
        result["title"] = m.group(1).strip()
    else:
        result["title"] = Path(file_path).stem

    # Extract sections
    sections = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    current_section = None
    for part in sections:
        part = part.strip()
        if part.lower() == "prompt":
            current_section = "prompt"
        elif part.lower() == "result":
            current_section = "result"
        elif "files referenced" in part.lower():
            current_section = "files_referenced"
        elif "key decisions" in part.lower() or "decisions" in part.lower():
            current_section = "decisions"
        elif current_section and part:
            if result[current_section]:
                result[current_section] += "\n\n" + part
            else:
                result[current_section] = part

    return result


def feed_subagent_sessions(dry_run: bool = False) -> int:
    """Parse all subagent session markdowns and write to sessions.sqlite.

    Returns number of sessions fed.
    """
    if not SESSIONS_DIR.exists():
        return 0

    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    fed = 0

    for md_file in SESSIONS_DIR.rglob("*.md"):
        if md_file.name == "master-index.json":
            continue

        session_id = f"subagent-{md_file.stem}"
        file_hash = _file_hash(str(md_file))

        # Check if already fed
        existing = conn.execute(
            "SELECT file_hash FROM fed_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if existing and existing[0] == file_hash:
            continue

        parsed = parse_subagent_md(str(md_file))
        if not parsed or not parsed["prompt"]:
            continue

        print(f"  {session_id}: {parsed['title'][:60]}")

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
                    "subagent",
                    parsed["title"],
                    str(md_file),
                    now,
                    now,
                    2 if parsed["result"] else 1,
                    1,
                    1 if parsed["result"] else 0,
                    0.0,
                    now,
                ),
            )

            # User turn (prompt)
            if parsed["prompt"]:
                conn.execute(
                    """INSERT INTO turns (session_id, role, timestamp, content, word_count)
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, "user", now, parsed["prompt"], len(parsed["prompt"].split())),
                )

            # AI turn (result)
            if parsed["result"]:
                conn.execute(
                    """INSERT INTO turns (session_id, role, timestamp, content, word_count)
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, "ai", now, parsed["result"], len(parsed["result"].split())),
                )

            conn.execute(
                "INSERT OR REPLACE INTO fed_sessions (session_id, file_hash, fed_at) VALUES (?, ?, ?)",
                (session_id, file_hash, now),
            )

        fed += 1

    if not dry_run:
        conn.commit()
    conn.close()
    return fed


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    count = feed_subagent_sessions(dry_run=dry_run)
    print(f"{'Would feed' if dry_run else 'Fed'}: {count} subagent sessions")
