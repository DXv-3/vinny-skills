#!/usr/bin/env bash
# Smoke-test deep-research-free skill packaging + prior artifacts.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_MIRROR="${HOME}/.agents/skills/deep-research-free"
RESEARCH_DIR="${HOME}/Documents/research"
VALIDATE="${SKILL_DIR}/scripts/validate_research_output.py"
FAIL=0

pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*"; FAIL=1; }

echo "=== deep-research-free smoke ==="
echo "SKILL_DIR=$SKILL_DIR"

# 1. Core files
for f in SKILL.md templates/run_manifest.json templates/report.md scripts/validate_research_output.py; do
  if [[ -f "${SKILL_DIR}/${f}" ]]; then pass "exists ${f}"
  else fail "missing ${f}"; fi
done

# 2. Template JSON parses
if python3 -c "import json; json.load(open('${SKILL_DIR}/templates/run_manifest.json'))"; then
  pass "run_manifest.json parses"
else
  fail "run_manifest.json invalid"
fi

# 3. Skill has Parallel-pattern requirements
for needle in "interaction_id" "deep-research-free" "surfaces_covered" "kickoff" "tier"; do
  if rg -q "$needle" "${SKILL_DIR}/SKILL.md"; then pass "SKILL.md has ${needle}"
  else fail "SKILL.md missing ${needle}"; fi
done

# 4. Mirror sync (warn if missing; fail if diverge when present)
if [[ -d "$AGENTS_MIRROR" ]]; then
  if diff -rq "$SKILL_DIR" "$AGENTS_MIRROR" >/tmp/drf-diff.txt 2>&1; then
    pass "agents mirror in sync"
  else
    fail "agents mirror out of sync (run rsync)"
    cat /tmp/drf-diff.txt | head -20
  fi
else
  fail "agents mirror missing at $AGENTS_MIRROR"
fi

# 5. Parallel skill fallback section
PAR="${HOME}/.agents/skills/parallel-deep-research/SKILL.md"
if [[ -f "$PAR" ]] && rg -q "Auto-fallback" "$PAR" && rg -q "deep-research-free" "$PAR"; then
  pass "parallel-deep-research has free fallback"
else
  fail "parallel-deep-research missing free fallback"
fi

# 6. Research dir + validator executable
mkdir -p "$RESEARCH_DIR"
chmod +x "$VALIDATE" 2>/dev/null || true
if [[ -x "$VALIDATE" ]] || [[ -f "$VALIDATE" ]]; then pass "validator present"
else fail "validator missing"; fi

# 7. Validate known prior artifact if present
PRIOR="${RESEARCH_DIR}/local-activity-intelligence-stack-2026"
if [[ -f "${PRIOR}.json" ]]; then
  if python3 "$VALIDATE" "$PRIOR"; then pass "prior research validates"
  else fail "prior research invalid"; fi
else
  echo "SKIP: no prior research at $PRIOR"
fi

# 8. Synthetic minimal artifact round-trip
SYN_STEM="${RESEARCH_DIR}/_smoke-synthetic-$$"
python3 - <<PY
import json
from pathlib import Path
from datetime import datetime, timezone
stem = Path("${SYN_STEM}")
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
iid = "free-smoke-test"
md = f"""# Smoke Topic — Deep Research Report
Generated: {now}
Engine: deep-research-free
Tier: lite
interaction_id: {iid}

## 1. Executive Summary

Synthetic smoke report for validator and packaging checks. Not real research.

## 2. Key Findings

- Packaging works ([Example](https://example.com))

## 8. Sources

- [Example](https://example.com)
"""
js = {
  "interaction_id": iid,
  "previous_interaction_id": None,
  "engine": "deep-research-free",
  "tier": "lite",
  "topic": "smoke",
  "steer": "minimal",
  "filename": stem.name,
  "generated_at": now,
  "sub_questions": ["does packaging work?"],
  "surfaces_covered": ["docs"],
  "sources": [{
    "id": "S1",
    "url": "https://example.com",
    "title": "Example",
    "surface": "docs",
    "accessed": now[:10],
    "role": "primary"
  }],
  "claims": [{
    "claim": "smoke packaging produces dual artifacts",
    "support": "confirmed",
    "source_ids": ["S1"]
  }],
  "conflicts": [],
  "recommendations": ["keep dual artifacts"],
  "gaps": [],
  "follow_up_hooks": ["none"],
  "methodology": {"search_count": 0, "primary_fetch_count": 0, "critique_pass": False, "limitations": ["synthetic"]}
}
stem.with_suffix(".md").write_text(md, encoding="utf-8")
stem.with_suffix(".json").write_text(json.dumps(js, indent=2), encoding="utf-8")
print("wrote", stem)
PY

if python3 "$VALIDATE" "$SYN_STEM"; then pass "synthetic dual artifacts validate"
else fail "synthetic dual artifacts invalid"; fi
rm -f "${SYN_STEM}.md" "${SYN_STEM}.json"

# 9. Parallel status helper (authoritative fallback detect)
STATUS_PY="${SKILL_DIR}/scripts/parallel_status.py"
if [[ -f "$STATUS_PY" ]]; then
  set +e
  STATUS_OUT="$(python3 "$STATUS_PY" 2>&1)"
  STATUS_RC=$?
  set -e
  if [[ "$STATUS_RC" -eq 0 || "$STATUS_RC" -eq 2 ]]; then
    pass "parallel_status.py rc=$STATUS_RC ($STATUS_OUT)"
  else
    fail "parallel_status.py unexpected rc=$STATUS_RC ($STATUS_OUT)"
  fi
else
  fail "parallel_status.py missing"
fi

# 10. E2E lite research artifact (if present from last run)
LITE="${RESEARCH_DIR}/activity-stack-install-lite-2026"
if [[ -f "${LITE}.json" ]]; then
  if python3 "$VALIDATE" "$LITE"; then pass "e2e lite research validates"
  else fail "e2e lite research invalid"; fi
else
  echo "SKIP: no e2e lite at $LITE (optional)"
fi

echo "=== summary ==="
if [[ "$FAIL" -eq 0 ]]; then
  echo "ALL SMOKE CHECKS PASSED"
  exit 0
else
  echo "SMOKE FAILED"
  exit 1
fi
