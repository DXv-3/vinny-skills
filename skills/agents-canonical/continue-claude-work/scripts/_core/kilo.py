"""Discover Kilo Code session history.

Kilo Code (the CLI variant) stores task/session history under
``~/.kilocode/tasks/<task-id>/`` rather than Claude's ``<home>/projects/``
layout. Each task folder contains:

- ``ui_messages.json``       -- the UI-facing message log
- ``api_conversation_history.json`` -- the raw API conversation (user/assistant roles)

This module mirrors :mod:`homes` so a single extractor can serve both
providers. We surface a pseudo-"home" whose ``projects`` dir is actually the
``tasks`` directory, so the rest of the pipeline can stay generic.
"""

import os
from pathlib import Path
from typing import List, Optional, Union


def discover_kilo_homes(
    explicit: Optional[Union[str, Path, List[Union[str, Path]]]] = None,
) -> List[Path]:
    """Return Kilo homes that hold a ``tasks/`` history dir.

    Args:
        explicit: ``None`` auto-discovers. A path (or list) restricts to exactly
            those homes. Each must contain a ``tasks/`` subdirectory.

    Returns:
        De-duplicated list of home ``Path`` objects, each with a ``tasks/`` dir.
        Order: ``KILO_CONFIG_DIR`` (if set), then ``~/.kilocode``.
    """
    homes: List[Path] = []
    seen = set()

    def add(candidate: Union[str, Path]) -> None:
        try:
            home = Path(candidate).expanduser()
        except Exception:
            return
        if not (home / "tasks").is_dir():
            return
        try:
            key = str(home.resolve())
        except Exception:
            key = str(home)
        if key in seen:
            return
        seen.add(key)
        homes.append(home)

    if explicit is not None:
        candidates = explicit if isinstance(explicit, (list, tuple)) else [explicit]
        for candidate in candidates:
            add(candidate)
        return homes

    env_home = os.environ.get("KILO_CONFIG_DIR")
    if env_home:
        add(env_home)
    add(Path.home() / ".kilocode")

    return homes


def home_label(home: Union[str, Path]) -> str:
    """Short provenance label for a Kilo home path."""
    home = Path(home)
    if home.name == ".kilocode":
        return "main"
    return home.name
