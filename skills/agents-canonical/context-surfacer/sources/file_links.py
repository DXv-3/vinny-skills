"""
File→session back-links. Tracks which sessions mention which files.
Enables surf_related(path) — "which sessions discuss this file?"
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "sessions" / "sessions.sqlite"

# Regex to extract file paths from turn content
FILE_RE = re.compile(
    r"(?:"
    r"~/[\w\-./]+"
    r"|/Users/vinnygilberti/[\w\-./]+"
    r"|[\w\-]+\.(?:py|js|ts|md|sqlite|json|html|sh|swift|yaml|toml|cfg)"
    r")"
)


def init_file_mentions(db: sqlite3.Connection):
    """Create file_mentions table if it doesn't exist."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS file_mentions (
            file_path TEXT NOT NULL,
            session_id TEXT NOT NULL,
            mentioned_at TEXT,
            context TEXT,
            PRIMARY KEY (file_path, session_id)
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_file_mentions_path ON file_mentions(file_path)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_file_mentions_session ON file_mentions(session_id)")
    db.commit()


def extract_file_paths(content: str) -> list[str]:
    """Extract file paths from text content."""
    matches = FILE_RE.findall(content)
    # Deduplicate and filter out noise
    seen = set()
    paths = []
    for m in matches:
        # Skip common false positives
        if any(skip in m for skip in [".git/", "node_modules/", "__pycache__/", ".venv/"]):
            continue
        if m not in seen:
            seen.add(m)
            paths.append(m)
    return paths


def populate_file_mentions(db: sqlite3.Connection, session_id: str, content: str, timestamp: str):
    """Extract file paths from content and insert into file_mentions."""
    paths = extract_file_paths(content)
    for path in paths:
        db.execute(
            """INSERT OR IGNORE INTO file_mentions (file_path, session_id, mentioned_at, context)
               VALUES (?, ?, ?, ?)""",
            (path, session_id, timestamp, content[:200]),
        )


def rebuild_all_links():
    """Re-scan all sessions and rebuild file_mentions from scratch."""
    db = sqlite3.connect(str(DB_PATH))
    init_file_mentions(db)
    db.execute("DELETE FROM file_mentions")

    rows = db.execute("SELECT id, content FROM turns").fetchall()
    count = 0
    for row in rows:
        session_id = row[0]
        content = row[1]
        if content:
            populate_file_mentions(db, session_id, content, "")
            count += 1

    db.commit()
    total_links = db.execute("SELECT COUNT(*) FROM file_mentions").fetchone()[0]
    db.close()
    print(f"Rebuilt file_mentions: {count} turns scanned, {total_links} links created")
    return total_links


def search_file_mentions(file_path: str, limit: int = 20) -> list[dict]:
    """Find all sessions that mention a given file path.

    Returns:
        List of dicts with session_id, agent, title, context
    """
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    try:
        # Try exact match first, then partial
        sql = """
            SELECT fm.file_path, fm.session_id, fm.context,
                   s.agent, s.title
            FROM file_mentions fm
            JOIN sessions s ON s.id = fm.session_id
            WHERE fm.file_path = ?
            LIMIT ?
        """
        rows = db.execute(sql, (file_path, limit)).fetchall()
        if rows:
            return [dict(row) for row in rows]

        # Partial match
        sql = """
            SELECT fm.file_path, fm.session_id, fm.context,
                   s.agent, s.title
            FROM file_mentions fm
            JOIN sessions s ON s.id = fm.session_id
            WHERE fm.file_path LIKE ?
            LIMIT ?
        """
        rows = db.execute(sql, (f"%{file_path}%", limit)).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        rebuild_all_links()
    elif len(sys.argv) > 1:
        results = search_file_mentions(sys.argv[1])
        print(f"Sessions mentioning '{sys.argv[1]}':")
        for r in results:
            print(f"  [{r['agent']}] {r['title'][:50]} — {r['file_path']}")
    else:
        print("Usage: python3 file_links.py <file_path>")
        print("       python3 file_links.py --rebuild")
