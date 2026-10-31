"""
Search codebase-memory graph. Discovery pass finds candidate projects,
then searches their code graphs for the query.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


def _discovery_pass(query: str) -> list[str]:
    """Find project names matching query from SYSTEM-STATE and session logs."""
    candidates = set()

    # From SYSTEM-STATE
    state_path = Path.home() / "SYSTEM-STATE.md"
    if not state_path.exists():
        state_path = Path.home() / "VINNYOS-STATE.md"
    if state_path.exists():
        text = state_path.read_text(errors="replace")
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for line in text.splitlines():
            if pattern.search(line):
                # Extract project names (paths after - or |)
                for match in re.finditer(r"`([^`]+)`", line):
                    candidates.add(match.group(1))

    # From session titles (quick grep)
    sessions_dir = Path.home() / ".ai-memory" / "sessions"
    if sessions_dir.exists():
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for log_file in list(sessions_dir.glob("*.log"))[:100]:
            try:
                with open(log_file, errors="replace") as f:
                    first_lines = f.read(2000)
                if pattern.search(first_lines):
                    # Extract session as potential project reference
                    candidates.add(log_file.stem)
            except Exception:
                continue

    return list(candidates)[:10]


def search_code(
    query: str,
    project: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Search codebase-memory for code matching the query.

    If project is given, searches that project directly.
    If not, runs discovery pass to find candidate projects first.

    Returns:
        List of dicts with project, qualified_name, type, file_path, snippet
    """
    # If no project specified, do discovery
    if not project:
        candidates = _discovery_pass(query)
        if not candidates:
            return []
    else:
        candidates = [project]

    results = []
    for proj in candidates:
        try:
            # Call codebase-memory search via CLI
            result = subprocess.run(
                [
                    str(Path.home() / "bin" / "codebase-memory-mcp"),
                    "search",
                    "--project", proj,
                    "--query", query,
                    "--limit", str(min(limit, 10)),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        parts = line.split("|", 3)
                        if len(parts) >= 3:
                            results.append({
                                "project": proj,
                                "qualified_name": parts[0].strip(),
                                "type": parts[1].strip(),
                                "file_path": parts[2].strip() if len(parts) > 2 else "",
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return results[:limit]


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "youtube"
    print(f"Searching code: {q}")
    for r in search_code(q, limit=10):
        print(f"  [{r['project']}] {r['type']}: {r['qualified_name']}")
