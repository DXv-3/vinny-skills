"""Phase 1: READ — file manifest with imports/exports and entry points."""

import ast
import os
import posixpath
import re
import subprocess

from .langs import (
    CONFIG_EXTENSIONS,
    DOC_EXTENSIONS,
    EXCLUDED_DIRS,
    EXTENSION_LANGUAGE,
)

BUILD_FILENAMES = {"Makefile", "Dockerfile", "CMakeLists.txt", "Package.swift"}

_PY_IMPORT_RE = re.compile(r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import\b)")
_JS_IMPORT_RE = re.compile(
    r"""(?:import\s+(?:[\w{},*\s]+?\s+from\s+)?['"]([^'"]+)['"]"""
    r"""|(?:const|let|var)\s+[\w{},*\s]+=\s*require\(\s*['"]([^'"]+)['"]\s*\))"""
)
_JS_EXPORT_RE = re.compile(
    r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+(\w+)",
    re.MULTILINE,
)
_GO_TOPLEVEL_RE = re.compile(r"^(func|type|var|const)\s+([A-Z]\w*)")
_SWIFT_IMPORT_RE = re.compile(r"^\s*import\s+(\w+)")
_RS_USE_RE = re.compile(r"^\s*use\s+([\w:{},\s]+);")


def _is_source(name):
    return os.path.splitext(name)[1].lower() in EXTENSION_LANGUAGE


def _classify(base, ext):
    if base in BUILD_FILENAMES or base == "project.pbxproj":
        return "build"
    if ext in EXTENSION_LANGUAGE:
        return "source"
    if ext in CONFIG_EXTENSIONS:
        return "config"
    if ext in DOC_EXTENSIONS:
        return "doc"
    return "other"


def _list_files(root):
    """Prefer git ls-files; fall back to filtered walk."""
    if os.path.isdir(os.path.join(root, ".git")):
        try:
            out = subprocess.run(
                ["git", "-C", root, "ls-files"],
                capture_output=True, text=True, timeout=30,
            )
            if out.returncode == 0:
                return sorted(line for line in out.stdout.splitlines() if line)
        except (OSError, subprocess.TimeoutExpired):
            pass
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            results.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(results)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _py_imports_exports(text):
    imports, exports = [], []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        for line in text.splitlines():
            m = _PY_IMPORT_RE.match(line)
            if m:
                imports.append(m.group(1) or m.group(2))
        return imports, exports
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                exports.append(node.name)
    return [i for i in imports if i], exports


def _js_imports_exports(text):
    imports = []
    for m in _JS_IMPORT_RE.finditer(text):
        imports.append(m.group(1) or m.group(2))
    exports = [m.group(1) for m in _JS_EXPORT_RE.finditer(text)]
    return imports, exports


def _go_imports_exports(lines):
    imports, exports = [], []
    in_block = False
    for line in lines:
        s = line.strip()
        if s.startswith("import ("):
            in_block = True
            continue
        if in_block:
            if s == ")":
                in_block = False
            elif s and not s.startswith("//"):
                imports.append(s.strip('"'))
            continue
        m = re.match(r'^import\s+"([^"]+)"', s)
        if m:
            imports.append(m.group(1))
        tm = _GO_TOPLEVEL_RE.match(line)
        if tm:
            exports.append(tm.group(2))
    return imports, exports


def analyze_file(root, relpath):
    """Return (lang, role, imports, exports) for one file."""
    base = posixpath.basename(relpath)
    ext = os.path.splitext(base)[1].lower()
    lang = EXTENSION_LANGUAGE.get(ext)
    role = _classify(base, ext)
    path = os.path.join(root, relpath)
    try:
        text = _read(path)
    except OSError as exc:
        raise exc
    lines = text.splitlines()
    imports, exports = [], []
    if lang == "python":
        imports, exports = _py_imports_exports(text)
    elif lang in ("javascript", "typescript", "javascript-react", "typescript-react"):
        imports, exports = _js_imports_exports(text)
    elif lang == "go":
        imports, exports = _go_imports_exports(lines)
    elif lang == "swift":
        imports = [
            m.group(1) for line in lines for m in [_SWIFT_IMPORT_RE.match(line)] if m
        ]
    elif lang == "rust":
        for line in lines:
            m = _RS_USE_RE.match(line)
            if m:
                imports.append(m.group(1).split("::")[0])
    return lang, role, imports, exports


def build_manifest(root):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        raise NotADirectoryError(root)

    entries, warnings, entry_points = [], [], []
    for relpath in _list_files(root):
        base = posixpath.basename(relpath)
        ext = os.path.splitext(base)[1].lower()
        lang = EXTENSION_LANGUAGE.get(ext)
        role = _classify(base, ext)
        imports, exports = [], []
        if lang:
            try:
                _, _, imports, exports = analyze_file(root, relpath)
            except OSError as exc:
                warnings.append("%s: unreadable (%s)" % (relpath, exc.__class__.__name__))
        entries.append({
            "path": relpath.replace(os.sep, "/"),
            "lang": lang,
            "role": role,
            "imports": imports,
            "exports": exports,
        })
        if base == "main.go" or base == "__main__.py":
            entry_points.append(relpath.replace(os.sep, "/"))
        elif lang == "python" and role == "source":
            try:
                if re.search(r"^if\s+__name__\s*[=!]=\s*['\"]__main__['\"]", _read(os.path.join(root, relpath)), re.M):
                    entry_points.append(relpath.replace(os.sep, "/"))
            except OSError:
                pass
        elif base in ("index.js", "main.js", "main.ts") :
            entry_points.append(relpath.replace(os.sep, "/"))

    return {
        "entries": entries,
        "entry_points": sorted(set(entry_points)),
        "warnings": warnings,
    }
