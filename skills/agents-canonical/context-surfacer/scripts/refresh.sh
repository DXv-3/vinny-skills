#!/bin/bash
# refresh.sh — Auto-refresh for context-surfacer session index
# Runs session_feeder.py + chat_exporters.py --import-all
# Called by launchd every 15 minutes

SKILL_DIR="$HOME/.claude/skills/context-surfacer"
LOG_DIR="$HOME/.sessions/logs"
mkdir -p "$LOG_DIR"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting refresh" >> "$LOG_DIR/refresh.log"

# Feed new sessions
python3 "$SKILL_DIR/sources/session_feeder.py" >> "$LOG_DIR/refresh.log" 2>&1

# Import any new browser chat exports
python3 "$SKILL_DIR/sources/chat_exporters.py" --import-all >> "$LOG_DIR/refresh.log" 2>&1

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Refresh complete" >> "$LOG_DIR/refresh.log"
