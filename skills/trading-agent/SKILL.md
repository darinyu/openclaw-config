---
name: trading-agent
description: "Multi-agent LLM stock trading analysis via TradingAgents. Analyzes stocks with fundamentals, sentiment, news, technical analysis, debate, risk assessment, and portfolio management — all via AI agents."
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins: ["python3", "bash", "git"]
      pkgs: ["mcp"]
    install:
      - id: setup
        kind: exec
        cmd: "bash /data/.openclaw/shared-skills/scripts/trading_agent_mcp.sh install"
        label: "Install TradingAgents + MCP deps"
      - id: start
        kind: exec
        cmd: "bash /data/.openclaw/shared-skills/scripts/trading_agent_mcp.sh start"
        label: "Start MCP server daemon"
---

# TradingAgent MCP

This skill gives you access to **TradingAgents**, a multi-agent LLM trading
framework that deploys specialized AI agents (Fundamentals, Sentiment, News,
Technical Analysts → Bullish/Bearish Researchers → Trader → Risk Management
→ Portfolio Manager) to analyze stocks and produce trading decisions.

An MCP tool `analyze_stock` is registered and available. You do **not** need
to call any external scripts directly — just use the tool when someone asks
about a stock.

## MCP Tool: `analyze_stock`

| Parameter       | Type   | Required | Default  | Description                                                  |
|-----------------|--------|----------|----------|--------------------------------------------------------------|
| `ticker`        | string | ✅       | —        | Stock ticker (e.g. AAPL, MSFT, SPY, TSLA, GOOGL)             |
| `date`          | string | ❌       | today    | Analysis date in YYYY-MM-DD format                           |
| `research_depth`| string | ❌       | "deep"   | "deep" (3 debate rounds) or "quick" (1 debate round)          |

Returns structured JSON with:
- **decision** — The Portfolio Manager's final trading decision
- **elapsed_seconds** — How long it took
- **analyst / researcher / trader / risk state** — Intermediate agent outputs

## 🎯 Agent Behavior (CRITICAL — Long-Running Analyses)

**Analyses take 3-15 minutes.** Users must not wait silently. Follow this pattern:

### Mandatory Status Updates

1. **Acknowledge immediately** — When a user asks to analyze a stock, reply right
   away saying the analysis has started and how long it will take (3-5 min for
   quick, 8-15 min for deep).

2. **Send intermittent progress updates** — While the analysis is running, post
   periodic status updates to the thread/conversation. The update frequency is:

   - After ~1 minute: "Agents are gathering data..."
   - After ~2-3 minutes: "Analysts have completed their reports. Debate is starting..."
   - After ~5-6 minutes (deep only): "Risk assessment in progress..."
   - Once done: Final results

3. **Final update** — Full results summary + GitHub link

### How to Send Updates

