#!/usr/bin/env python3
"""
surf.py — Context Surfacer: query router that searches all data sources
on this Mac and returns unified, relevance-scored results.

Usage:
    python3 surf.py "your query"
    python3 surf.py "your query" --depth deep
    python3 surf.py "your query" --source sessions
    python3 surf.py "your query" --json
    python3 surf.py --mcp   # Run as MCP server
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add parent dir for source imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sources.sessions import search_sessions, get_session_stats
from sources.knowledge import search_knowledge
from sources.files import search_files
from sources.state import search_state
from sources.octopus import search_octopus
from sources.skills import search_skills
from sources.code import search_code
from sources.opencode_db import search_opencode_db
from sources.hermes_db import search_hermes
from sources.subagent import feed_subagent_sessions
from sources.file_links import search_file_mentions, init_file_mentions
from sources.chat_exporters import import_all_html_chats

# ─── Configurable Scoring Weights ───

WEIGHTS = {
    "content_match": 0.3,
    "source_authority": {
        "sessions": 0.15,
        "opencode_db": 0.15,
        "hermes_db": 0.12,
        "subagent": 0.10,
        "knowledge": 0.15,
        "code": 0.15,
        "state": 0.10,
        "files": 0.05,
        "skills": 0.05,
        "octopus": 0.10,
    },
    "recency_half_life_days": 30,
    "noise_penalty": 0.3,
}

# ─── Source Definitions ───

ALL_SOURCES = [
    "sessions", "opencode_db", "hermes_db", "subagent",
    "knowledge", "code", "state", "files", "skills", "octopus",
]

QUICK_SOURCES = ["sessions", "opencode_db", "knowledge", "files"]


def _score_result(result: dict, query: str, source: str) -> float:
    """Score a result based on content match, source authority, and recency."""
    score = 0.0

    # Content match
    content = (
        result.get("content", "")
        or result.get("snippet", "")
        or result.get("match_line", "")
        or result.get("action", "")
        or result.get("decision", "")
        or ""
    )
    if query.lower() in content.lower():
        score += WEIGHTS["content_match"]

    # Source authority
    score += WEIGHTS["source_authority"].get(source, 0.05)

    # Recency
    ts = result.get("timestamp") or result.get("date") or result.get("created_at") or ""
    if ts:
        try:
            from datetime import datetime, timezone
            if "T" in ts:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            elif "-" in ts and len(ts) == 10:
                dt = datetime.strptime(ts, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            else:
                dt = None
            if dt:
                days_old = (datetime.now(timezone.utc) - dt).days
                half_life = WEIGHTS["recency_half_life_days"]
                recency = max(0, 0.15 * (0.5 ** (days_old / half_life)))
                score += recency
        except Exception:
            pass

    # Noise penalty
    if result.get("is_noise"):
        score -= WEIGHTS["noise_penalty"]

    return min(max(score, 0.0), 1.0)


def _search_source(source: str, query: str) -> tuple[list[dict], str | None]:
    """Search a single source, returning results and an optional error."""
    results = []
    try:
        if source == "sessions":
            for r in search_sessions(query, limit=10):
                r["source"] = "sessions"
                results.append(r)
        elif source == "opencode_db":
            for r in search_opencode_db(query, limit=10):
                r["source"] = "opencode_db"
                results.append(r)
        elif source == "hermes_db":
            for r in search_hermes(query, limit=10):
                r["source"] = "hermes_db"
                results.append(r)
        elif source == "subagent":
            for r in search_sessions(query, limit=10):
                if r.get("session_id", "").startswith("subagent-"):
                    r["source"] = "subagent"
                    results.append(r)
        elif source == "knowledge":
            for r in search_knowledge(query, limit=10):
                r["source"] = "knowledge"
                results.append(r)
        elif source == "files":
            for r in search_files(query, limit=10):
                r["source"] = "files"
                results.append(r)
        elif source == "state":
            for r in search_state(query):
                r["source"] = "state"
                results.append(r)
        elif source == "octopus":
            for r in search_octopus(query, limit=10):
                r["source"] = "octopus"
                results.append(r)
        elif source == "skills":
            for r in search_skills(query, limit=10):
                r["source"] = "skills"
                results.append(r)
        elif source == "code":
            for r in search_code(query, limit=10):
                r["source"] = "code"
                results.append(r)
        return results, None
    except Exception as exc:
        return results, f"{type(exc).__name__}: {exc}"


def surf(
    query: str,
    depth: str = "standard",
    sources: list[str] | None = None,
    as_json: bool = False,
) -> dict:
    """Search all data sources and return unified, ranked results."""
    start = time.time()

    if sources is not None:
        search_these = [s for s in sources if s in ALL_SOURCES]
        unknown_sources = [s for s in sources if s not in ALL_SOURCES]
    elif depth == "quick":
        search_these = QUICK_SOURCES
        unknown_sources = []
    else:
        search_these = ALL_SOURCES
        unknown_sources = []

    source_errors = {}
    if unknown_sources:
        source_errors["unknown_sources"] = "Unknown source(s): " + ", ".join(unknown_sources)

    all_results = []
    if search_these:
        with ThreadPoolExecutor(max_workers=len(search_these)) as pool:
            futures = {
                pool.submit(_search_source, src, query): src
                for src in search_these
            }
            for future in as_completed(futures):
                src = futures[future]
                try:
                    results, error = future.result()
                    all_results.extend(results)
                    if error:
                        source_errors[src] = error
                except Exception as exc:
                    source_errors[src] = f"{type(exc).__name__}: {exc}"

    # Score all results
    for r in all_results:
        r["confidence"] = round(_score_result(r, query, r.get("source", "")), 3)

    # Sort by confidence
    all_results.sort(key=lambda x: x["confidence"], reverse=True)

    # Follow threads (deep mode)
    expansions = []
    if depth == "deep" and all_results:
        top = all_results[:3]
        for r in top:
            path = r.get("path") or r.get("project") or ""
            if path and Path(path).exists():
                expansions.append({"type": "file_context", "path": path})
            elif r.get("session_id"):
                expansions.append({"type": "session_turns", "session_id": r["session_id"]})

    elapsed = time.time() - start

    # Group by source
    grouped = {}
    for r in all_results:
        src = r.pop("source", "unknown")
        if src not in grouped:
            grouped[src] = []
        grouped[src].append(r)

    output = {
        "query": query,
        "depth": depth,
        "sources_searched": search_these,
        "total_results": len(all_results),
        "elapsed_ms": round(elapsed * 1000),
        "results": grouped,
        "expansions": expansions[:3],
        "errors": source_errors,
    }

    if as_json:
        return output

    # Pretty print
    print(f"\n🔍 \"{query}\" — {len(all_results)} results in {elapsed*1000:.0f}ms")
    print(f"   Sources: {', '.join(search_these)}\n")

    for src, items in grouped.items():
        if not items:
            continue
        print(f"  [{src.upper()}] ({len(items)} results)")
        for item in items[:5]:
            conf = item.get("confidence", 0)
            title = (
                item.get("title")
                or item.get("session_id")
                or item.get("name")
                or ""
            )
            snippet = (
                item.get("snippet")
                or item.get("content", "")[:100]
                or item.get("match_line", "")
                or item.get("action", "")
                or item.get("decision", "")
                or ""
            )
            print(f"    [{conf:.2f}] {title[:50]}")
            if snippet:
                print(f"         {snippet[:100]}")
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more")
        print()

    if expansions:
        print(f"  [THREADS] {len(expansions)} follow-up queries available")

    if source_errors:
        print("  [ERRORS]")
        for source, error in source_errors.items():
            print(f"    {source}: {error}")
        print()

    return output


def surf_related(file_path: str) -> list[dict]:
    """Find all sessions that mention a given file path."""
    return search_file_mentions(file_path)


def main():
    # MCP mode
    if "--mcp" in sys.argv:
        try:
            sys.path.insert(0, str(Path.home() / ".mcp" / "lib"))
            from mcp_base import BaseMCPServer, tool

            class SurfacerServer(BaseMCPServer):
                server_name = "context-surfacer"
                server_version = "1.0.0"

                @tool(
                    name="surf",
                    description="Search all data sources on this Mac: sessions, files, knowledge base, state, octopus journal, skills, code. Returns unified ranked results.",
                    schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "depth": {
                                "type": "string",
                                "enum": ["quick", "standard", "deep"],
                                "description": "Search depth (default: standard)",
                                "default": "standard",
                            },
                            "sources": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter to specific sources (optional)",
                            },
                        },
                        "required": ["query"],
                    },
                )
                def surf_tool(self, query: str, depth: str = "standard", sources: list[str] = None) -> dict:
                    return surf(query, depth=depth, sources=sources, as_json=True)

                @tool(
                    name="surf_related",
                    description="Find all sessions that mention a given file path. Shows which conversations discussed this file.",
                    schema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "File path to search for"},
                        },
                        "required": ["file_path"],
                    },
                )
                def surf_related_tool(self, file_path: str) -> dict:
                    results = search_file_mentions(file_path)
                    return {"file_path": file_path, "count": len(results), "sessions": results}

            SurfacerServer().run()
        except Exception as e:
            print(f"MCP server failed: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # CLI mode
    parser = argparse.ArgumentParser(description="Context Surfacer — search everything on this Mac")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard")
    parser.add_argument("--source", action="append", help="Filter to specific source(s)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--related", help="Find sessions mentioning a file path")
    args = parser.parse_args()

    if args.related:
        results = surf_related(args.related)
        print(f"Sessions mentioning '{args.related}':")
        for r in results:
            print(f"  [{r.get('agent', '?')}] {r.get('title', '')[:50]} — {r.get('file_path', '')}")
    elif args.query:
        query = " ".join(args.query)
        result = surf(query, depth=args.depth, sources=args.source, as_json=args.json)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
