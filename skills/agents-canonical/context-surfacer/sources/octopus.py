"""
Search octopus journal entries and decisions by keyword.
Directly queries octopus SQLite database (no MCP needed).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

OCTOPUS_DB = Path.home() / "Documents" / "octopus" / "data" / "octopus.db"


def _get_db() -> sqlite3.Connection | None:
    if not OCTOPUS_DB.exists():
        return None
    conn = sqlite3.connect(str(OCTOPUS_DB))
    conn.row_factory = sqlite3.Row
    return conn


def search_octopus(query: str, limit: int = 20) -> list[dict]:
    """Search octopus journal and decisions for query matches.

    Returns:
        List of dicts with type, agent, action, summary, timestamp
    """
    conn = _get_db()
    if conn is None:
        return []

    try:
        results = []

        # Search journal
        try:
            rows = conn.execute(
                """SELECT agent, action, project_path, summary, created_at
                   FROM journal
                   WHERE action LIKE ? OR summary LIKE ? OR project_path LIKE ?
                   ORDER BY created_at DESC LIMIT ?""",
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            ).fetchall()
            for row in rows:
                results.append({
                    "type": "journal",
                    "agent": row["agent"],
                    "action": row["action"],
                    "project": row["project_path"],
                    "summary": row["summary"],
                    "timestamp": row["created_at"],
                })
        except sqlite3.OperationalError:
            pass

        # Search decisions
        try:
            rows = conn.execute(
                """SELECT agent, decision, rationale, created_at
                   FROM decisions
                   WHERE decision LIKE ? OR rationale LIKE ?
                   ORDER BY created_at DESC LIMIT ?""",
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
            for row in rows:
                results.append({
                    "type": "decision",
                    "agent": row["agent"],
                    "decision": row["decision"],
                    "rationale": row["rationale"],
                    "timestamp": row["created_at"],
                })
        except sqlite3.OperationalError:
            pass

        return results[:limit]
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching octopus: {q}")
    for r in search_octopus(q, limit=5):
        print(f"  [{r['type']}] {r.get('agent', '?')}: {r.get('action') or r.get('decision', '')[:60]}")
