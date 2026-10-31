"""Shared language/file constants for Code Doctor."""

EXCLUDED_DIRS = {
    ".git", "node_modules", "__pycache__", "build", "dist", "DerivedData",
    ".venv", "venv", "env", "target", "vendor", "Pods", ".build",
    ".next", ".turbo", "coverage", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", "eggs", ".eggs", "site-packages",
}

SOURCE_EXTENSIONS = {
    ".swift", ".go", ".rs", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".kt", ".java", ".c", ".cpp", ".cc", ".h", ".hpp", ".m", ".mm",
}

CONFIG_EXTENSIONS = {
    ".plist", ".yml", ".yaml", ".toml", ".json", ".xcconfig",
    ".entitlements", ".ini", ".cfg",
}

DOC_EXTENSIONS = {".md"}

EXTENSION_LANGUAGE = {
    ".swift": "swift",
    ".go": "go",
    ".rs": "rust",
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".kt": "kotlin",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".h": "c-header",
    ".hpp": "cpp-header",
    ".m": "objc",
    ".mm": "objc",
}

# Platform Pitfalls appendix — deterministic items become rules in issues.py;
# these strings feed Phase 0's project-specific checklist.
PITFALLS = {
    "python": [
        "Python: mutable default argument (def f(x=[]))",
        "Python: except:/except Exception: without logging swallows errors",
        "Python: relative import that won't resolve outside a package",
        "Python: file handle not closed (use with statement)",
        "Python: is used for value comparison instead of ==",
    ],
    "javascript": [
        "JS: response sent but handler continues (missing return after res.json())",
        "JS: useEffect runs on every render (missing dependency array)",
        "JS: event listener/setInterval registered, never cleaned up",
        "JS: await missing on async function call",
        "JS: process.env accessed without fallback",
    ],
    "typescript": [
        "TS: response sent but handler continues (missing return after res.json())",
        "TS: useEffect runs on every render (missing dependency array)",
        "TS: event listener/setInterval registered, never cleaned up",
        "TS: await missing on async function call",
        "TS: process.env accessed without fallback",
    ],
    "go": [
        "Go: error returned but not checked (_, or ignored)",
        "Go: goroutine started, never stopped (no context.Context or done channel)",
        "Go: defer in loop — accumulates until function returns",
        "Go: nil map or slice accessed without initialization",
        "Go: race condition on shared variable (run with -race)",
    ],
    "rust": [
        "Rust: .unwrap()/.expect() on Result/Option that can fail",
        "Rust: blocking call inside async without spawn_blocking",
        "Rust: unsafe block without safety documentation",
        "Rust: clone in hot loop instead of reference",
        "Rust: missing Send + Sync bounds on types crossing threads",
    ],
    "swift": [
        "Swift: force unwrap (!) on optional that can be nil at runtime",
        "Swift: @Published property updated from background thread",
        "Swift: strong delegate reference cycle (use weak)",
        "Swift: missing privacy description in Info.plist",
        "Swift: try!/try? on throwing call that should propagate",
    ],
    "react": [
        "React: state update on unmounted component (missing useEffect cleanup)",
        "React: key prop missing or index-as-key in lists",
        "React: derived state not memoized (useMemo/useCallback)",
        "React: effect runs on every render (missing dependency array)",
        "React: controlled/uncontrolled input switching",
    ],
}
