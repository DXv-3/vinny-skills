"""
Read-only adapter for ~/.local/share/opencode/opencode.db.
Extracts text parts with session context. NEVER modifies opencode.db.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"


def _get_db() -> sqlite3.Connection | None:
    if not OPENCODE_DB.exists():
        return None
    conn = sqlite3.connect(f"file:{OPENCODE_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def search_opencode_db(query: str, limit: int = 20) -> list[dict]:
    """Search opencode.db text parts for query matches.

    Returns:
        List of dicts with session_id, title, created_at, content, match_snippet
    """
    conn = _get_db()
    if conn is None:
        return []

    try:
        # Search text parts by content match
        sql = """
            SELECT
                s.id as session_id,
                s.title,
                datetime(s.time_created / 1000, 'unixepoch') as created_at,
                json_extract(p.data, '$.text') as content,
                p.time_created as part_time
            FROM part p
            JOIN message m ON m.id = p.message_id
            JOIN session s ON s.id = p.session_id
            WHERE json_extract(p.data, '$.type') = 'text'
            AND json_extract(p.data, '$.text') IS NOT NULL
            AND LENGTH(json_extract(p.data, '$.text')) > 10
            AND json_extract(p.data, '$.text') LIKE ?
            ORDER BY s.time_created DESC
            LIMIT ?
        """
        rows = conn.execute(sql, (f"%{query}%", limit)).fetchall()

        results = []
        for row in rows:
            content = row["content"] or ""
            # Create snippet around match
            idx = content.lower().find(query.lower())
            if idx >= 0:
                start = max(0, idx - 80)
                end = min(len(content), idx + len(query) + 80)
                snippet = ">>>" + content[start:end] + "<<<"
            else:
                snippet = content[:160]

            results.append({
                "session_id": row["session_id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "content": content[:500],
                "snippet": snippet,
                "source": "opencode_db",
            })

        return results
    except Exception:
        return []
    finally:
        conn.close()


def get_session_parts(session_id: str, limit: int = 50) -> list[dict]:
    """Get all text parts for a specific opencode session."""
    conn = _get_db()
    if conn is None:
        return []

    try:
        sql = """
            SELECT
                json_extract(p.data, '$.text') as content,
                p.time_created as part_time
            FROM part p
            WHERE p.session_id = ?
            AND json_extract(p.data, '$.type') = 'text'
            AND json_extract(p.data, '$.text') IS NOT NULL
            ORDER BY p.time_created
            LIMIT ?
        """
        rows = conn.execute(sql, (session_id, limit)).fetchall()
        return [{"content": row["content"], "time": row["part_time"]} for row in rows]
    except Exception:
        return []
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching opencode.db: {q}")
    for r in search_opencode_db(q, limit=5):
        print(f"  [{r['title'][:50]}] {r['snippet'][:80]}")
