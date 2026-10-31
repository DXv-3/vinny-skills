"""
Format-Smormat adapter layer for session log normalization.

Detects session format from first 5 lines, runs the appropriate adapter,
and returns normalized SessionTurn/ParsedSession dataclasses.

Handles: OpenCode, Grok, Kilo, IDE, Gemini, Codex, Ollama, AnythingLLM, unknown.
Never crashes on a file — returns None on unrecoverable error.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SessionTurn:
    role: str           # "user" | "ai" | "system"
    timestamp: str      # ISO format
    content: str        # extracted text
    line_start: int
    line_end: int
    is_noise: bool = False


@dataclass
class ParsedSession:
    agent: str
    title: str
    turns: list[SessionTurn]
    started_at: str
    ended_at: str
    noise_ratio: float
    source_file: str
    file_hash: str = ""


# ─── Regex for timestamp lines ───

TS_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2}T[\d:.]+Z)\]\s+(USER|AI|TOOL):\s*(.*)",
    re.MULTILINE,
)

# ─── Noise patterns ───

NOISE_PATTERNS = [
    re.compile(r"^\s*\{.*\}\s*$"),           # standalone JSON lines
    re.compile(r"^\s*<\w+.*>\s*$"),          # standalone HTML/XML tags (not <task>)
    re.compile(r"^\s*\$\d+\.\d+\s*$"),       # cost lines like $0.0000
    re.compile(r"^\s*#{3,}\s*$"),             # separator lines
]


def _file_hash(path: str, length: int = 1000) -> str:
    """MD5 of first `length` bytes for incremental feed tracking."""
    try:
        data = Path(path).read_bytes()[:length]
        return hashlib.md5(data).hexdigest()
    except Exception:
        return ""


def _is_noise_line(line: str) -> bool:
    """Check if a line is pure noise (JSON, HTML tags, cost, etc.)."""
    for pat in NOISE_PATTERNS:
        if pat.match(line):
            return True
    return False


def _word_count(text: str) -> int:
    return len(text.split())


# ─── Format Detection ───

def detect_format(first_lines: list[str]) -> str:
    """Sniff first 5 lines → return adapter name."""
    text = "\n".join(first_lines)

    # Check for TOOL lines → Kilo
    if re.search(r"^\[.*\] TOOL:", text, re.MULTILINE):
        return "kilo"

    # Check for <task> XML tags → IDE
    if "<task>" in text:
        return "ide"

    # Check for standard [TS] USER:/AI: format
    if re.search(r"^\[.*\] (USER|AI):", text, re.MULTILINE):
        # Determine agent from filename or content
        lower = text.lower()
        if "gemini" in lower:
            return "gemini"
        if "codex" in lower:
            return "codex"
        if "ollama" in lower:
            return "ollama"
        if "anythingllm" in lower:
            return "anythingllm"
        if "grok" in lower:
            return "grok"
        return "opencode"

    return "unknown"


# ─── Adapters ───

def _parse_standard(file_path: str, agent: str) -> ParsedSession:
    """Handles OpenCode, Grok, Gemini, Codex, Ollama, AnythingLLM.
    All share [TIMESTAMP] USER:/AI: format."""
    try:
        lines = Path(file_path).read_text(errors="replace").splitlines()
    except Exception:
        return None

    turns = []
    for i, line in enumerate(lines):
        m = TS_RE.match(line)
        if m:
            ts, role_raw, content = m.group(1), m.group(2).lower(), m.group(3)
            content = content.strip()
            if not content:
                continue

            # Strip <think>...</think> from AI responses
            if role_raw == "ai":
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                if not content:
                    continue

            turns.append(SessionTurn(
                role=role_raw,
                timestamp=ts,
                content=content,
                line_start=i + 1,
                line_end=i + 1,
                is_noise=_is_noise_line(content),
            ))

    if not turns:
        return None

    noisy = sum(1 for t in turns if t.is_noise)
    return ParsedSession(
        agent=agent,
        title=next((t.content[:100] for t in turns if t.role == "user" and not t.is_noise), ""),
        turns=turns,
        started_at=turns[0].timestamp,
        ended_at=turns[-1].timestamp,
        noise_ratio=noisy / max(len(turns), 1),
        source_file=file_path,
        file_hash=_file_hash(file_path),
    )


def _parse_kilo(file_path: str) -> ParsedSession:
    """Kilo format: raw tool dumps. Strips TOOL blocks, keeps USER/AI."""
    try:
        lines = Path(file_path).read_text(errors="replace").splitlines()
    except Exception:
        return None

    turns = []
    in_tool_block = False
    for i, line in enumerate(lines):
        m = TS_RE.match(line)
        if m:
            ts, role_raw, content = m.group(1), m.group(2).lower(), m.group(3)
            if role_raw == "tool":
                in_tool_block = True
                continue
            if role_raw in ("user", "ai"):
                in_tool_block = False
                content = content.strip()
                if content:
                    turns.append(SessionTurn(
                        role=role_raw,
                        timestamp=ts,
                        content=content,
                        line_start=i + 1,
                        line_end=i + 1,
                        is_noise=False,
                    ))
        elif in_tool_block:
            continue

    if not turns:
        return None

    total = len(lines)
    noise_lines = total - len(turns)
    return ParsedSession(
        agent="kilo",
        title=next((t.content[:100] for t in turns if t.role == "user"), ""),
        turns=turns,
        started_at=turns[0].timestamp,
        ended_at=turns[-1].timestamp,
        noise_ratio=noise_lines / max(total, 1),
        source_file=file_path,
        file_hash=_file_hash(file_path),
    )


def _parse_ide(file_path: str) -> ParsedSession:
    """IDE/globalStorage format: [TS] USER: <task>...</task>"""
    try:
        raw = Path(file_path).read_text(errors="replace")
    except Exception:
        return None

    # Strip <task> tags
    content = re.sub(r"<task>(.*?)</task>", r"\1", raw, flags=re.DOTALL)
    lines = content.splitlines()
    turns = []
    for i, line in enumerate(lines):
        m = TS_RE.match(line)
        if m:
            ts, role_raw, text = m.group(1), m.group(2).lower(), m.group(3)
            text = text.strip()
            if text:
                turns.append(SessionTurn(
                    role=role_raw,
                    timestamp=ts,
                    content=text,
                    line_start=i + 1,
                    line_end=i + 1,
                    is_noise=False,
                ))

    if not turns:
        return None

    return ParsedSession(
        agent="ide",
        title=next((t.content[:100] for t in turns if t.role == "user"), ""),
        turns=turns,
        started_at=turns[0].timestamp,
        ended_at=turns[-1].timestamp,
        noise_ratio=0.05,
        source_file=file_path,
        file_hash=_file_hash(file_path),
    )


def _parse_fallback(file_path: str) -> ParsedSession:
    """Unknown format: extract any [TIMESTAMP] ROLE: content lines."""
    try:
        lines = Path(file_path).read_text(errors="replace").splitlines()
    except Exception:
        return None

    turns = []
    for i, line in enumerate(lines):
        m = TS_RE.match(line)
        if m:
            ts, role_raw, content = m.group(1), m.group(2).lower(), m.group(3)
            content = content.strip()
            if content:
                turns.append(SessionTurn(
                    role=role_raw,
                    timestamp=ts,
                    content=content,
                    line_start=i + 1,
                    line_end=i + 1,
                    is_noise=_is_noise_line(content),
                ))

    if not turns:
        return None

    noisy = sum(1 for t in turns if t.is_noise)
    return ParsedSession(
        agent="unknown",
        title=next((t.content[:100] for t in turns if t.role == "user" and not t.is_noise), ""),
        turns=turns,
        started_at=turns[0].timestamp,
        ended_at=turns[-1].timestamp,
        noise_ratio=noisy / max(len(turns), 1),
        source_file=file_path,
        file_hash=_file_hash(file_path),
    )


# ─── Router ───

def parse_session(file_path: str) -> ParsedSession | None:
    """Detect format → run adapter → return normalized turns.
    Returns None on unrecoverable error. Never raises."""
    try:
        first_lines = Path(file_path).read_text(errors="replace").splitlines()[:5]
    except Exception:
        return None

    fmt = detect_format(first_lines)

    try:
        if fmt == "kilo":
            return _parse_kilo(file_path)
        elif fmt == "ide":
            return _parse_ide(file_path)
        elif fmt == "gemini":
            return _parse_standard(file_path, "gemini")
        elif fmt == "codex":
            return _parse_standard(file_path, "codex")
        elif fmt == "ollama":
            return _parse_standard(file_path, "ollama")
        elif fmt == "anythingllm":
            return _parse_standard(file_path, "anythingllm")
        elif fmt == "grok":
            return _parse_standard(file_path, "grok")
        elif fmt == "opencode":
            return _parse_standard(file_path, "opencode")
        else:
            return _parse_fallback(file_path)
    except Exception:
        return None
