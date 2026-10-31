#!/usr/bin/env bash
# install-launchd.sh — Install context-surfacer auto-refresh LaunchAgent
# Pattern from local-recall/scripts/install-launchd.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_SRC="${SCRIPT_DIR}/com.vinnyos.context-surfacer.refresh.plist"
DEST="${HOME}/Library/LaunchAgents/com.vinnyos.context-surfacer.refresh.plist"

mkdir -p "${HOME}/Library/LaunchAgents" "${HOME}/.sessions/logs"
chmod +x "${SCRIPT_DIR}/refresh.sh"

# Copy plist
cp "$PLIST_SRC" "$DEST"

# Unload if already loaded
launchctl bootout "gui/$(id -u)/com.vinnyos.context-surfacer.refresh" 2>/dev/null || true

# Load
launchctl bootstrap "gui/$(id -u)" "$DEST"
launchctl enable "gui/$(id -u)/com.vinnyos.context-surfacer.refresh" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/com.vinnyos.context-surfacer.refresh" 2>/dev/null || true

echo "Installed LaunchAgent: $DEST"
echo "Interval: every 15 minutes + at load"
echo "Logs: ~/.sessions/logs/"
launchctl print "gui/$(id -u)/com.vinnyos.context-surfacer.refresh" 2>/dev/null | head -20 || true
