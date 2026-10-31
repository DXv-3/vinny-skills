#!/usr/bin/env python3
"""
daily_brief.py — Daily context surfacer health check.
Scans all sources, identifies what's stale, and outputs an actionable guide.

Usage:
    python3 daily_brief.py              # Run daily check
    python3 daily_brief.py --json       # Output as JSON
    python3 daily_brief.py --fix        # Auto-fix what can be auto-fixed
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / "sessions" / "sessions.sqlite"
SESSIONS_DIR = Path.home() / ".ai-memory" / "sessions"
KNOWLEDGE_DB = Path.home() / "knowledge-base" / "database.sqlite"
OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
HERMES_DB = Path.home() / "Documents" / ".hermes" / "state.db"
LOCAL_RECALL_DB = Path.home() / ".local-recall" / "events.sqlite"
SUBAGENT_DIR = Path.home() / ".ai-memory" / "subagent-sessions"
LAUNCHD_PLIST = Path.home() / "Library" / "LaunchAgents" / "com.vinnyos.context-surfacer.refresh.plist"


def check_sessions_index() -> dict:
    """Check sessions.sqlite freshness."""
    if not DB_PATH.exists():
        return {"status": "missing", "action": "Run session_feeder.py to create the index"}

    db = sqlite3.connect(str(DB_PATH))
    sessions = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    turns = db.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
    links = db.execute("SELECT COUNT(*) FROM file_mentions").fetchone()[0]
    last_feed = db.execute("SELECT value FROM meta WHERE key='last_feed_time'").fetchone()
    db.close()

    last_feed_str = last_feed[0] if last_feed else None
    if last_feed_str:
        try:
            last_feed_dt = datetime.fromisoformat(last_feed_str)
            hours_ago = (datetime.now(timezone.utc) - last_feed_dt).total_seconds() / 3600
        except Exception:
            hours_ago = 999
    else:
        hours_ago = 999

    # Count raw log files
    raw_logs = len(list(SESSIONS_DIR.glob("*.log"))) if SESSIONS_DIR.exists() else 0

    stale = hours_ago > 24
    return {
        "status": "stale" if stale else "fresh",
        "sessions": sessions,
        "turns": turns,
        "file_links": links,
        "raw_logs": raw_logs,
        "hours_since_feed": round(hours_ago, 1),
        "action": f"Run: python3 ~/.claude/skills/context-surfacer/sources/session_feeder.py" if stale else None,
    }


def check_knowledge_base() -> dict:
    """Check knowledge-base freshness."""
    if not KNOWLEDGE_DB.exists():
        return {"status": "missing", "action": "knowledge-base database not found"}

    db = sqlite3.connect(str(KNOWLEDGE_DB))
    items = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    if "sources" in tables:
        last_updated = db.execute("SELECT MAX(last_updated) FROM sources").fetchone()[0]
    elif "items" in tables:
        last_updated = db.execute("SELECT MAX(created_at) FROM items").fetchone()[0]
    else:
        last_updated = None
    db.close()

    if last_updated:
        try:
            last_dt = datetime.fromisoformat(last_updated.replace(" ", "T"))
            days_ago = (datetime.now(timezone.utc) - last_dt).days
        except Exception:
            days_ago = 999
    else:
        days_ago = 999

    stale = days_ago > 7
    return {
        "status": "stale" if stale else "fresh",
        "items": items,
        "days_since_update": days_ago,
        "action": "Run universal-pipeline ingest to refresh" if stale else None,
    }


def check_opencode_db() -> dict:
    """Check opencode.db exists and is accessible."""
    if not OPENCODE_DB.exists():
        return {"status": "missing", "action": "opencode.db not found"}

    size_gb = OPENCODE_DB.stat().st_size / (1024**3)

    db = sqlite3.connect(f"file:{OPENCODE_DB}?mode=ro", uri=True)
    sessions = db.execute("SELECT COUNT(*) FROM session").fetchone()[0]
    parts = db.execute("SELECT COUNT(*) FROM part").fetchone()[0]
    db.close()

    return {
        "status": "connected",
        "sessions": sessions,
        "parts": parts,
        "size_gb": round(size_gb, 1),
        "action": None,
    }


def check_local_recall() -> dict:
    """Check local-recall freshness."""
    if not LOCAL_RECALL_DB.exists():
        return {"status": "missing", "action": "local-recall database not found"}

    db = sqlite3.connect(str(LOCAL_RECALL_DB))
    events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    last_ingest = db.execute("SELECT MAX(ingested_at) FROM events").fetchone()[0]
    db.close()

    if last_ingest:
        try:
            last_dt = datetime.fromisoformat(last_ingest.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - last_dt).days
        except Exception:
            days_ago = 999
    else:
        days_ago = 999

    stale = days_ago > 3
    return {
        "status": "stale" if stale else "fresh",
        "events": events,
        "days_since_ingest": days_ago,
        "action": "Run: cd ~/Projects/local-recall && python3 -m local_recall ingest all" if stale else None,
    }


def check_subagent_sessions() -> dict:
    """Check subagent-sessions freshness."""
    if not SUBAGENT_DIR.exists():
        return {"status": "missing", "action": "subagent-sessions directory not found"}

    md_files = list(SUBAGENT_DIR.rglob("*.md"))
    md_files = [f for f in md_files if f.name != "master-index.json"]
    unindexed = len(md_files)
    indexed = 0

    if not DB_PATH.exists():
        return {
            "status": "stale" if unindexed else "fresh",
            "total_files": len(md_files),
            "indexed": 0,
            "unindexed": unindexed,
            "action": f"Run: python3 ~/.claude/skills/context-surfacer/sources/subagent.py ({unindexed} new files)" if unindexed else None,
        }

    try:
        db = sqlite3.connect(str(DB_PATH))
        indexed = db.execute(
            "SELECT COUNT(*) FROM sessions WHERE agent='subagent'"
        ).fetchone()[0]
        db.close()
    except sqlite3.Error:
        indexed = 0

    unindexed = len(md_files) - indexed

    return {
        "status": "stale" if unindexed > 0 else "fresh",
        "total_files": len(md_files),
        "indexed": indexed,
        "unindexed": unindexed,
        "action": f"Run: python3 ~/.claude/skills/context-surfacer/sources/subagent.py ({unindexed} new files)" if unindexed > 0 else None,
    }


def check_surfacer_mcp() -> dict:
    """Check if surfacer is wired in opencode.json."""
    config_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if not config_path.exists():
        return {"status": "missing", "action": "opencode.json not found"}

    try:
        config = json.loads(config_path.read_text())
        wired = "context-surfacer" in config.get("mcp", {})
    except Exception:
        wired = False

    return {
        "status": "wired" if wired else "not_wired",
        "action": "Add context-surfacer to opencode.json mcp section" if not wired else None,
    }


def check_launchd() -> dict:
    """Check if launchd agent is installed."""
    installed = LAUNCHD_PLIST.exists()
    return {
        "status": "installed" if installed else "removed",
        "action": None,
    }


def generate_brief(fix: bool = False) -> dict:
    """Generate the daily brief."""
    checks = {
        "sessions_index": check_sessions_index(),
        "knowledge_base": check_knowledge_base(),
        "opencode_db": check_opencode_db(),
        "local_recall": check_local_recall(),
        "subagent_sessions": check_subagent_sessions(),
        "surfacer_mcp": check_surfacer_mcp(),
        "launchd": check_launchd(),
    }

    # Collect actions
    actions = []
    for name, check in checks.items():
        if check.get("action"):
            actions.append({"source": name, "action": check["action"]})

    # Auto-fix if requested
    fixed = []
    if fix and actions:
        for item in actions:
            if "session_feeder.py" in item["action"]:
                import subprocess
                subprocess.run(["python3", str(Path.home() / ".claude/skills/context-surfacer/sources/session_feeder.py")], capture_output=True)
                fixed.append(item["source"])
            elif "subagent.py" in item["action"]:
                import subprocess
                subprocess.run(["python3", str(Path.home() / ".claude/skills/context-surfacer/sources/subagent.py")], capture_output=True)
                fixed.append(item["source"])

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "actions": actions,
        "fixed": fixed,
        "summary": f"{len(actions)} items need attention" if actions else "All sources fresh",
    }


def print_brief(brief: dict):
    """Print the daily brief as a human-readable guide."""
    print("=" * 60)
    print("  CONTEXT SURFACER — DAILY BRIEF")
    print(f"  {brief['timestamp']}")
    print("=" * 60)
    print()

    for name, check in brief["checks"].items():
        status = check["status"]
        icon = {"fresh": "✅", "stale": "⚠️", "missing": "❌", "connected": "✅", "wired": "✅", "not_wired": "⚠️", "removed": "✅", "installed": "ℹ️"}.get(status, "❓")
        label = name.replace("_", " ").title()
        print(f"  {icon} {label}: {status}")

        # Show key stats
        for key in ["sessions", "turns", "items", "events", "parts", "hours_since_feed", "days_since_update", "days_since_ingest", "unindexed"]:
            if key in check and check[key] is not None:
                print(f"     {key}: {check[key]}")

        if check.get("action"):
            print(f"     → {check['action']}")
        print()

    if brief["actions"]:
        print("-" * 60)
        print("  TODAY'S ACTIONS:")
        print("-" * 60)
        for i, item in enumerate(brief["actions"], 1):
            print(f"  {i}. [{item['source']}] {item['action']}")
        print()
    else:
        print("  ✅ All sources fresh. Nothing to do today.")
        print()

    if brief["fixed"]:
        print(f"  Auto-fixed: {', '.join(brief['fixed'])}")
        print()

    print("=" * 60)


if __name__ == "__main__":
    fix = "--fix" in sys.argv
    as_json = "--json" in sys.argv

    brief = generate_brief(fix=fix)

    if as_json:
        print(json.dumps(brief, indent=2, default=str))
    else:
        print_brief(brief)
