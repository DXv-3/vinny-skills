#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

agent_team_require_jq

usage() {
  cat <<'EOF'
Usage: setup-team.sh [options] [task description...]

Creates .agent-team/ in the current directory (or TEAM_DIR).

Options:
  --cwd PATH          Project root (default: pwd)
  --team-dir PATH     Override .agent-team location
  --max-rounds N      Max build↔composer cycles (default: 8)
  --task TEXT         Initial task (or pass as trailing args)
  -h, --help          Show help

Environment:
  GROK_BIN            Path to grok executable
  TEAM_DIR            Target team directory
EOF
}

PROJECT_CWD="$(pwd)"
MAX_ROUNDS=8
TASK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cwd)
      PROJECT_CWD="$(cd "$2" && pwd)"
      shift 2
      ;;
    --team-dir)
      export TEAM_DIR="$2"
      shift 2
      ;;
    --max-rounds)
      MAX_ROUNDS="$2"
      shift 2
      ;;
    --task)
      TASK="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      if [[ -z "$TASK" ]]; then
        TASK="$1"
      else
        TASK="$TASK $1"
      fi
      shift
      ;;
  esac
done

while [[ $# -gt 0 ]]; do
  TASK="$TASK $1"
  shift
done

TEAM_DIR="$(agent_team_resolve_dir)"
if [[ -n "${TEAM_DIR_OVERRIDE:-}" ]]; then
  TEAM_DIR="$TEAM_DIR_OVERRIDE"
fi

if [[ "$TEAM_DIR" != /* ]]; then
  TEAM_DIR="${PROJECT_CWD}/${TEAM_DIR}"
fi

SKILL_ROOT="$(agent_team_skill_root)"
TEMPLATES="${SKILL_ROOT}/templates"

mkdir -p "${TEAM_DIR}/roles" "${TEAM_DIR}/runs"

if [[ ! -f "${TEAM_DIR}/roles/build.md" ]]; then
  cp "${TEMPLATES}/roles/build.md" "${TEAM_DIR}/roles/build.md"
fi
if [[ ! -f "${TEAM_DIR}/roles/composer.md" ]]; then
  cp "${TEMPLATES}/roles/composer.md" "${TEAM_DIR}/roles/composer.md"
fi
if [[ ! -f "${TEAM_DIR}/roles/orchestrator.md" ]]; then
  cp "${TEMPLATES}/roles/orchestrator.md" "${TEAM_DIR}/roles/orchestrator.md"
fi

if [[ -z "$TASK" ]]; then
  TASK="(set task via: orchestrator.sh task \"your goal\")"
fi

jq -n \
  --arg task "$TASK" \
  --arg cwd "$PROJECT_CWD" \
  --argjson max_rounds "$MAX_ROUNDS" \
  '{
    version: 1,
    status: "active",
    turn: "build",
    round: 0,
    max_rounds: $max_rounds,
    task: $task,
    cwd: $cwd,
    models: { build: "grok-build", composer: "grok-composer-2.5-fast" },
    last_role: null,
    updated_at: null
  }' > "${TEAM_DIR}/state.json"

touch "${TEAM_DIR}/events.jsonl"

if [[ "$TASK" != "(set task via: orchestrator.sh task \"your goal\")" ]]; then
  agent_team_append_event "$TEAM_DIR" "$(jq -n \
    --arg body "$TASK" \
    '{type:"task",from:"human",body:$body,verdict:null,artifacts:[],blockers:[]}')"
fi

echo "agent-team ready: ${TEAM_DIR}"
echo "  task:   ${TASK}"
echo "  cwd:    ${PROJECT_CWD}"
echo "  turn:   build"
echo ""
echo "Next:"
echo "  ${SCRIPT_DIR}/orchestrator.sh step    # one agent turn"
echo "  ${SCRIPT_DIR}/orchestrator.sh run     # loop until done"
echo "  ${SCRIPT_DIR}/launch-tmux.sh          # optional tmux dashboard"