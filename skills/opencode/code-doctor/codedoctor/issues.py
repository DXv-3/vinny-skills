"""Phase 3: CATEGORIZE — deterministic rule engine over SKILL.md pitfalls.

Findings are candidates for agent verification, not verdicts.
"""

import os
import posixpath
import re

from .langs import EXTENSION_LANGUAGE
from .manifest import _list_files, _read

COMMENT_PREFIXES = ("#", "//", "/*", "*")
JS_FAMILY = {"javascript", "typescript", "javascript-react", "typescript-react"}

SEVERITIES = ("critical", "functional", "quality")


class Rule:
    def __init__(self, rule_id, severity, languages, message, apply):
        self.id = rule_id
        self.severity = severity
        self.languages = languages
        self.message = message
        self.apply = apply


def _strip_inline_comment(line, lang):
    stripped = line.lstrip()
    if stripped.startswith(COMMENT_PREFIXES):
        return ""
    if lang == "python":
        return line.split("#")[0]
    for marker in ("//",):
        idx = line.find(marker)
        if idx >= 0 and '"' not in line[:idx] and "'" not in line[:idx]:
            return line[:idx]
    return line


def line_rule(rule_id, severity, languages, message, pattern, flags=0):
    compiled = re.compile(pattern, flags)

    def apply(lines, lang):
        hits = []
        for i, raw in enumerate(lines, 1):
            code = _strip_inline_comment(raw, lang)
            m = compiled.search(code)
            if m:
                hits.append((i, m.start() + 1))
        return hits

    return Rule(rule_id, severity, languages, message, apply)


RULES = [
    # ---- Swift ----
    line_rule(
        "SW001", "critical", {"swift"},
        "possible force unwrap (!) — crashes at runtime if nil",
        r"[)\]\w]!(?![=])",
    ),
    line_rule(
        "SW002", "critical", {"swift"},
        "try! aborts the process on throw — propagate instead",
        r"\btry!",
    ),
    line_rule(
        "SW003", "quality", {"swift"},
        "try? silently converts errors to nil — verify this is intended",
        r"\btry\?",
    ),
    # ---- Python ----
    line_rule(
        "PY001", "functional", {"python"},
        "mutable default argument — shared across calls",
        r"def\s+\w+\s*\([^)]*=\s*(?:\[\]|\{\})",
    ),
    line_rule(
        "PY002", "functional", {"python"},
        "bare/broad except swallows real failures — log or re-raise",
        r"^\s*except(?:\s+Exception)?\s*:",
        re.MULTILINE,
    ),
    line_rule(
        "PY003", "functional", {"python"},
        "'is' used for value comparison — use == (is None is fine)",
        r"\bis\s+(?:True|False)\b",
    ),
    # ---- Go ----
    line_rule(
        "GO001", "functional", {"go"},
        "value assigned to blank identifier — error possibly discarded",
        r"^\s*(?:\w[\w.\[\]]*\s*,\s*)*_\s*(?:,\s*[\w.\[\]]+\s*,?\s*)*:?=\s*\S",
        re.MULTILINE,
    ),
    # ---- Rust ----
    line_rule(
        "RS001", "critical", {"rust"},
        ".unwrap()/.expect() panics on Err/None",
        r"\.(?:unwrap|expect)\s*\(",
    ),
]


def _check_open_without_with(lines, lang):
    hits = []
    pat = re.compile(r"(?<![.\w])open\s*\(")
    for i, raw in enumerate(lines, 1):
        stripped = raw.lstrip()
        if stripped.startswith(("with ", "with(")):
            continue
        m = pat.search(_strip_inline_comment(raw, lang))
        if m:
            hits.append((i, m.start() + 1))
    return hits


RULES.append(Rule(
    "PY004", "quality", {"python"},
    "open() without a with statement — file handle may leak",
    _check_open_without_with,
))


def _check_env_fallback(lines, lang):
    pat = re.compile(r"process\.env\.([A-Za-z_]\w*)")
    hits = []
    for i, raw in enumerate(lines, 1):
        code = _strip_inline_comment(raw, lang)
        for m in pat.finditer(code):
            rest = code[m.end():]
            if "||" not in rest and "??" not in rest:
                hits.append((i, m.start() + 1))
                break
    return hits


