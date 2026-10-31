"""
Parse ~/SYSTEM-STATE.md into sections. Falls back to the legacy VINNYOS-STATE.md path.
"""

from __future__ import annotations

import re
from pathlib import Path

STATE_PATH = Path.home() / "SYSTEM-STATE.md"
LEGACY_STATE_PATH = Path.home() / "VINNYOS-STATE.md"


def _active_state_path() -> Path:
    if STATE_PATH.exists():
        return STATE_PATH
    return LEGACY_STATE_PATH


def _parse_state() -> dict[str, str]:
    """Parse state file into {section_name: section_content}."""
    state_path = _active_state_path()
    if not state_path.exists():
        return {}
    text = state_path.read_text(errors="replace")
    sections = {}
    current = "header"
    lines = []
    for line in text.splitlines():
        if line.startswith("## "):
            sections[current] = "\n".join(lines)
            current = line[3:].strip()
            lines = []
        else:
            lines.append(line)
    sections[current] = "\n".join(lines)
    return sections


def search_state(query: str) -> list[dict]:
    """Search parsed state sections for query matches.

    Returns:
        List of dicts with section, matching_lines, line_numbers
    """
    sections = _parse_state()
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    results = []

    for section, content in sections.items():
        matches = []
        for i, line in enumerate(content.splitlines(), 1):
            if pattern.search(line):
                matches.append({"line": i, "text": line.strip()[:200]})
        if matches:
            results.append({
                "section": section,
                "match_count": len(matches),
                "matches": matches[:10],
            })

    return results


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching VINNYOS-STATE: {q}")
    for r in search_state(q):
        print(f"  [{r['section']}] {r['match_count']} matches")
        for m in r["matches"][:3]:
            print(f"    L{m['line']}: {m['text'][:80]}")
