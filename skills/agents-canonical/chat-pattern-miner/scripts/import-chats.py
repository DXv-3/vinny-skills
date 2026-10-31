#!/usr/bin/env python3
"""Import chat history from other sources into the chat-mining corpus.

Sources:
  opencode   local opencode database (~/.local/share/opencode/opencode.db)
  chatgpt    ChatGPT export: conversations.json (unzip the data-export zip first)
  claude     Claude.ai export: conversations.json (from Settings > Privacy > Export data)
  <dir>      generic directory of .txt/.md exports (heuristic user:/assistant: parsing)

Usage:
  import-chats.py opencode --out ~/Projects/chat-mining/corpus/
  import-chats.py chatgpt ~/Downloads/conversations.json --out ~/Projects/chat-mining/corpus/
  import-chats.py claude ~/Downloads/claude-export/data --out ~/Projects/chat-mining/corpus/

Read-only on sources. Output: one .txt per conversation + _INDEX.txt (same format
as extract-chats.py, so the mining workflow is identical afterward).
"""
import argparse, json, sqlite3, sys, re
from datetime import datetime, timezone
from pathlib import Path

OPENCODE_DB = Path.home() / ".local/share/opencode/opencode.db"
MAX_CHARS = 200000


def fmt(convo_id, title, when, turns, out_dir, max_chars=MAX_CHARS):
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", f"{convo_id}-{title}")[:80]
    dest = out_dir / f"{safe}.txt"
    lines, total = [f"# {title}  ({when})\n"], 0
    for role, text in turns:
        if not text.strip():
            continue
        chunk = f"### {role.upper()}\n{text.strip()}\n"
        lines.append(chunk)
        total += len(chunk)
        if total > max_chars:
            lines.append("\n[TRUNCATED]\n")
            break
    if total > 200:
        dest.write_text("".join(lines))
        return dest.name, total
    return None, 0


def import_opencode(out_dir, db_path=OPENCODE_DB, limit=None):
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)  # read-only
    sessions = db.execute(
        "select id, title, time_updated from session order by time_updated").fetchall()
    if limit:
        sessions = sessions[-limit:]
    index = []
    for sid, title, updated in sessions:
        rows = db.execute(
            """select m.data, p.data from message m join part p on p.message_id = m.id
               where m.session_id = ? and json_extract(p.data,'$.type')='text'
               order by m.time_created, p.time_created""", (sid,)).fetchall()
        turns = []
        for mdata, pdata in rows:
            role = json.loads(mdata).get("role", "user")
            text = json.loads(pdata).get("text", "")
            turns.append(("user" if role == "user" else "assistant", text))
        when = datetime.fromtimestamp(updated / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        name, chars = fmt(sid, title or sid, when, turns, out_dir)
        if name:
            index.append((name, chars))
    db.close()
    return index


def _import_conversations_json(path, out_dir, user_keys, asst_keys):
    data = json.loads(Path(path).read_text(errors="replace"))
    index = []
    for convo in data:
        title = convo.get("title") or convo.get("name") or "untitled"
        when = (convo.get("create_time") or convo.get("created_at") or "")
        if isinstance(when, float):
            when = datetime.fromtimestamp(when, tz=timezone.utc).strftime("%Y-%m-%d")
        turns = []
        mapping = convo.get("mapping")
        if mapping:  # ChatGPT export format: node tree
            for node in mapping.values():
                msg = node.get("message") or {}
                role = (msg.get("author") or {}).get("role")
                content = (msg.get("content") or {})
                if role in ("user", "assistant") and content.get("content_type") == "text":
                    parts = content.get("parts", [])
                    text = "\n".join(p for p in parts if isinstance(p, str))
                    turns.append((role, text))
        else:  # Claude export format: flat chat_messages list
            for msg in convo.get("chat_messages", []):
                role = "user" if msg.get("sender") == "human" else "assistant"
                text = "\n".join(c.get("text", "") for c in msg.get("content", []))
                turns.append((role, text))
        cid = convo.get("id", title)[:40]
        name, chars = fmt(cid, title, str(when) or "?", turns, out_dir)
        if name:
            index.append((name, chars))
    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="opencode | chatgpt | claude | a directory")
    ap.add_argument("path", nargs="?", help="export file/dir (chatgpt/claude/generic)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, help="opencode: only most recent N sessions")
    args = ap.parse_args()

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    src = args.source.lower()

    if src == "opencode":
        index = import_opencode(out, limit=args.limit)
    elif src == "chatgpt":
        index = _import_conversations_json(args.path, out, None, None)
    elif src == "claude":
        # accept either the conversations.json or the folder containing it
        p = Path(args.path).expanduser()
        if p.is_dir():
            p = p / "conversations.json"
        index = _import_conversations_json(p, out, None, None)
    else:
        p = Path(args.source).expanduser()
        files = sorted(q for q in p.rglob("*") if q.is_file() and q.suffix.lower() in (".txt", ".md"))
        index = []
        for f in files:
            name, chars = fmt(f.stem, f.stem, "?", [("user", f.read_text(errors="replace"))], out)
            if name:
                index.append((name, chars))

    with (out / "_INDEX.txt").open("a") as fh:
        for n, c in index:
            fh.write(f"{n}\t{c} chars\n")
        fh.write(f"\nimported {len(index)} conversations from {src}\n\n")
    print(f"imported {len(index)} conversations from {src} -> {out}")


if __name__ == "__main__":
    main()
