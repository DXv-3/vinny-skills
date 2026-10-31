"""
Read-only adapter for ~/Documents/.hermes/state.db.
Hermes has FTS5 + trigram search on sessions and messages. NEVER modifies the DB.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

HERMES_DB = Path.home() / "Documents" / ".hermes" / "state.db"


def _get_db() -> sqlite3.Connection | None:
    if not HERMES_DB.exists():
        return None
    conn = sqlite3.connect(f"file:{HERMES_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def search_hermes(query: str, limit: int = 20) -> list[dict]:
    """Search hermes state.db using FTS5.

    Returns:
        List of dicts with session_id, title, role, content, timestamp
    """
    conn = _get_db()
    if conn is None:
        return []

    try:
        # Try FTS5 first
        sql = """
            SELECT
                s.id as session_id,
                s.title,
                m.role,
                m.content,
                datetime(m.created_at, 'unixepoch') as message_time
            FROM messages_fts f
            JOIN messages m ON m.rowid = f.rowid
            JOIN sessions s ON s.id = m.session_id
            WHERE messages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        rows = conn.execute(sql, (query, limit)).fetchall()
        if rows:
            return [dict(row) for row in rows]

        # Fallback to LIKE search
        sql = """
            SELECT
                s.id as session_id,
                s.title,
                m.role,
                m.content,
                datetime(m.created_at, 'unixepoch') as message_time
            FROM messages m
            JOIN sessions s ON s.id = m.session_id
            WHERE m.content LIKE ?
            ORDER BY m.created_at DESC
            LIMIT ?
        """
        rows = conn.execute(sql, (f"%{query}%", limit)).fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []
    finally:
        conn.close()


def get_recent_sessions(limit: int = 10) -> list[dict]:
    """Get recent hermes sessions."""
    conn = _get_db()
    if conn is None:
        return []

    try:
        sql = """
            SELECT id, title, model, message_count,
                   datetime(started_at, 'unixepoch') as started
            FROM sessions
            ORDER BY started_at DESC
            LIMIT ?
        """
        rows = conn.execute(sql, (limit,)).fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching hermes: {q}")
    for r in search_hermes(q, limit=5):
        print(f"  [{r.get('role', '?')}] {r.get('content', '')[:80]}")
