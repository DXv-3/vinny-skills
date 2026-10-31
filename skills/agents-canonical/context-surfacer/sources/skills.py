"""
Scan SKILL.md files for name, description, and trigger keywords.
Matches against query.
"""

from __future__ import annotations

import re
from pathlib import Path

SKILL_DIRS = [
    Path.home() / ".claude" / "skills",
    Path.home() / ".agents" / "skills",
]


def _parse_skill(skill_md: Path) -> dict | None:
    """Extract name and description from YAML frontmatter."""
    try:
        text = skill_md.read_text(errors="replace")
    except Exception:
        return None

    # Extract YAML frontmatter
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None

    frontmatter = m.group(1)
    name = ""
    description = ""
    for line in frontmatter.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            description = line.split(":", 1)[1].strip().strip('"').strip("'")

    if not name:
        name = skill_md.parent.name

    return {
        "name": name,
        "description": description[:300],
        "path": str(skill_md.parent),
        "triggers": description.lower(),
    }


def search_skills(query: str, limit: int = 10) -> list[dict]:
    """Scan SKILL.md files and match against query.

    Returns:
        List of dicts with name, description, path, relevance
    """
    results = []
    seen = set()
    query_lower = query.lower()
    query_words = set(query_lower.split())

    for skill_dir in SKILL_DIRS:
        if not skill_dir.exists():
            continue
        for skill_md in skill_dir.glob("*/SKILL.md"):
            if skill_md in seen:
                continue
            seen.add(skill_md)

            skill = _parse_skill(skill_md)
            if not skill:
                continue

            # Score: name match > description word match > trigger match
            score = 0.0
            if query_lower in skill["name"].lower():
                score = 1.0
            elif query_words & set(skill["triggers"].split()):
                score = 0.5
            elif any(w in skill["description"].lower() for w in query_words):
                score = 0.3

            if score > 0:
                skill["relevance"] = score
                results.append(skill)

    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:limit]


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching skills: {q}")
    for r in search_skills(q, limit=5):
        print(f"  [{r['relevance']:.1f}] {r['name']}: {r['description'][:60]}")
