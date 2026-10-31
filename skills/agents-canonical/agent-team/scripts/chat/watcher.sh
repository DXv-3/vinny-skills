#!/usr/bin/env bash
# Background watcher: notifies when peer sends a message on the bus.
set -euo pipefail

ROLE="${1:?role required: build or composer}"
CHAT_DIR="${2:?chat dir required}"

# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

BUS="${CHAT_DIR}/bus.jsonl"
OFFSET_FILE="${CHAT_DIR}/watch-${ROLE}.offset"
LOG="${CHAT_DIR}/watch-${ROLE}.log"
PEER="$(agent_chat_peer "$ROLE")"

mkdir -p "$CHAT_DIR"
touch "$BUS"
[[ -f "$OFFSET_FILE" ]] || echo "0" > "$OFFSET_FILE"

echo "$(agent_chat_now_iso) watcher ${ROLE} started (peer=${PEER})" >> "$LOG"

while true; do
  if [[ ! -f "$BUS" ]]; then
    sleep 1
    continue
  fi
  offset="$(cat "$OFFSET_FILE")"
  count="$(wc -l < "$BUS" | tr -d ' ')"
  if [[ "$count" -le "$offset" ]]; then
    sleep 0.4
    continue
  fi
  tail -n +"$((offset + 1))" "$BUS" | while IFS= read -r line; do
    from="$(echo "$line" | jq -r '.from // empty')"
    to="$(echo "$line" | jq -r '.to // empty')"
    body="$(echo "$line" | jq -r '.body // empty')"
    if [[ "$from" == "$ROLE" ]]; then
      continue
    fi
    if [[ "$to" != "$ROLE" && "$to" != "all" ]]; then
      continue
    fi
    short="${body:0:200}"
    [[ "${#body}" -gt 200 ]] && short="${short}…"
    stamp="$(date '+%H:%M:%S')"
    msg="[${stamp}] ${from} → ${ROLE}: ${short}"
    echo "$msg" >> "$LOG"
    printf '\a' 2>/dev/null || true
    agent_chat_notify "agent-chat (${ROLE})" "${from}: ${short}"
    agent_chat_banner "${from} → you"
    echo "$body"
    echo ""
    echo "Reply: agent-chat send ${ROLE} \"...\""
    echo "---"
  done
  echo "$count" > "$OFFSET_FILE"
  sleep 0.4
done