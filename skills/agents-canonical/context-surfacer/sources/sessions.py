"""
Search interface for sessions.sqlite — FTS5 full-text search on normalized turns.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "sessions" / "sessions.sqlite"


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def search_sessions(
    query: str,
    agent: str | None = None,
    after: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """FTS5 search on turns, optionally filtered by agent and date.

    Args:
        query: FTS5 search term
        agent: Filter by agent name (opencode, grok, kilo, ide, gemini, codex, ollama)
        after: ISO date string — only return turns after this date
        limit: Max results

    Returns:
        List of dicts with session_id, agent, role, timestamp, snippet, rank
    """
    conn = _get_db()
    try:
        # Build query
        sql = """
            SELECT
                s.id as session_id,
                s.agent,
                s.title,
                t.role,
                t.timestamp,
                snippet(turns_fts, 0, '>>>', '<<<', '...', 40) as snippet,
                rank
            FROM turns_fts f
            JOIN turns t ON t.id = f.rowid
            JOIN sessions s ON s.id = t.session_id
            WHERE turns_fts MATCH ?
        """
        params: list = [query]

        if agent:
            sql += " AND s.agent = ?"
            params.append(agent)

        if after:
            sql += " AND t.timestamp > ?"
            params.append(after)

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_session_turns(session_id: str, limit: int = 50) -> list[dict]:
    """Get all turns for a specific session."""
    conn = _get_db()
    try:
        rows = conn.execute(
            """SELECT role, timestamp, content, word_count
               FROM turns WHERE session_id = ?
               ORDER BY timestamp LIMIT ?""",
            (session_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_session_stats() -> dict:
    """Get aggregate stats across all indexed sessions."""
    conn = _get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        turns = conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
        user_turns = conn.execute(
            "SELECT COUNT(*) FROM turns WHERE role = 'user'"
        ).fetchone()[0]
        ai_turns = conn.execute(
            "SELECT COUNT(*) FROM turns WHERE role = 'ai'"
        ).fetchone()[0]
        by_agent = conn.execute(
            "SELECT agent, COUNT(*) as count FROM sessions GROUP BY agent ORDER BY count DESC"
        ).fetchall()
        last_feed = conn.execute(
            "SELECT value FROM meta WHERE key = 'last_feed_time'"
        ).fetchone()

        return {
            "total_sessions": total,
            "total_turns": turns,
            "user_turns": user_turns,
            "ai_turns": ai_turns,
            "by_agent": {row["agent"]: row["count"] for row in by_agent},
            "last_feed": last_feed[0] if last_feed else None,
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching: {q}")
    for r in search_sessions(q, limit=5):
        print(f"  [{r['agent']}] {r['role']}: {r['snippet'][:100]}")
