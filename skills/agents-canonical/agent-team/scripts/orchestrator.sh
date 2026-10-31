#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

agent_team_require_jq

usage() {
  cat <<'EOF'
Usage: orchestrator.sh <command> [args]

Commands:
  setup [task...]       Initialize .agent-team (calls setup-team.sh)
  task <text>           Set/replace task, reset to build turn
  step                  Run exactly one agent turn
  run [--sleep SEC]     Loop step until done, error, or max_rounds
  status                Print state + last 5 events
  emit <json>           Append a manual event (must be JSON object)
  pause | resume        Stop or continue automated runs

Environment:
  TEAM_DIR, GROK_BIN, AGENT_TEAM_SLEEP (default 4)
EOF
}

cmd="${1:-status}"
shift || true

TEAM_DIR="$(agent_team_resolve_dir)"
if [[ "$TEAM_DIR" != /* ]]; then
  TEAM_DIR="$(cd "$(dirname "$TEAM_DIR")" 2>/dev/null && pwd)/$(basename "$TEAM_DIR")" || TEAM_DIR="$(pwd)/.agent-team"
fi

GROK_BIN="$(agent_team_grok_bin)"
if [[ -z "$GROK_BIN" ]]; then
  echo "agent-team: grok not found (set GROK_BIN)" >&2
  exit 1
fi

ensure_team() {
  if [[ ! -f "${TEAM_DIR}/state.json" ]]; then
    echo "agent-team: no state at ${TEAM_DIR}/state.json — run: orchestrator.sh setup \"your task\"" >&2
    exit 1
  fi
}

update_state_fields() {
  local patch="$1"
  local state
  state="$(agent_team_read_state "$TEAM_DIR")"
  state="$(echo "$state" | jq --arg now "$(agent_team_now_iso)" ". + $patch + {updated_at: \$now}")"
  agent_team_write_state "$TEAM_DIR" "$state"
}

next_turn_after_event() {
  local event="$1"
  local state
  state="$(agent_team_read_state "$TEAM_DIR")"
  local etype from verdict round max_rounds status
  etype="$(echo "$event" | jq -r '.type')"
  from="$(echo "$event" | jq -r '.from // empty')"
  verdict="$(echo "$event" | jq -r '.verdict // empty')"
  round="$(echo "$state" | jq -r '.round')"
  max_rounds="$(echo "$state" | jq -r '.max_rounds')"

  case "$etype" in
    plan)
      update_state_fields '{"turn":"composer","last_role":"build"}'
      ;;
    implement)
      round=$((round + 1))
      if [[ "$round" -ge "$max_rounds" ]]; then
        update_state_fields "$(jq -n --argjson r "$round" '{turn:null,round:$r,status:"max_rounds",last_role:"composer"}')"
      else
        update_state_fields "$(jq -n --argjson r "$round" '{turn:"build",round:$r,last_role:"composer"}')"
      fi
      ;;
    review)
      if [[ "$verdict" == "approve" ]]; then
        update_state_fields '{"turn":null,"status":"done","last_role":"build"}'
      else
        update_state_fields '{"turn":"composer","last_role":"build"}'
      fi
      ;;
    status)
      update_state_fields '{"turn":"build","last_role":"'"$from"'"}'
      ;;
    error)
      update_state_fields '{"turn":null,"status":"error","last_role":"'"$from"'"}'
      ;;
    task)
      update_state_fields '{"turn":"build","status":"active","round":0,"last_role":"human"}'
      ;;
    done)
      update_state_fields '{"turn":null,"status":"done"}'
      ;;
    *)
      echo "agent-team: unknown event type: $etype" >&2
      ;;
  esac
}

run_one_step() {
  ensure_team
  local state
  state="$(agent_team_read_state "$TEAM_DIR")"
  local status turn cwd model_build model_composer
  status="$(echo "$state" | jq -r '.status')"
  turn="$(echo "$state" | jq -r '.turn')"
  cwd="$(echo "$state" | jq -r '.cwd')"
  model_build="$(echo "$state" | jq -r '.models.build')"
  model_composer="$(echo "$state" | jq -r '.models.composer')"

  if [[ "$status" == "paused" ]]; then
    echo "agent-team: paused"
    return 0
  fi
  if [[ "$status" != "active" ]]; then
    echo "agent-team: status=$status (nothing to do)"
    return 0
  fi
  if [[ "$turn" == "null" || -z "$turn" ]]; then
    echo "agent-team: no active turn (status=$status)"
    return 0
  fi

  local model="$model_composer"
  if [[ "$turn" == "build" ]]; then
    model="$model_build"
  fi

  local prompt
  prompt="$(agent_team_build_prompt "$TEAM_DIR" "$turn")"
  local run_id
  run_id="$(date +%Y%m%dT%H%M%S)-${turn}"
  local log_dir="${TEAM_DIR}/runs"
  mkdir -p "$log_dir"

  echo "agent-team: running ${turn} (${model}) → ${log_dir}/${run_id}.log"
  local raw_json
  if ! raw_json="$("$GROK_BIN" -p "$prompt" -m "$model" --cwd "$cwd" \
      --output-format json --no-subagents --permission-mode bypassPermissions \
      2>"${log_dir}/${run_id}.stderr" | tee "${log_dir}/${run_id}.raw.json")"; then
    agent_team_append_event "$TEAM_DIR" "$(jq -n \
      --arg body "grok invocation failed; see ${run_id}.stderr" \
      '{type:"error",from:"orchestrator",body:$body,verdict:null,artifacts:[],blockers:[]}')"
    update_state_fields '{"status":"error","turn":null}'
    return 1
  fi

  local text
  text="$(echo "$raw_json" | jq -r '.text // empty')"
  echo "$text" > "${log_dir}/${run_id}.txt"

  local team_event
  if ! team_event="$(agent_team_extract_team_event "$text" 2>/dev/null)"; then
    agent_team_append_event "$TEAM_DIR" "$(jq -n \
      --arg body "Agent did not emit a team-event block. See ${run_id}.txt" \
      '{type:"error",from:"orchestrator",body:$body,verdict:null,artifacts:[],blockers:[]}')"
    update_state_fields '{"status":"error","turn":null}'
    echo "agent-team: missing team-event in response" >&2
    return 1
  fi

  team_event="$(echo "$team_event" | jq --arg from "$turn" '. + {from: (.from // $from)}')"
  local stamped
  stamped="$(agent_team_append_event "$TEAM_DIR" "$team_event")"
  echo "agent-team: event $(echo "$stamped" | jq -c '{type,from,verdict}')"
  next_turn_after_event "$stamped"
}

cmd_setup() {
  exec "${SCRIPT_DIR}/setup-team.sh" --cwd "$(pwd)" "$@"
}

cmd_task() {
  local text="$*"
  if [[ -z "$text" ]]; then
    echo "usage: orchestrator.sh task <description>" >&2
    exit 1
  fi
  ensure_team
  update_state_fields "$(jq -n --arg t "$text" '{task:$t,status:"active",turn:"build",round:0}')"
  agent_team_append_event "$TEAM_DIR" "$(jq -n \
    --arg body "$text" \
    '{type:"task",from:"human",body:$body,verdict:null,artifacts:[],blockers:[]}')"
  echo "agent-team: task set, turn=build"
}

cmd_status() {
  ensure_team
  echo "=== state (${TEAM_DIR}/state.json) ==="
  agent_team_read_state "$TEAM_DIR" | jq .
  echo ""
  echo "=== recent events ==="
  agent_team_recent_events "$TEAM_DIR" 5 | jq -c '{ts,type,from,verdict,body:(.body|tostring|.[:120])}' 2>/dev/null || true
}

cmd_emit() {
  local json="$*"
  ensure_team
  echo "$json" | jq . >/dev/null
  agent_team_append_event "$TEAM_DIR" "$json"
  next_turn_after_event "$json"
}

cmd_pause() {
  ensure_team
  update_state_fields '{"status":"paused"}'
  echo "agent-team: paused"
}

cmd_resume() {
  ensure_team
  update_state_fields '{"status":"active"}'
  echo "agent-team: resumed"
}

cmd_run() {
  local sleep_sec="${AGENT_TEAM_SLEEP:-4}"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --sleep) sleep_sec="$2"; shift 2 ;;
      *) break ;;
    esac
  done
  ensure_team
  while true; do
    local status
    status="$(agent_team_read_state "$TEAM_DIR" | jq -r '.status')"
    if [[ "$status" != "active" ]]; then
      echo "agent-team: finished (status=$status)"
      cmd_status
      break
    fi
    run_one_step || true
    status="$(agent_team_read_state "$TEAM_DIR" | jq -r '.status')"
    if [[ "$status" != "active" ]]; then
      echo "agent-team: finished (status=$status)"
      cmd_status
      break
    fi
    sleep "$sleep_sec"
  done
}

case "$cmd" in
  setup) cmd_setup "$@" ;;
  task) cmd_task "$@" ;;
  step) run_one_step ;;
  run) cmd_run "$@" ;;
  status) cmd_status ;;
  emit) cmd_emit "$@" ;;
  pause) cmd_pause ;;
  resume) cmd_resume ;;
  -h|--help) usage ;;
  *)
    echo "unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac