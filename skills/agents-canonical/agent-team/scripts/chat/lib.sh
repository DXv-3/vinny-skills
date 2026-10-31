# shellcheck shell=bash

agent_chat_skill_root() {
  echo "${HOME}/.grok/skills/agent-team"
}

agent_chat_resolve_bus_dir() {
  if [[ -n "${AGENT_CHAT_DIR:-}" ]]; then
    echo "$AGENT_CHAT_DIR"
    return 0
  fi
  echo "$(pwd)/.agent-chat"
}

agent_chat_project_cwd() {
  if [[ -f "$(agent_chat_resolve_bus_dir)/cwd" ]]; then
    cat "$(agent_chat_resolve_bus_dir)/cwd"
    return 0
  fi
  if [[ -n "${AGENT_CHAT_CWD:-}" ]]; then
    echo "$AGENT_CHAT_CWD"
    return 0
  fi
  pwd
}

agent_chat_grok_bin() {
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

agent_chat_now_iso() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

agent_chat_require_jq() {
  command -v jq >/dev/null 2>&1 || {
    echo "agent-chat: install jq (brew install jq)" >&2
    exit 1
  }
}

agent_chat_banner() {
  printf '\n\033[1;36m━━ agent-chat ━━\033[0m %s\n\n' "$1"
}

agent_chat_notify() {
  local title="$1"
  local body="$2"
  if [[ "$(uname)" == "Darwin" ]] && command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"${body//\"/\\\"}\" with title \"${title//\"/\\\"}\"" 2>/dev/null || true
  fi
}

agent_chat_peer() {
  local role="$1"
  if [[ "$role" == "build" ]]; then
    echo "composer"
  else
    echo "build"
  fi
}