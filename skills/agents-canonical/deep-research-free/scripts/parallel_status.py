#!/usr/bin/env python3
"""Detect Parallel CLI readiness for deep-research fallback decisions.

Exit codes:
  0  ready (authed enough to start research)
  2  fallback to deep-research-free (missing CLI / unauth / API error)
  3  unknown / unexpected

Prints one line: READY|FALLBACK|UNKNOWN\treason
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys


def main() -> int:
    if not shutil.which("parallel-cli"):
        print("FALLBACK\tparallel-cli not on PATH")
        return 2

    try:
        proc = subprocess.run(
            [
                "parallel-cli",
                "research",
                "run",
                "ping",
                "--processor",
                "lite-fast",
                "--no-wait",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as e:
        print(f"FALLBACK\tparallel-cli failed to run: {e}")
        return 2

    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    low = out.lower()

    # Try parse JSON error/success
    payload = None
    for chunk in (proc.stdout or "", out):
        chunk = chunk.strip()
        if chunk.startswith("{"):
            try:
                payload = json.loads(chunk)
                break
            except json.JSONDecodeError:
                pass

    if payload and isinstance(payload, dict):
        if "error" in payload:
            err = payload["error"]
            if isinstance(err, dict):
                msg = str(err.get("message", err))
            else:
                msg = str(err)
            print(f"FALLBACK\t{msg}")
            return 2
        if payload.get("run_id") or payload.get("id"):
            print(f"READY\trun_id={payload.get('run_id') or payload.get('id')}")
            return 0

    if any(
        s in low
        for s in (
            "api key required",
            "not authenticated",
            "parallel_api_key",
            "login",
            "403",
            "insufficient",
        )
    ):
        print(f"FALLBACK\t{out.strip()[:200]}")
        return 2

    if "run_id" in low:
        print("READY\tparsed run_id from text")
        return 0

    print(f"UNKNOWN\texit={proc.returncode} out={out.strip()[:200]}")
    return 3


if __name__ == "__main__":
    sys.exit(main())
