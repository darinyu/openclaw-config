#!/usr/bin/env bash
# MCP Health Check — checks xiaohongshu-mcp and tradingview-mcp liveness
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${MCP_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/mcp-health-check.log"
TIMESTAMP="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
mkdir -p "$LOG_DIR"

echo "===== [$TIMESTAMP] MCP Health Check =====" | tee -a "$LOG_FILE"

XHS_OK=false
TV_OK=false

# ─── Check 1: xiaohongshu-mcp ────────────────────────────────────────────
XHS_LOGIN_OK=false
XHS_CHECK=$(mcporter list xiaohongshu-mcp 2>&1 || true)
if echo "$XHS_CHECK" | grep -q "check_login_status"; then
  echo "[$TIMESTAMP] ✅ xiaohongshu-mcp service is online" | tee -a "$LOG_FILE"
  XHS_OK=true

  # Also check login status (not expired)
  XHS_LOGIN=$(mcporter call xiaohongshu-mcp.check_login_status --timeout 15000 --output json 2>&1 || true)
  if echo "$XHS_LOGIN" | grep -qiE "未登录|not.logged|login.required|请登录"; then
    echo "[$TIMESTAMP] ⚠️ xiaohongshu-mcp login EXPIRED" | tee -a "$LOG_FILE"
    XHS_LOGIN_OK=false
  elif echo "$XHS_LOGIN" | grep -qiE "已登录|logged.in|already.login|success"; then
    echo "[$TIMESTAMP] ✅ xiaohongshu-mcp login is valid" | tee -a "$LOG_FILE"
    XHS_LOGIN_OK=true
  elif echo "$XHS_LOGIN" | grep -qE "timeout"; then
    echo "[$TIMESTAMP] ⚠️ xiaohongshu-mcp login check timed out (may need headless browser)" | tee -a "$LOG_FILE"
    XHS_LOGIN_OK=false
  else
    XHS_LOGIN_TEXT=$(echo "$XHS_LOGIN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(next((c['text'] for c in d.get('content',[]) if c.get('type')=='text'), 'unknown'))" 2>/dev/null || echo "unknown")
    if echo "$XHS_LOGIN_TEXT" | grep -qiE "未登录|not.logged"; then
      echo "[$TIMESTAMP] ⚠️ xiaohongshu-mcp login EXPIRED: $XHS_LOGIN_TEXT" | tee -a "$LOG_FILE"
      XHS_LOGIN_OK=false
    elif echo "$XHS_LOGIN_TEXT" | grep -qiE "已登录|logged.in"; then
      echo "[$TIMESTAMP] ✅ xiaohongshu-mcp login valid: $XHS_LOGIN_TEXT" | tee -a "$LOG_FILE"
      XHS_LOGIN_OK=true
    else
      echo "[$TIMESTAMP] ⚠️ xiaohongshu-mcp login status unknown: $XHS_LOGIN_TEXT" | tee -a "$LOG_FILE"
      XHS_LOGIN_OK=false
    fi
  fi
else
  echo "[$TIMESTAMP] ⚠️ xiaohongshu-mcp is DOWN. Attempting restart..." | tee -a "$LOG_FILE"
  XHS_SKILL_DIR="$SCRIPT_DIR/../skills/xiaohongshu-mcp-openclaw"
  if [ -f "$XHS_SKILL_DIR/scripts/start_server.sh" ]; then
    XHS_BASE_URL=https://www.rednote.com bash "$XHS_SKILL_DIR/scripts/start_server.sh" 2>&1 | tee -a "$LOG_FILE"
    sleep 3
    if mcporter list xiaohongshu-mcp 2>&1 | grep -q "check_login_status"; then
      echo "[$TIMESTAMP] ✅ xiaohongshu-mcp restart successful" | tee -a "$LOG_FILE"
      XHS_OK=true
    else
      echo "[$TIMESTAMP] ❌ xiaohongshu-mcp restart FAILED" | tee -a "$LOG_FILE"
    fi
  else
    echo "[$TIMESTAMP] ❌ xiaohongshu-mcp: start_server.sh not found" | tee -a "$LOG_FILE"
  fi
fi

# ─── Check 2: tradingview-mcp ────────────────────────────────────────────
# Test via Python wrapper (fast, no MCP handshake needed)
TV_TEST=$(python3 /data/.openclaw/tools/trading.py price AAPL 2>&1 || true)
TV_PRICE=$(echo "$TV_TEST" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('price',''))" 2>/dev/null || echo "")
if [ -n "$TV_PRICE" ]; then
  echo "[$TIMESTAMP] ✅ tradingview-mcp is healthy (AAPL: \$$TV_PRICE)" | tee -a "$LOG_FILE"
  TV_OK=true
else
  echo "[$TIMESTAMP] ⚠️ tradingview-mcp is DOWN. Checking process..." | tee -a "$LOG_FILE"
  # Check if the MCP server binary is available
  if /data/.local/bin/tradingview-mcp --version 2>&1 | grep -q .; then
    echo "[$TIMESTAMP] ℹ️  tradingview-mcp binary is present. May need gateway restart." | tee -a "$LOG_FILE"
  else
    echo "[$TIMESTAMP] ℹ️  tradingview-mcp binary check failed." | tee -a "$LOG_FILE"
  fi
fi

# ─── Summary ─────────────────────────────────────────────────────────────
echo "" | tee -a "$LOG_FILE"
if $XHS_OK && $TV_OK; then
  echo "[$TIMESTAMP] ✅ ALL MCP services healthy" | tee -a "$LOG_FILE"
elif $XHS_OK || $TV_OK; then
  echo "[$TIMESTAMP] ⚠️ Partial: XHS=$XHS_OK TV=$TV_OK" | tee -a "$LOG_FILE"
else
  echo "[$TIMESTAMP] ❌ ALL MCP services DOWN" | tee -a "$LOG_FILE"
  exit 1
fi

# Compact mobile-friendly summary (last line visible on mobile)
if $XHS_OK && $TV_OK; then
  if $XHS_LOGIN_OK; then
    echo "✅ XHS online&loggedin | TV ok"
  else
    echo "⚠️ XHS online+login-expired | TV ok"
  fi
elif $XHS_OK && ! $TV_OK; then
  if $XHS_LOGIN_OK; then
    echo "⚠️ XHS online&loggedin | TV down"
  else
    echo "⚠️ XHS online+login-expired | TV down"
  fi
elif ! $XHS_OK && $TV_OK; then
  echo "⚠️ XHS down | TV ok"
else
  echo "❌ XHS down | TV down"
fi

echo "" | tee -a "$LOG_FILE"