- **On Slack/thread**: Use `message(action=send)` with the correct `threadId`
  (the source message's `ts`) for each update.
- **On WebChat/Control UI**: Content automatically appears in this session, so
  reply naturally.
- Keep updates concise — a short sentence + elapsed time marker is enough.
- Don't send updates more than once per ~90 seconds to avoid noise.

### Progress Indicators During MCP/Shell Execution

Since the analysis runs as a subprocess (via exec or MCP tool), you need to
**poll the process** to check intermediate state.

**⚠️ Polling gotcha:** When using `process(action=poll, timeout=...)`, a
timeout with "no new output" does NOT mean the process is still running —
it means the process wrote no new output during the wait window. The
process may have already exited. Always check the exit code / status
(e.g. `process(action=log)` or `process(action=poll)` with a short timeout
and then read the full log) before assuming it's still running. A stale
"still running" update with a wrong timer is misleading.

```python
# Check process exit status before assuming still running
# Use a short poll first, then check log
import time
poll_start = time.monotonic()
# ... after some polling ...
elapsed = time.monotonic() - poll_start
if elapsed > 30:  # If we've been waiting more than the expected run time
    # Check if process actually exited
    result = process(action=log, sessionId=SESSION)
    if "complete" in result or "exited" in result:
        finished
```

## GitHub Report Publishing

After completing an analysis, **always save the full report to GitHub**:

```bash
python3 /data/.openclaw/shared-skills/scripts/push_trading_report.py <TICKER> <report.md>
```

Reports are pushed to `darinyu/deep-research-reports/trading/<TICKER>/<date>/report.md`.

**Complete workflow:**
1. Acknowledge the request and share the timeline
2. Start the analysis (via `analyze_stock` MCP tool or direct Python exec)
3. Send intermittent status updates while it runs
4. Once done, parse the state log from `/data/.tradingagents/logs/<TICKER>/`
5. Build a clean Markdown report with all agent findings

   **⚠️ Report builder gotcha:** Several state fields are **dicts**, not strings:
   - `risk_debate_state` and `investment_debate_state` are dicts with `judge_decision`, `history`, etc.
   - `str(risk_debate_state)` dumps raw Python dict syntax (`{'judge_decision': '...'}`)
   - Always use `.get('judge_decision', '')` or `.get('summary', '')` for dict-type fields
   - `fundamentals_report`, `market_report`, `sentiment_report`, `news_report` are **strings**
   - Scan the final report for `{'` characters before pushing — they indicate a raw dict dump

   **📎 Report quality: include resource links for every data point**
   Every number in the report MUST be backed by a source link. Before writing the report:
   1. Search the web for each key data point (revenue, earnings, margins, platform assets, P/E ratio, analyst targets, price targets, etc.)
   2. Find the **specific source URL** (Yahoo Finance, Seeking Alpha, company earnings release, SEC filing)
   3. Include the source link inline next to each data point using standard markdown: `[Source](url)`
   4. If a number comes from the company's earnings release, link both the announcement and the specific data on Yahoo/WSJ
   5. For technical indicators (SMA, RSI, MACD), link the chart or data source (TradingView, Yahoo Finance)
   6. For analyst ratings/price targets, link the source (TipRanks, Benzinga, etc.)
   7. **No unsourced numbers** — every metric, percentage, or dollar figure in the report must have a citation

6. Push to GitHub
7. Share the GitHub link + executive summary in the final update

## Cost Estimates (DeepSeek Chat)

| Depth   | Est. Tokens | Est. Cost | Time      |
|---------|-------------|-----------|-----------|
| `deep`  | ~210K       | ~$0.06    | 8-15 min  |
| `quick` | ~110K       | ~$0.03    | 3-5 min   |

Costs are higher with GPT-5.x (~20-30x), comparable with Gemini.

## When to Use This

**Use when** the user asks to:
- "Analyze AAPL" / "What do you think about MSFT stock?"
- "Run a trading analysis on TSLA"
- "Should I buy/sell/hold GOOGL?"
- "Get the multi-agent trading opinion on SPY"
- "Deep dive on NVDA"

**Do NOT use** when:
- Asking for real-time price quotes — this does fundamental/sentiment research
- Asking about general market news (not ticker-specific)
- The user wants simple technical indicators (RSI, MACD) without the full pipeline

## Quickstart (first-time setup)

```bash
# 1. Install TradingAgents + dependencies (one-time, creates venv)
bash /data/.openclaw/shared-skills/scripts/trading_agent_mcp.sh install

# 2. Start the MCP server daemon
bash /data/.openclaw/shared-skills/scripts/trading_agent_mcp.sh start

# 3. Check it's running
bash /data/.openclaw/shared-skills/scripts/trading_agent_mcp.sh status
```

## Server Management

The MCP server runs as a daemon with auto-respawn. These commands work
standalone (no LLM needed, no OpenClaw needed):

```bash
trading-agent-mcp status   # Check if running
trading-agent-mcp restart  # Restart
trading-agent-mcp health   # Deep health check
trading-agent-mcp logs -f  # Follow logs
```

## Configuration

Configure via environment variables before starting the server:

| Variable                      | Purpose                          | Example                |
|-------------------------------|----------------------------------|------------------------|
| `DEEPSEEK_API_KEY`            | DeepSeek API key (recommended)   | `sk-...`               |
| `TRADINGAGENTS_LLM_PROVIDER`  | LLM provider to use              | `deepseek`             |
| `OPENAI_API_KEY`              | OpenAI API key                   | `sk-...`               |
| `ANTHROPIC_API_KEY`           | Anthropic API key                | `sk-ant-...`           |
| `GOOGLE_API_KEY`              | Google AI API key                | `AIza...`              |
| `XAI_API_KEY`                 | xAI/Grok API key                 | `xai-...`              |
| `ALPHA_VANTAGE_API_KEY`       | Data provider (for fundamentals) | `...`                  |

The default is DeepSeek (cost-effective). To customize:

```bash
export TRADINGAGENTS_LLM_PROVIDER=deepseek
export TRADINGAGENTS_DEEP_THINK_LLM="deepseek-chat"
export TRADINGAGENTS_QUICK_THINK_LLM="deepseek-chat"
export DEEPSEEK_API_KEY="sk-..."
bash trading_agent_mcp.sh restart
```

## Troubleshooting

**"No module named 'mcp'"** → Run `install` to set up the venv.

**"Server not responding"** → Run `restart` to respawn the daemon.

**"MCP tool not found by the agent"** → The server must be running before
the agent session starts (MCP tools are discovered at agent init). If you
start the server mid-session, the agent won't see it until restart.

**"API key not set"** → Check `health` output, set the env var, and `restart`.
