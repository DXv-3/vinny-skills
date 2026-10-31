#!/usr/bin/env python3
"""Extract readable conversations from ZCode rollout JSONL (or a directory of
uploaded chat exports) into plain-text files for LLM analysis.

Usage:
  extract-chats.py --source rollout --out ~/Projects/chat-mining/corpus/
  extract-chats.py --source /path/to/exports --out ~/Projects/chat-mining/corpus/

Read-only: never modifies or moves source files.
"""
import argparse, json, sys
from pathlib import Path

ROLLOUT = Path.home() / ".zcode/cli/rollout"


def iter_rollout_messages(path: Path):
    """Yield (role, text) from a ZCode model-io JSONL transcript."""
    try:
        for line in path.open(errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            # ZCode model-io record: request.messages is the conversation.
            req = rec.get("request") or {}
            msgs = req.get("messages")
            if isinstance(msgs, list):
                for m in msgs:
                    if not isinstance(m, dict):
                        continue
                    role = m.get("role") or "?"
                    content = m.get("content")
                    if isinstance(content, str):
                        yield role, content
                    elif isinstance(content, list):
                        parts = []
                        for c in content:
                            if isinstance(c, dict):
                                if c.get("type") in ("text", "input_text"):
                                    parts.append(c.get("text", ""))
                                elif c.get("type") == "tool_use":
                                    parts.append(f"[tool:{c.get('name', '?')} omitted]")
                        if parts:
                            yield role, "\n".join(p for p in parts if p)
                continue
            # Fallback: generic shapes.
            msg = rec.get("message") or rec.get("msg") or rec
            role = msg.get("role") or rec.get("role")
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, str):
                yield role or "?", content
            elif isinstance(content, list):
                parts = []
                for c in content:
                    if isinstance(c, dict):
                        if c.get("type") in ("text", "input_text"):
                            parts.append(c.get("text", ""))
                        elif c.get("type") == "tool_use":
                            parts.append(f"[tool:{c.get('name', '?')} omitted]")
                if parts:
                    yield role or "?", "\n".join(p for p in parts if p)
    except OSError as e:
        print(f"warn: cannot read {path}: {e}", file=sys.stderr)


def iter_uploaded(path: Path):
    """Yield (role, text) heuristically from plain-text chat exports."""
    text = path.read_text(errors="replace")
    role = "user"
    buf = []
    for line in text.splitlines():
        low = line.strip().lower()
        if low.startswith(("user:", "you:", "human:")):
            if buf:
                yield role, "\n".join(buf)
            role, buf = "user", [line.split(":", 1)[1].lstrip()]
        elif low.startswith(("assistant:", "ai:", "chatgpt:", "claude:", "zcode:")):
            if buf:
                yield role, "\n".join(buf)
            role, buf = "assistant", [line.split(":", 1)[1].lstrip()]
        else:
            buf.append(line)
    if buf:
        yield role, "\n".join(buf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="'rollout' or a directory of exports")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-chars", type=int, default=200000, help="truncate each conversation")
    args = ap.parse_args()

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    src = Path(args.source)
    files = (sorted(ROLLOUT.glob("model-io-sess_*.jsonl")) if src == Path("rollout")
             else sorted(p for p in src.rglob("*") if p.is_file()))
    if src == Path("rollout") and not files:
        print(f"no transcripts found in {ROLLOUT}", file=sys.stderr)
        sys.exit(1)

    index = []
    for f in files:
        name = f.stem.replace("model-io-", "")[:60]
        dest = out / f"{name}.txt"
        turns = iter_rollout_messages(f) if f.suffix == ".jsonl" else iter_uploaded(f)
        lines, total, seen = [], 0, set()
        for role, text in turns:
            if not text.strip() or role == "system":
                continue
            key = (role, hash(text))
            if key in seen:  # rollout records replay the whole history
                continue
            seen.add(key)
            chunk = f"### {role.upper()}\n{text.strip()}\n"
            lines.append(chunk)
            total += len(chunk)
            if total > args.max_chars:
                lines.append("\n[TRUNCATED]\n")
                break
        if lines:
            dest.write_text("".join(lines))
            index.append((dest.name, total))

    (out / "_INDEX.txt").write_text(
        "\n".join(f"{n}\t{c} chars" for n, c in index) + f"\n\n{len(index)} conversations\n")
    print(f"extracted {len(index)} conversations -> {out}")


if __name__ == "__main__":
    main()
