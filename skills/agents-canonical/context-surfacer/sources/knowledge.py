"""
Wrapper around knowledge-base FTS5 search.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "knowledge-base" / "database.sqlite"


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def search_knowledge(
    query: str,
    source_type: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """FTS5 search on knowledge-base items.

    Args:
        query: FTS5 search term
        source_type: Filter by type (article, youtube, browser)
        limit: Max results

    Returns:
        List of dicts with id, title, source_type, url, date, snippet
    """
    conn = _get_db()
    try:
        sql = """
            SELECT
                i.id,
                i.title,
                i.source_type,
                i.url,
                i.date,
                i.word_count,
                snippet(items_fts, 1, '>>>', '<<<', '...', 40) as snippet
            FROM items_fts f
            JOIN items i ON i.rowid = f.rowid
            WHERE items_fts MATCH ?
        """
        params: list = [query]

        if source_type:
            sql += " AND i.source_type = ?"
            params.append(source_type)

        sql += " LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching knowledge-base: {q}")
    for r in search_knowledge(q, limit=5):
        print(f"  [{r['source_type']}] {r['title'][:60]} — {r['snippet'][:80]}")
