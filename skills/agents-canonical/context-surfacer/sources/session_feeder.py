#!/usr/bin/env python3
"""
session_feeder.py — Parse 496 session logs → write to sessions.sqlite.

Usage:
    python3 session_feeder.py              # Feed all new sessions
    python3 session_feeder.py --dry-run    # Parse but don't write
    python3 session_feeder.py --force      # Re-feed all files (ignore hash cache)
    python3 session_feeder.py --rebuild-links  # Rebuild file_mentions from all turns
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_parser import parse_session
from file_links import init_file_mentions, populate_file_mentions, rebuild_all_links

SESSIONS_DIR = Path.home() / ".ai-memory" / "sessions"
DB_PATH = Path.home() / "sessions" / "sessions.sqlite"


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    init_file_mentions(conn)
    return conn


def is_already_fed(conn: sqlite3.Connection, session_id: str, file_hash: str) -> bool:
    row = conn.execute(
        "SELECT file_hash FROM fed_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        return False
    return row[0] == file_hash


def mark_fed(conn: sqlite3.Connection, session_id: str, file_hash: str):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO fed_sessions (session_id, file_hash, fed_at) VALUES (?, ?, ?)",
        (session_id, file_hash, now),
    )


def feed_all(dry_run: bool = False, force: bool = False):
    conn = get_db()
    log_files = sorted(SESSIONS_DIR.glob("*.log"))
    total = len(log_files)
    print(f"Found {total} session logs in {SESSIONS_DIR}")

    fed_count = 0
    skipped_count = 0
    failed_count = 0
    total_turns = 0
    total_user = 0
    total_ai = 0
    total_noise = 0
    total_links = 0
    failures: list[str] = []

    for i, log_file in enumerate(log_files):
        session_id = log_file.stem

        try:
            parsed = parse_session(str(log_file))
        except Exception as e:
            failed_count += 1
            msg = f"FAIL: {log_file.name} — {e}"
            failures.append(msg)
            print(f"  [{i+1}/{total}] {msg}")
            continue

        if parsed is None:
            failed_count += 1
            msg = f"SKIP: {log_file.name} — no turns extracted"
            failures.append(msg)
            continue

        # Incremental: check hash
        if not force and is_already_fed(conn, session_id, parsed.file_hash):
            skipped_count += 1
            continue

        if not dry_run:
            # Delete old data for this session if re-feeding
            conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.execute("DELETE FROM file_mentions WHERE session_id = ?", (session_id,))

            # Insert session
            conn.execute(
                """INSERT INTO sessions
                   (id, agent, title, source_file, started_at, ended_at,
                    turn_count, user_turn_count, ai_turn_count, noise_ratio, indexed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    parsed.agent,
                    parsed.title,
                    parsed.source_file,
                    parsed.started_at,
                    parsed.ended_at,
                    len(parsed.turns),
                    sum(1 for t in parsed.turns if t.role == "user" and not t.is_noise),
                    sum(1 for t in parsed.turns if t.role == "ai" and not t.is_noise),
                    parsed.noise_ratio,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            # Insert turns (skip noise) + populate file_mentions
            for turn in parsed.turns:
                if not turn.is_noise:
                    conn.execute(
                        """INSERT INTO turns
                           (session_id, role, timestamp, content, word_count)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            session_id,
                            turn.role,
                            turn.timestamp,
                            turn.content,
                            len(turn.content.split()),
                        ),
                    )
                    # Extract file paths and populate back-links
                    populate_file_mentions(conn, session_id, turn.content, turn.timestamp)

            mark_fed(conn, session_id, parsed.file_hash)

        fed_count += 1
        total_turns += len(parsed.turns)
        total_user += sum(1 for t in parsed.turns if t.role == "user" and not t.is_noise)
        total_ai += sum(1 for t in parsed.turns if t.role == "ai" and not t.is_noise)
        total_noise += sum(1 for t in parsed.turns if t.is_noise)

        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(
                f"  [{i+1}/{total}] {session_id} — "
                f"{len(parsed.turns)} turns, "
                f"{sum(1 for t in parsed.turns if t.is_noise)} noise"
            )
            if not dry_run:
                conn.commit()

    if not dry_run:
        # Update meta
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_feed_time', ?)",
            (datetime.now(timezone.utc).isoformat(),),
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('total_sessions', ?)",
            (str(fed_count),),
        )
        total_links = conn.execute("SELECT COUNT(*) FROM file_mentions").fetchone()[0]
        conn.commit()

    conn.close()

    mode = "DRY RUN" if dry_run else "FED"
    print(f"\n=== {mode} COMPLETE ===")
    print(f"  Fed:       {fed_count}")
    print(f"  Skipped:   {skipped_count} (already indexed, same hash)")
    print(f"  Failed:    {failed_count}")
    print(f"  Turns:     {total_turns} ({total_user} user, {total_ai} ai)")
    print(f"  Noise:     {total_noise} lines filtered")
    print(f"  Links:     {total_links} file→session back-links")

    if failures:
        print(f"\n  Failures:")
        for f in failures[:20]:
            print(f"    {f}")
        if len(failures) > 20:
            print(f"    ... and {len(failures) - 20} more")

    if not dry_run:
        print(f"\n  Database: {DB_PATH} ({DB_PATH.stat().st_size / 1024:.0f}KB)")


if __name__ == "__main__":
    if "--rebuild-links" in sys.argv:
        print("Rebuilding file_mentions from all turns...")
        rebuild_all_links()
    else:
        dry_run = "--dry-run" in sys.argv
        force = "--force" in sys.argv
        feed_all(dry_run=dry_run, force=force)
