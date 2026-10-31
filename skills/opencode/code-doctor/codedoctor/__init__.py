"""Code Doctor — deterministic tooling for the SKILL.md review chain.

Public API:
    profile_project(root)          -> Phase 0 profile dict
    build_manifest(root)           -> Phase 1 manifest dict
    find_issues(root)              -> Phase 3 findings list
    scan_text(text, lang, fname)   -> Phase 3 findings for one in-memory file
    verify_files(paths)            -> Phase 5 syntax-check results
    generate_report(state)         -> Phase 6 markdown report
    SessionState                   -> checkpoint persistence
"""

from .issues import RULES, find_issues, scan_text
from .manifest import analyze_file, build_manifest
from .profile import detect_project_type, profile_project
from .report import generate_report
from .state import SessionState
from .verify import verify_files

__all__ = [
    "RULES",
    "SessionState",
    "analyze_file",
    "build_manifest",
    "detect_project_type",
    "find_issues",
    "generate_report",
    "profile_project",
    "scan_text",
    "verify_files",
]
