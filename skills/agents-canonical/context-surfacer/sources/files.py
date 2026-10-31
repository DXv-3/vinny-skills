"""
Direct glob + grep across known project directories.
Skips mac-catalog (indexes system files, not user content).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

SEARCH_DIRS = [
    Path.home() / "youtube-ingest",
    Path.home() / "Projects",
    Path.home() / ".claude" / "skills",
    Path.home() / "Documents",
    Path.home() / "knowledge-base",
    Path.home() / "miniclusy",
    Path.home() / "Projects" / "GitHub-Repos",
    Path.home() / "sessions",
]

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".next",
}

SKIP_EXTS = {
    ".pyc", ".pyo", ".so", ".dylib", ".o", ".a",
    ".sqlite", ".db", ".log", ".DS_Store",
}


def search_files(
    query: str,
    limit: int = 20,
) -> list[dict]:
    """Glob + grep across known project directories.

    Returns:
        List of dicts with path, size, match_line, match_context
    """
    results = []
    seen = set()
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for search_dir in SEARCH_DIRS:
        if not search_dir.exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            # Prune dirs
            dirs[:] = [
                d for d in dirs
                if d not in SKIP_DIRS
            ]

            for fname in files:
                if any(fname.endswith(ext) for ext in SKIP_EXTS):
                    continue

                fpath = Path(root) / fname
                if fpath in seen:
                    continue
                seen.add(fpath)

                # Only search text files under 1MB
                try:
                    size = fpath.stat().st_size
                    if size > 1_000_000 or size == 0:
                        continue
                except OSError:
                    continue

                try:
                    text = fpath.read_text(errors="replace")
                except Exception:
                    continue

                # Check filename match
                if pattern.search(fname):
                    results.append({
                        "path": str(fpath),
                        "size": size,
                        "match_type": "filename",
                        "match_line": fname,
                    })
                    if len(results) >= limit:
                        return results
                    continue

                # Check content match (first match only)
                for i, line in enumerate(text.splitlines(), 1):
                    if pattern.search(line):
                        results.append({
                            "path": str(fpath),
                            "size": size,
                            "match_type": "content",
                            "match_line": line.strip()[:200],
                            "line_number": i,
                        })
                        if len(results) >= limit:
                            return results
                        break

    return results


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching files: {q}")
    for r in search_files(q, limit=10):
        print(f"  {r['match_type']}: {r['path']} — {r['match_line'][:80]}")
