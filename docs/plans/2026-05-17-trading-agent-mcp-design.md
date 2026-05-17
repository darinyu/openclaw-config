# TradingAgent MCP Server — Design Document

**Date:** 2026-05-17
**Status:** Implemented

## Overview

An MCP server that wraps [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents),
a multi-agent LLM financial trading framework, exposing it as a callable tool
for OpenClaw agents and as a standalone daemon for CLI use.

## Architecture

```
┌─────────────────────────────────────┐
│  OpenClaw Agent                     │
│  ┌───────────────────────────────┐  │
│  │ Skills: trading-agent         │  │
│  │ → knows about analyze_stock() │  │
│  └──────────┬────────────────────┘  │
│             │ MCP stdio (JSON-RPC)  │
│  ┌──────────▼────────────────────┐  │
│  │ mcp.servers.trading-agent     │  │
│  │ spawns: .sh foreground → .py  │  │
│  └───────────────────────────────┘  │
└──────────┬──────────────────────────┘
           │ stdin/stdout
┌──────────▼──────────────────────────┐
│  trading_agent_mcp.py               │
│  (FastMCP server, stdio transport)  │
│                                     │
│  Tool: analyze_stock()             │
│  → TradingAgentsGraph.propagate()   │
│  → Returns structured JSON report   │
└─────────────────────────────────────┘
```

## Components

### 1. MCP Server (`shared-skills/scripts/trading_agent_mcp.py`)

- Uses the official `mcp` Python SDK (FastMCP) for MCP protocol compliance
- Exposes one tool: `analyze_stock(ticker, date, research_depth)`
- Lazy-loads `TradingAgentsGraph` on first call (heavy import ≈ 3-5s)
- Stdio transport by default; optional HTTP SSE mode via `TRADINGAGENT_MCP_PORT`
- Config is env-var-driven at runtime (`TRADINGAGENTS_LLM_PROVIDER`, API keys, etc.)

**Tool: `analyze_stock`**

| Parameter       | Type   | Required | Default  | Description                          |
|-----------------|--------|----------|----------|--------------------------------------|
| `ticker`        | string | yes      | —        | Stock symbol (AAPL, MSFT, SPY, etc.) |
| `date`          | string | no       | today    | Analysis date (YYYY-MM-DD)           |
| `research_depth`| string | no       | "quick"  | "quick" or "deep"                    |

Returns JSON with: `decision`, `elapsed_seconds`, and intermediate agent outputs
from the LangGraph state (analysts, researchers, trader, risk, portfolio mgr).

### 2. Management Script (`shared-skills/scripts/trading_agent_mcp.sh`)

Standalone shell script for lifecycle management — no LLM or OpenClaw needed.

| Command       | Purpose                                           |
|---------------|---------------------------------------------------|
| `install`     | Create venv, clone TradingAgents, install deps    |
| `start`       | Background daemon with auto-respawn loop          |
| `stop`        | Graceful shutdown                                 |
| `restart`     | Stop + start                                      |
| `status`      | PID, child process, uptime                        |
| `health`      | Full env check (Python, venv, MCP SDK, TA, keys)  |
| `foreground`  | Run server in foreground (for OpenClaw MCP spawn) |
| `venv-py`     | Print venv python path                            |
| `logs [-f]`   | View or follow server logs                        |

The `start` command wraps the Python process in a `while true` loop so it
auto-restarts if it crashes. PID tracking prevents duplicate instances.

### 3. OpenClaw Skill (`skills/trading-agent/`)

- **SKILL.md** — teaches the agent when to invoke `analyze_stock`, how to
  interpret results, and how to troubleshoot
- **_meta.json** — skill metadata for OpenClaw's skill registry
- **config/openclaw.json** — `mcp.servers.trading-agent` registration snippet

The MCP server is registered in OpenClaw config so the agent auto-discovers
the `analyze_stock` tool.

## Data Flow

1. User asks "Analyze AAPL" in Slack/WebChat
2. OpenClaw agent (via trading-agent skill) calls `analyze_stock(ticker="AAPL")`
3. OpenClaw routes to MCP server over stdin/stdout JSON-RPC
4. Python server lazy-loads TradingAgentsGraph, then calls `ta.propagate()`
5. TradingAgents runs its multi-agent pipeline:
   - Analysts gather data (fundamentals, sentiment, news, technical)
   - Researchers debate (bullish vs bearish)
   - Trader proposes action
   - Risk management evaluates
   - Portfolio manager approves/rejects
6. Result is returned as structured JSON
7. Agent formats response for the user

## Provider Configuration

Managed via environment variables (set before starting the server):

```bash
export TRADINGAGENTS_LLM_PROVIDER=deepseek    # Default: openai
export DEEPSEEK_API_KEY=sk-...                 # Provider API key
```

The TradingAgents lib also supports `TRADINGAGENTS_*` env-var overrides
for `deep_think_llm`, `quick_think_llm`, `output_language`, and more.

## File Locations

| File | Purpose |
|------|---------|
| `/data/.openclaw/shared-skills/scripts/trading_agent_mcp.py` | MCP server implementation |
| `/data/.openclaw/shared-skills/scripts/trading_agent_mcp.sh` | Management shell script |
| `~/.openclaw/workspace/skills/trading-agent/SKILL.md` | OpenClaw skill definition |
| `~/.openclaw/workspace/skills/trading-agent/_meta.json` | Skill metadata |
| `~/.openclaw/workspace/skills/trading-agent/config/openclaw.json` | MCP config snippet |
| `~/.tradingagents/venv/` | Python virtual environment |
| `~/.tradingagents/mcp_server.log` | Server log |
| `~/.tradingagents/mcp.pid` | PID file |
| `~/.tradingagents/tradingagents-src/` | Cloned TradingAgents repo |

## Security

- API keys live in environment variables, never in the MCP config or logs
- The MCP server only accepts local stdio connections (no open ports by default)
- TradingAgents runs in a `backtrader` simulated exchange — no real money
- Input ticker is stripped/uppercased before use (no injection vector via ticker)
- All external data fetches use yfinance and tradingagent's own data sources

## Known Limitations

- First import of TradingAgentsGraph takes 3-8 seconds (LangGraph + deps)
- Individual propagate() calls take 30s-5min depending on depth and provider
- No real-time streaming — result is returned after full pipeline completes
- The framework is for research purposes, not financial advice
