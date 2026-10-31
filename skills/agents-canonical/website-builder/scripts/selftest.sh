#!/bin/bash
# website-builder skill selftest (offline, stdlib only). Exit 0 = pass.
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$HERE/SKILL.md"
fail() { echo "FAIL: $1" >&2; exit 1; }

[ -f "$SKILL" ] || fail "SKILL.md missing at $SKILL"

# Frontmatter: exactly one name: line and one description: line inside the leading --- block.
awk '/^---$/{c++; next} c==1{print}' "$SKILL" > /tmp/wb_frontmatter.$$
grep -c '^name: website-builder$' /tmp/wb_frontmatter.$$ | grep -qx '1' || fail "frontmatter name line"
grep -c '^description: Use when' /tmp/wb_frontmatter.$$ | grep -qx '1' || fail "frontmatter description line"
awk '/^[a-zA-Z-]+:/ {print $1}' /tmp/wb_frontmatter.$$ | sort -u | tr -d ':' > /tmp/wb_fields.$$
diff -q <(printf 'description\nname\n') /tmp/wb_fields.$$ >/dev/null || fail "frontmatter must have exactly name+description"
rm -f /tmp/wb_frontmatter.$$ /tmp/wb_fields.$$

# Required sections present.
for section in "## Money frame" "## Intake" "## Stack law" "## Workflow (journey-first, per the motion spec)" "## Film stage (Flute)" "## Verification gates (fill before any handoff)" "## Deliver" "## Run + selftest"; do
  grep -qF "$section" "$SKILL" || fail "missing section: $section"
done

# Provenance marker back to the verbatim source revision.
grep -q 'sha256:c092a96b' "$SKILL" || fail "provenance revision marker missing"

# English-only law: no CJK characters in the adapted skill body.
if LC_ALL=C grep -n '[^[:print:][:space:]]' "$SKILL" | grep -q .; then
  fail "non-ASCII characters found (English-only law)"
fi

echo "website-builder selftest: OK (frontmatter, sections, provenance, English-only)"
exit 0
