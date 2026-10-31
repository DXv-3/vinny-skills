"""Phase 5 BUILD gate — syntax-check dispatcher per language.

Statuses: pass | fail | unsupported (no checker for ext) | tool-missing |
error (file unreadable). Only "fail" and "error" set ok=False.
"""

import os
import shutil
import subprocess

from .langs import EXTENSION_LANGUAGE


def _py_check(path):
    import ast
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            ast.parse(f.read(), filename=path)
    except SyntaxError as exc:
        return False, "SyntaxError: %s (line %s)" % (exc.msg, exc.lineno)
    except OSError as exc:
        return False, str(exc)
    return True, ""


def _subprocess_checker(argv, timeout=30):
    def check(path):
        try:
            proc = subprocess.run(
                [*argv, path],
                capture_output=True, text=True, timeout=timeout,
                stdin=subprocess.DEVNULL,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, "%s: %s" % (exc.__class__.__name__, exc)
        if proc.returncode == 0:
            return True, ""
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return False, detail[0] if detail else "exit code %d" % proc.returncode
    return check


CHECKERS = {
    ".py": ("python3", _py_check),
    ".js": ("node", _subprocess_checker(["node", "--check"])),
    ".swift": ("swiftc", _subprocess_checker(["swiftc", "-parse"])),
    ".go": ("gofmt", _subprocess_checker(["gofmt", "-e"])),
    ".rs": ("rustc", _subprocess_checker(["rustc", "--edition", "2021", "--check"])),
    ".c": ("cc", _subprocess_checker(["cc", "-fsyntax-only"])),
    ".cpp": ("cc", _subprocess_checker(["cc", "-fsyntax-only"])),
}


def verify_files(paths, tool_lookup=shutil.which):
    results = []
    for path in paths:
        entry = {"file": path, "ok": True, "status": "unsupported", "output": ""}
        if not os.path.isfile(path):
            entry.update(ok=False, status="error", output="not found")
            results.append(entry)
            continue
        ext = os.path.splitext(path)[1].lower()
        spec = CHECKERS.get(ext)
        if not spec:
            lang = EXTENSION_LANGUAGE.get(ext)
            entry["output"] = "no syntax checker registered for %s (%s)" % (ext, lang)
            results.append(entry)
            continue
        tool, checker = spec
        if tool and not tool_lookup(tool):
            entry["status"] = "tool-missing"
            entry["output"] = "%s not on PATH; cannot verify %s" % (tool, ext)
            results.append(entry)
            continue
        ok, output = checker(path)
        entry.update(ok=ok, status="pass" if ok else "fail", output=output)
        results.append(entry)
    return results
