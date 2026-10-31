# shellcheck shell=bash
# Shared helpers for agent-team orchestration.

agent_team_skill_root() {
  local src="${BASH_SOURCE[1]:-${BASH_SOURCE[0]}}"
  while [[ -n "$src" && "$src" != "/" ]]; do
    if [[ "$(basename "$(dirname "$src")")" == "scripts" && "$(basename "$(dirname "$(dirname "$src")")")" != "scripts" ]]; then
      dirname "$(dirname "$src")"
      return 0
    fi
    src="$(dirname "$src")"
  done
  echo "${HOME}/.grok/skills/agent-team"
}

agent_team_resolve_dir() {
  if [[ -n "${TEAM_DIR:-}" ]]; then
    echo "$TEAM_DIR"
    return 0
  fi
  if [[ -f ".agent-team/state.json" ]]; then
    echo "$(pwd)/.agent-team"
    return 0
  fi
  echo "$(pwd)/.agent-team"
}

agent_team_grok_bin() {
  if [[ -n "${GROK_BIN:-}" && -x "${GROK_BIN}" ]]; then
    echo "$GROK_BIN"
    return 0
  fi
  if [[ -x "${HOME}/.grok/bin/grok" ]]; then
    echo "${HOME}/.grok/bin/grok"
    return 0
  fi
  command -v grok 2>/dev/null || true
}

agent_team_require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "agent-team: jq is required (brew install jq)" >&2
    exit 1
  fi
}

agent_team_now_iso() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

agent_team_append_event() {
  local team_dir="$1"
  local event_json="$2"
  local stamped
  stamped="$(echo "$event_json" | jq -c --arg ts "$(agent_team_now_iso)" '. + {ts: $ts}')"
  echo "$stamped" >> "${team_dir}/events.jsonl"
  echo "$stamped"
}

agent_team_read_state() {
  local team_dir="$1"
  cat "${team_dir}/state.json"
}

agent_team_write_state() {
  local team_dir="$1"
  local state_json="$2"
  echo "$state_json" | jq '.' > "${team_dir}/state.json"
}

agent_team_recent_events() {
  local team_dir="$1"
  local limit="${2:-12}"
  if [[ ! -f "${team_dir}/events.jsonl" ]]; then
    return 0
  fi
  tail -n "$limit" "${team_dir}/events.jsonl"
}

agent_team_extract_team_event() {
  python3 - "$1" <<'PY'
import json, re, sys
text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
patterns = [
    r"```team-event\s*\n(.*?)\n```",
    r"<team-event>\s*(\{.*?\})\s*</team-event>",
]
for pat in patterns:
    matches = re.findall(pat, text, flags=re.DOTALL | re.IGNORECASE)
    for raw in reversed(matches):
        raw = raw.strip()
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "type" in obj:
            print(json.dumps(obj))
            sys.exit(0)
sys.exit(1)
PY
}

agent_team_build_prompt() {
  local team_dir="$1"
  local role="$2"
  local state
  state="$(agent_team_read_state "$team_dir")"
  local task cwd round max_rounds
  task="$(echo "$state" | jq -r '.task')"
  cwd="$(echo "$state" | jq -r '.cwd')"
  round="$(echo "$state" | jq -r '.round')"
  max_rounds="$(echo "$state" | jq -r '.max_rounds')"
  local role_file="${team_dir}/roles/${role}.md"
  local role_text=""
  if [[ -f "$role_file" ]]; then
    role_text="$(cat "$role_file")"
  fi
  local events
  events="$(agent_team_recent_events "$team_dir" 16)"
  cat <<EOF
You are the **${role}** agent on a two-model engineering team (shared event log).

## Role instructions
${role_text}

## Project
- Working directory: ${cwd}
- Round: ${round} / ${max_rounds}
- Task: ${task}

## Recent team events (newest last)
\`\`\`jsonl
${events}
\`\`\`

## Your job this turn
Follow your role instructions. Read the event log. Produce real work in the repo when appropriate.

## Required machine-readable handoff
End your reply with **exactly one** fenced block (valid JSON inside):

\`\`\`team-event
{"type":"<plan|implement|review|status|error>","from":"${role}","body":"...","verdict":"approve|revise|null","artifacts":[],"blockers":[]}
\`\`\`

Rules:
- **build** first turn on a new task: \`type\` = \`plan\` (architecture + steps, no code dumps).
- **composer** after a plan: \`type\` = \`implement\` (what you changed, tests run).
- **build** after implement: \`type\` = \`review\` and set \`verdict\` to \`approve\` or \`revise\`.
- Use \`status\` only for blockers or questions; keep \`blockers\` non-empty when blocked.
- Use \`error\` if you cannot proceed.
EOF
}