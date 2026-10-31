"""Phase 0: PROFILE — project type, languages, scope, N/A flags, pitfalls."""

import json
import os

from .langs import EXCLUDED_DIRS, EXTENSION_LANGUAGE, PITFALLS


def _root_files(root):
    try:
        return set(os.listdir(root))
    except OSError:
        return set()


def _detect_languages_from_config(root):
    langs = []
    files = _root_files(root)
    if "pyproject.toml" in files or "requirements.txt" in files or "setup.py" in files:
        langs.append("python")
    if "package.json" in files:
        langs.append("javascript")
    if "go.mod" in files:
        langs.append("go")
    if "Cargo.toml" in files:
        langs.append("rust")
    if any(f.endswith(".xcodeproj") for f in files) or "Package.swift" in files:
        langs.append("swift")
    if "CMakeLists.txt" in files or "Makefile" in files:
        langs.extend(["c", "cpp"])
    if "pom.xml" in files or "build.gradle" in files:
        langs.extend(["java", "kotlin"])
    return langs


def _count_files(root):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in EXTENSION_LANGUAGE:
                count += 1
    return count


def _load_package_json(root):
    path = os.path.join(root, "package.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _has_console_script(root):
    path = os.path.join(root, "pyproject.toml")
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return False
    return "[project.scripts]" in content or "[project.gui-scripts]" in content


def detect_project_type(root):
    files = _root_files(root)
    if any(f.endswith(".xcodeproj") for f in files):
        return "mobile app"
    pkg = _load_package_json(root)
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    web_markers = {"react", "next", "vue", "svelte", "angular", "@angular/core",
                   "express", "fastify", "koa"}
    if set(deps) & web_markers or "next.config.js" in files or "next.config.mjs" in files:
        return "web app"
    if pkg.get("bin") or _has_console_script(root):
        return "CLI"
    if "go.mod" in files and os.path.exists(os.path.join(root, "main.go")):
        return "CLI"
    return "library"


def build_na_flags(project_type, languages):
    flags = []
    if project_type != "web app":
        flags.append(
            "N/A — [Web] CORS / rate-limiting / public-endpoint auth items: "
            "project_type is '%s'" % project_type
        )
    js_like = {"javascript", "typescript", "javascript-react", "typescript-react"}
    if not (js_like & set(languages)):
        flags.append(
            "N/A — [JS] event-listener/interval cleanup items: no JavaScript sources"
        )
    if not ("javascript-react" in languages or "typescript-react" in languages):
        flags.append(
            "N/A — React hook items: no JSX/TSX sources detected"
        )
    return flags


def build_pitfalls(languages):
    out = []
    react_like = {"javascript-react", "typescript-react"}
    order = ["swift", "python", "go", "rust"]
    for lang in order:
        if lang in languages:
            out.extend(PITFALLS[lang])
    for lang in ("javascript", "typescript"):
        if lang in languages:
            out.extend(PITFALLS[lang])
    if react_like & set(languages):
        out.extend(PITFALLS["react"])
    if not out:
        out.append("Generic: secrets in code, hardcoded localhost, TODO/FIXME markers")
    return out


def profile_project(root):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        raise NotADirectoryError(root)

    languages = _detect_languages_from_config(root)
    file_count = _count_files(root)

    seen = set(languages)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            lang = EXTENSION_LANGUAGE.get(os.path.splitext(name)[1].lower())
            if lang and lang not in seen:
                seen.add(lang)
                languages.append(lang)

    project_type = detect_project_type(root)
    return {
        "project_root": root,
        "project_type": project_type,
        "languages": languages,
        "file_count": file_count,
        "scope": "full" if file_count <= 100 else "scan",
        "na_flags": build_na_flags(project_type, languages),
        "pitfalls": build_pitfalls(languages),
    }
