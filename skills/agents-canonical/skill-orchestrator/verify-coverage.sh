#!/bin/bash
# verify-coverage.sh — routing test for skill-orchestrator.
# PASS = every library skill in ~/.agents/skills/ token-matches SKILL.md (exit 0).
# FAIL = prints each un routed skill (exit 1). Run after any edit to SKILL.md.
set -u
cd "$(dirname "$0")/.." || exit 1
lib=$(mktemp); tok=$(mktemp)
ls -d */ | sed 's|/$||' | grep -v '^skill-orchestrator$' | sort > "$lib"
grep -oE '[A-Za-z0-9][A-Za-z0-9._-]*' skill-orchestrator/SKILL.md | sed 's/[.,;:)]*$//' | sort -u > "$tok"
total=0; miss=0
while read -r n; do
  total=$((total+1))
  case "$n" in mengto-*) p="${n#mengto-}";; *) p="$n";; esac
  if ! grep -qx -- "$p" "$tok" && ! grep -qx -- "$n" "$tok"; then
    miss=$((miss+1)); echo "UNROUTED: $n"
  fi
done < "$lib"
echo "routed: $((total-miss))/$total library skills"
rm -f "$lib" "$tok"
[ "$miss" -eq 0 ]
