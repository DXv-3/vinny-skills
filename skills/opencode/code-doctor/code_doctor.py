#!/usr/bin/env python3
"""Code Doctor CLI — deterministic phases of the SKILL.md chain.

Usage:
  code_doctor.py profile <dir>            Phase 0: project profile
  code_doctor.py scan [--json] <dir>      Phases 0+1+3: profile, manifest, findings
  code_doctor.py check-syntax <file>...   Phase 5 BUILD gate per file
  code_doctor.py run <dir>                Full deterministic chain + state save
  code_doctor.py report <dir>             Render Phase 6 markdown from saved state

Exit codes: 0 clean | 1 findings found | 2 error.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codedoctor.issues import find_issues
from codedoctor.manifest import build_manifest
from codedoctor.profile import profile_project
from codedoctor.report import generate_report
from codedoctor.state import SessionState
from codedoctor.verify import verify_files


def _emit(obj, as_json):
    if as_json:
        print(json.dumps(obj, indent=1))
    else:
        for key, val in obj.items():
            print("%s: %s" % (key, val))


def cmd_profile(args):
    profile = profile_project(args.dir)
    _emit(profile, args.json)
    return 0


def cmd_scan(args):
    profile = profile_project(args.dir)
    manifest = build_manifest(args.dir)
    findings = find_issues(args.dir)
    counts = {"critical": 0, "functional": 0, "quality": 0}
    for f in findings:
        counts[f["severity"]] += 1
    payload = {
        "profile": profile,
        "manifest": {
            "entries": manifest["entries"],
            "entry_points": manifest["entry_points"],
            "warnings": manifest["warnings"],
        },
        "findings": findings,
        "summary": counts,
    }
    if args.json:
        print(json.dumps(payload, indent=1))
    else:
        print("Project: %s (%s)" % (profile["project_type"], ", ".join(profile["languages"])))
        print("Scope: %d source files — %s read" % (profile["file_count"], profile["scope"]))
        print("Files in manifest: %d" % len(manifest["entries"]))
        if manifest["entry_points"]:
            print("Entry points: %s" % ", ".join(manifest["entry_points"]))
        print("Findings: %d critical / %d functional / %d quality"
              % (counts["critical"], counts["functional"], counts["quality"]))
        by_sev = {"critical": [], "functional": [], "quality": []}
        for f in findings:
            by_sev[f["severity"]].append(f)
        for sev in ("critical", "functional", "quality"):
            for f in by_sev[sev]:
                print("  [%s] %s:%d %s — %s"
                      % (sev, f["file"], f["line"], f["rule_id"], f["message"]))
    return 1 if findings else 0


def cmd_check_syntax(args):
    results = verify_files(args.files)
    failed = False
    for r in results:
        mark = r["status"].upper()
        print("%-8s %s%s" % (mark, r["file"], ": " + r["output"] if r["output"] else ""))
        if not r["ok"]:
            failed = True
    return 1 if failed else 0


def cmd_run(args):
    state = SessionState.load(args.dir)
    state.profile = profile_project(args.dir)
    state.phases_done.append("profile")
    manifest = build_manifest(args.dir)
    state.manifest_entries = manifest["entries"]
    state.entry_points = manifest["entry_points"]
    state.phases_done.append("manifest")
    state.findings = find_issues(args.dir)
    state.phases_done.append("issues")
    state.save()
    counts = state.severity_counts()
    total = sum(counts.values())
    print("Chain complete → %s" % state.path)
    print("Findings: %d (c:%d f:%d q:%d)"
          % (total, counts["critical"], counts["functional"], counts["quality"]))
    print("Next: agent verifies contracts (Phase 2), fixes (Phase 4), then `report`.")
    return 1 if total else 0


def cmd_report(args):
    state = SessionState.load(args.dir)
    if not state.phases_done:
        print("No saved chain state; run `code_doctor.py run <dir>` first.", file=sys.stderr)
        return 2
    print(generate_report(state))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="codedoctor", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("profile", help="Phase 0 project profile")
    p.add_argument("dir")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("scan", help="Phases 0+1+3: profile, manifest, findings")
    p.add_argument("--json", action="store_true")
    p.add_argument("dir")

    p = sub.add_parser("check-syntax", help="Phase 5 syntax gate on files")
    p.add_argument("files", nargs="+")

    p = sub.add_parser("run", help="Full deterministic chain, saves state")
    p.add_argument("dir")

    p = sub.add_parser("report", help="Phase 6 markdown report from saved state")
    p.add_argument("dir")

    args = parser.parse_args(argv)
    handlers = {
        "profile": cmd_profile,
        "scan": cmd_scan,
        "check-syntax": cmd_check_syntax,
        "run": cmd_run,
        "report": cmd_report,
    }
    try:
        return handlers[args.command](args)
    except (NotADirectoryError, FileNotFoundError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
