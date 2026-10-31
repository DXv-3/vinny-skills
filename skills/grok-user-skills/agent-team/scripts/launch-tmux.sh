#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

TEAM_DIR="$(agent_team_resolve_dir)"
if [[ "$TEAM_DIR" != /* ]]; then
  TEAM_DIR="$(pwd)/.agent-team"
fi

GROK_BIN="$(agent_team_grok_bin)"
PROJECT_CWD="$(pwd)"
if [[ -f "${TEAM_DIR}/state.json" ]]; then
  PROJECT_CWD="$(jq -r '.cwd' "${TEAM_DIR}/state.json")"
fi

SESSION_NAME="${AGENT_TEAM_TMUX_SESSION:-agent-team}"

if ! command -v tmux >/dev/null 2>&1; then
  cat >&2 <<EOF
agent-team: tmux is not installed.

Install:  brew install tmux

Without tmux you can still run:
  ${SCRIPT_DIR}/orchestrator.sh run
  tail -f ${TEAM_DIR}/events.jsonl
EOF
  exit 1
fi

if [[ ! -f "${TEAM_DIR}/state.json" ]]; then
  echo "agent-team: run setup first: ${SCRIPT_DIR}/orchestrator.sh setup \"your task\"" >&2
  exit 1
fi

MODEL_BUILD="$(jq -r '.models.build' "${TEAM_DIR}/state.json")"
MODEL_COMPOSER="$(jq -r '.models.composer' "${TEAM_DIR}/state.json")"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "attaching to existing session: $SESSION_NAME"
  exec tmux attach -t "$SESSION_NAME"
fi

ORCH_CMD="cd '${PROJECT_CWD}' && TEAM_DIR='${TEAM_DIR}' GROK_BIN='${GROK_BIN}' '${SCRIPT_DIR}/orchestrator.sh' run --sleep 5"
EVENTS_CMD="cd '${PROJECT_CWD}' && tail -f '${TEAM_DIR}/events.jsonl' | while read -r line; do echo \"\$line\" | jq -c '{ts,type,from,verdict,body:(.body|tostring|.[:100])}' 2>/dev/null || echo \"\$line\"; done"
BUILD_CMD="cd '${PROJECT_CWD}' && '${GROK_BIN}' -m '${MODEL_BUILD}'"
COMPOSER_CMD="cd '${PROJECT_CWD}' && '${GROK_BIN}' -m '${MODEL_COMPOSER}'"

tmux new-session -d -s "$SESSION_NAME" -n team -c "$PROJECT_CWD" \
  "${ORCH_CMD}"

tmux split-window -h -t "$SESSION_NAME":0 -c "$PROJECT_CWD" \
  bash -lc "${EVENTS_CMD}"

tmux split-window -v -t "$SESSION_NAME":0.0 -c "$PROJECT_CWD" \
  bash -lc "${BUILD_CMD}"

tmux split-window -v -t "$SESSION_NAME":0.1 -c "$PROJECT_CWD" \
  bash -lc "${COMPOSER_CMD}"

tmux select-layout -t "$SESSION_NAME":0 tiled
tmux select-pane -t "$SESSION_NAME":0.0

tmux set-window-option -t "$SESSION_NAME":0 pane-border-status top
tmux set-option -t "$SESSION_NAME" remain-on-exit on

cat <<EOF
agent-team tmux session: ${SESSION_NAME}

Panes:
  0  orchestrator (automated run loop)
  1  event log (tail)
  2  grok-build (manual)
  3  composer (manual)

Attach: tmux attach -t ${SESSION_NAME}
EOF

exec tmux attach -t "$SESSION_NAME"