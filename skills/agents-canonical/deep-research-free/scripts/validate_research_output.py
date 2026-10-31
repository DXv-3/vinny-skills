#!/usr/bin/env python3
"""Validate deep-research-free dual artifacts (.md + .json basis).

Usage:
  validate_research_output.py PATH_STEM
  validate_research_output.py ~/Documents/research/my-topic

PATH_STEM may be with or without .md/.json extension.
Exit 0 on pass, 1 on fail. Prints machine-readable FAIL lines.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP = {
    "interaction_id",
    "engine",
    "tier",
    "topic",
    "filename",
    "generated_at",
    "sub_questions",
    "surfaces_covered",
    "sources",
    "claims",
    "recommendations",
    "gaps",
    "follow_up_hooks",
}
TIERS = {"lite", "base", "core", "pro", "ultra"}
SUPPORT = {"confirmed", "single-source", "vendor-only", "disputed", "gap"}
SURFACES = {"github", "reddit", "arxiv", "vendor", "hn", "x", "docs", "other"}
ROLES = {"primary", "secondary", "critical"}


def stem_paths(arg: str) -> tuple[Path, Path]:
    p = Path(arg).expanduser()
    if p.suffix in {".md", ".json"}:
        p = p.with_suffix("")
    return p.with_suffix(".md"), p.with_suffix(".json")


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)
    print(f"FAIL: {msg}")


def validate(md_path: Path, json_path: Path) -> list[str]:
    errors: list[str] = []

    if not md_path.is_file():
        fail(f"missing report: {md_path}", errors)
    if not json_path.is_file():
        fail(f"missing basis: {json_path}", errors)
        return errors

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"basis JSON invalid: {e}", errors)
        return errors

    if not isinstance(data, dict):
        fail("basis root must be object", errors)
        return errors

    missing = REQUIRED_TOP - set(data.keys())
    if missing:
        fail(f"basis missing keys: {sorted(missing)}", errors)

    if data.get("engine") != "deep-research-free":
        fail(f"engine must be deep-research-free, got {data.get('engine')!r}", errors)

    if data.get("tier") not in TIERS:
        fail(f"tier must be one of {sorted(TIERS)}, got {data.get('tier')!r}", errors)

    iid = data.get("interaction_id") or ""
    if not isinstance(iid, str) or not iid.startswith("free-"):
        fail(f"interaction_id must start with 'free-', got {iid!r}", errors)

    for key in ("sub_questions", "surfaces_covered", "sources", "claims", "recommendations", "gaps", "follow_up_hooks"):
        if key in data and not isinstance(data[key], list):
            fail(f"{key} must be list", errors)

    sources = data.get("sources") or []
    source_ids: set[str] = set()
    for i, s in enumerate(sources):
        if not isinstance(s, dict):
            fail(f"sources[{i}] not object", errors)
            continue
        for k in ("id", "url", "title", "surface", "role"):
            if k not in s or s[k] in (None, ""):
                fail(f"sources[{i}] missing {k}", errors)
        sid = s.get("id")
        if sid:
            if sid in source_ids:
                fail(f"duplicate source id {sid}", errors)
            source_ids.add(sid)
        if s.get("surface") not in SURFACES:
            fail(f"sources[{i}].surface invalid: {s.get('surface')!r}", errors)
        if s.get("role") not in ROLES:
            fail(f"sources[{i}].role invalid: {s.get('role')!r}", errors)
        url = s.get("url") or ""
        if url and not re.match(r"^https?://", url):
            fail(f"sources[{i}].url not http(s): {url!r}", errors)

    for i, c in enumerate(data.get("claims") or []):
        if not isinstance(c, dict):
            fail(f"claims[{i}] not object", errors)
            continue
        if not c.get("claim"):
            fail(f"claims[{i}] empty claim", errors)
        if c.get("support") not in SUPPORT:
            fail(f"claims[{i}].support invalid: {c.get('support')!r}", errors)
        for sid in c.get("source_ids") or []:
            if source_ids and sid not in source_ids:
                fail(f"claims[{i}] references unknown source_id {sid}", errors)

    if md_path.is_file():
        text = md_path.read_text(encoding="utf-8", errors="replace")
        if len(text.strip()) < 200:
            fail(f"report too short ({len(text)} chars)", errors)
        if "Executive Summary" not in text and "## 1. Executive Summary" not in text:
            fail("report missing Executive Summary section", errors)
        if "Sources" not in text:
            fail("report missing Sources section", errors)
        if data.get("interaction_id") and data["interaction_id"] not in text:
            # soft warning as hard fail for chainability
            fail(f"report does not mention interaction_id {data['interaction_id']}", errors)
        if "deep-research-free" not in text and "Engine: deep-research-free" not in text:
            fail("report should name engine deep-research-free", errors)

    if not errors:
        print(f"OK: {md_path.name} + {json_path.name}")
        print(f"  interaction_id={data.get('interaction_id')} tier={data.get('tier')} sources={len(sources)}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    md, js = stem_paths(sys.argv[1])
    errors = validate(md, js)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
