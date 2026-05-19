#!/usr/bin/env bash
# 30-min health check for xiaohongshu-mcp server
# Checks via mcporter, restarts if needed, posts status to Slack
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
XHS_SKILL_DIR="$(dirname "$SKILL_DIR")/xiaohongshu-mcp-openclaw"
LOG_DIR="${XHS_MCP_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/xhs-mcp-health-check.log"
TIMESTAMP="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

mkdir -p "$LOG_DIR"

echo "[$TIMESTAMP] Checking xiaohongshu-mcp status..." | tee -a "$LOG_FILE"

# Check 1: mcporter can list the MCP tools
if mcporter list xiaohongshu-mcp 2>&1 | grep -q "check_login_status"; then
  echo "[$TIMESTAMP] ✅ xiaohongshu-mcp is healthy" | tee -a "$LOG_FILE"
  exit 0
fi

echo "[$TIMESTAMP] ⚠️ xiaohongshu-mcp is DOWN. Attempting restart..." | tee -a "$LOG_FILE"

# Check 2: Try restart
if [ -f "$XHS_SKILL_DIR/scripts/start_server.sh" ]; then
  bash "$XHS_SKILL_DIR/scripts/start_server.sh" 2>&1 | tee -a "$LOG_FILE"
  RESTART_EXIT=$?
else
  echo "[$TIMESTAMP] ❌ start_server.sh not found at $XHS_SKILL_DIR/scripts/start_server.sh" | tee -a "$LOG_FILE"
  RESTART_EXIT=1
fi

# Check 3: Verify restart succeeded
sleep 3
if mcporter list xiaohongshu-mcp 2>&1 | grep -q "check_login_status"; then
  echo "[$TIMESTAMP] ✅ Restart successful" | tee -a "$LOG_FILE"
  # Post to Slack via openclaw cron output or write status
  echo "xiaohongshu-mcp was DOWN, restart successful."
else
  echo "[$TIMESTAMP] ❌ Restart FAILED" | tee -a "$LOG_FILE"
  tail -n 20 "$LOG_FILE"
  echo "xiaohongshu-mcp was DOWN and restart FAILED. Check logs: $LOG_FILE"
  exit 1
fi