RULES.append(Rule(
    "JS001", "quality", JS_FAMILY,
    "process.env accessed without fallback — may be undefined",
    _check_env_fallback,
))
RULES.extend([
    line_rule(
        "REACT001", "functional", {"javascript-react", "typescript-react"},
        "index-as-key breaks reconciliation state — use stable id",
        r"key=\{\s*(?:index|i|idx)\s*\}",
    ),
    line_rule(
        "JS003", "critical", JS_FAMILY,
        "response sent but handler may continue executing (no return)",
        r"res\.json\s*\(",
    ),
    # ---- Generic ----
    line_rule(
        "GEN001", "critical", None,
        "hardcoded credential-looking string — move to secret store",
        (
            r"(?i)(?:api[_-]?key|secret|token|password|passwd|pwd|access[_-]?key)"
            r"[\"']?\s*[:=]\s*[\"'][A-Za-z0-9+/_\-]{16,}[\"']"
            r"|AKIA[0-9A-Z]{16}"
        ),
    ),
    line_rule(
        "GEN002", "critical", None,
        "hardcoded localhost endpoint — breaks outside dev",
        r"https?://(?:localhost|127\.0\.0\.1)",
    ),
])


def _check_todo(lines, lang):
    out = []
    pat = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
    for i, raw in enumerate(lines, 1):
        m = pat.search(raw)
        if m:
            out.append((i, m.start() + 1))
    return out


RULES.append(Rule(
    "GEN003", "functional", None,
    "unresolved TODO/FIXME/HACK marker",
    _check_todo,
))


def _rule_js_interval_balance(text, lang):
    """setInterval/addEventListener without matching teardown."""
    hits = []
    n_set = len(re.findall(r"\bsetInterval\s*\(", text))
    n_clear = len(re.findall(r"\bclearInterval\s*\(", text))
    if n_set > n_clear:
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"\bsetInterval\s*\(", _strip_inline_comment(line, "javascript")):
                hits.append((i, 1))
                break
    n_add = len(re.findall(r"\baddEventListener\s*\(", text))
    n_remove = len(re.findall(r"\bremoveEventListener\s*\(", text))
    if n_add > n_remove:
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"\baddEventListener\s*\(", _strip_inline_comment(line, "javascript")):
                hits.append((i, 1))
                break
    return hits


RULE_JS002 = Rule(
    "JS002", "critical", JS_FAMILY,
    "interval/listener registered without cleanup path (leak)",
    None,
)


def _check_defer_in_loop(text, lang):
    """Brace-stack tracker: defer inside a for/while block."""
    hits = []
    stack = []
    lines = text.splitlines()
    for i, raw in enumerate(lines, 1):
        code = _strip_inline_comment(raw, lang)
        if re.match(r"^\s*(?:for|while)\b", code) and "{" in code:
            stack.append(True)
        elif "{" in code:
            stack.append(False)
        if re.search(r"\bdefer\b", code) and any(stack):
            hits.append((i, code.find("defer") + 1))
        depth = code.count("}")
        while depth > 0 and stack:
            stack.pop()
            depth -= 1
    return hits


RULE_GO002 = Rule(
    "GO002", "quality", {"go"},
    "defer inside loop accumulates until function returns",
    None,
)


def scan_text(text, lang, filename):
    """Run all applicable rules over one in-memory file."""
    findings = []
    lines = text.splitlines()
    for rule in RULES:
        if rule.languages is not None and lang not in rule.languages:
            continue
        for line_no, col in rule.apply(lines, lang):
            findings.append({
                "severity": rule.severity,
                "file": filename,
                "line": line_no,
                "col": col,
                "rule_id": rule.id,
                "message": rule.message,
            })
    special = []
    if lang in JS_FAMILY:
        special.append((RULE_JS002, _rule_js_interval_balance))
    if lang == "go":
        special.append((RULE_GO002, _check_defer_in_loop))
    for rule, checker in special:
        for line_no, col in checker(text, lang):
            findings.append({
                "severity": rule.severity,
                "file": filename,
                "line": line_no,
                "col": col,
                "rule_id": rule.id,
                "message": rule.message,
            })
    return findings


def find_issues(root):
    root = os.path.abspath(root)
    findings = []
    for relpath in _list_files(root):
        ext = os.path.splitext(posixpath.basename(relpath))[1].lower()
        lang = EXTENSION_LANGUAGE.get(ext)
        if not lang:
            continue
        try:
            text = _read(os.path.join(root, relpath))
        except OSError:
            continue
        posix_path = relpath.replace(os.sep, "/")
        findings.extend(scan_text(text, lang, posix_path))
    findings.sort(key=lambda f: (f["file"], f["line"], f["col"]))
    return findings
