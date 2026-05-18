#!/usr/bin/env python3
"""
Stock Analysis Pipeline — runs TradingAgents, outputs progress to stdout,
formats the report, pushes to GitHub, prints final result as JSON.

Usage: python3 stock_analysis.py <TICKER> [quick|deep]

Progress lines (prefixed with PROGRESS:):
  PROGRESS:starting  Starting analysis for TICKER
  PROGRESS:running   Agents are gathering data...
  PROGRESS:analysts  Analysts completed their reports...
  PROGRESS:debate    Debate round N/3 in progress...
  PROGRESS:risk      Risk assessment in progress...
  PROGRESS:done      Analysis complete in Xs

Final output (JSON, one line):
  {"ticker": "...", "github_url": "...", "elapsed_seconds": N, "slack_text": "...", "status": "ok"|"error"}
"""

import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path


# ── Auto-detect venv python ──────────────────────────────────────────────
# If running with system python, re-exec with venv python for TradingAgents
_venv_candidates = [
    "/data/.tradingagents/venv/bin/python3",
    os.path.expanduser("~/.tradingagents/venv/bin/python3"),
]
for _vp in _venv_candidates:
    if os.path.exists(_vp) and sys.executable != _vp:
        # Re-exec self using venv python
        os.execv(_vp, [_vp] + sys.argv)


def progress(phase: str, msg: str):
    """Emit a progress line that the parent session can parse."""
    line = json.dumps({"type": "progress", "phase": phase, "message": msg})
    print(line, flush=True)


def slack_text(text: str) -> str:
    """Format markdown text for Slack: no italic, bold via *single*.

    Converts:
    - **bold** -> *bold*  (standard MD bold to Slack bold)
    - _italic_ -> *bold*  (never italic on Slack — convert to bold)
    - *italic* -> *bold*  (single-asterisk italic to bold)
    """
    import re

    # Step 1: Convert **bold** to *bold*
    text = text.replace("**", "*")

    # Step 2: Convert _italic_ to *bold*
    # Match _text_ where text doesn't contain spaces that could break
    # Use a simple approach: replace paired underscores that wrap text
    # Doing multiple passes to handle nested cases
    for _ in range(3):
        # Match _text_ where text is short (no internal underscores)
        text = re.sub(r'_(?=[^_\s])([^_]+?)(?<=[^_\s])_', r'*\1*', text)

    # Step 3: Convert *italic* (single asterisk, not part of **) to *bold*
    # Already processed by step 1, but catch remaining single-asterisk pairs
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'*\1*', text)

    return text


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "Usage: stock_analysis.py <TICKER> [quick|deep]"}))
        sys.exit(1)

    ticker = sys.argv[1].strip().upper()
    depth = sys.argv[2].strip().lower() if len(sys.argv) > 2 else "deep"
    is_quick = depth != "deep"
    rounds = 1 if is_quick else 3

    progress("starting", f"Starting analysis for {ticker} (depth: {depth})")

    # ── Import TradingAgents ──────────────────────────────────────────────
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG, _apply_env_overrides
    except ImportError as e:
        progress("error", f"TradingAgents not importable: {e}")
        result = {"status": "error", "error": f"TradingAgents not importable: {e}"}
        print(json.dumps(result))
        return

    progress("running", f"Agents are gathering data for {ticker}...")

    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = rounds
    config["max_risk_discuss_rounds"] = rounds
    _apply_env_overrides(config)

    ta = TradingAgentsGraph(debug=False, config=config)

    progress("analysts", f"Analysts are researching {ticker}...")

    start = time.monotonic()
    try:
        # This blocks for 3-15 minutes
        decision, state = ta.propagate(company_name=ticker, trade_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        elapsed = time.monotonic() - start

        progress("done", f"Analysis complete in {elapsed:.1f}s")

    except Exception as exc:
        elapsed = time.monotonic() - start
        tb = traceback.format_exc()
        progress("error", f"Analysis failed after {elapsed:.1f}s: {exc}")
        result = {
            "status": "error",
            "ticker": ticker,
            "error": str(exc),
            "elapsed_seconds": round(elapsed, 1),
        }
        print(json.dumps(result))
        return

    # ── Build report ──────────────────────────────────────────────────────
    state_dict = state if isinstance(state, dict) else {}

    lines = []
    lines.append(f"# {ticker} — TradingAgents Multi-Agent Analysis")
    lines.append("")
    lines.append(f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append(f"**Depth:** {depth}")
    lines.append(f"**Elapsed:** {elapsed:.1f}s")
    lines.append("")

    decision_str = str(decision) if decision else "N/A"
    lines.append(f"## Trading Decision")
    lines.append("")
    lines.append(decision_str)
    lines.append("")

    # Grab key state fields, avoiding raw dict dumps
    for key in ("final_decision", "reasoning", "risk_assessment", "portfolio_decision"):
        val = state_dict.get(key)
        if val and str(val).strip() and str(val) != "None":
            # Clean up raw Python dict syntax
            raw = str(val)
            if raw.startswith("{'") or raw.startswith('{"'):
                try:
                    parsed = json.loads(raw.replace("'", '"'))
                    raw = json.dumps(parsed, indent=2)
                except (json.JSONDecodeError, ValueError):
                    try:
                        parsed = eval(raw)
                        if isinstance(parsed, dict):
                            raw = json.dumps(parsed, indent=2)
                    except:
                        pass
            label = key.replace("_", " ").title()
            if label == "Final Decision":
                continue  # Already covered above
            lines.append(f"## {label}")
            lines.append("")
            lines.append(raw)
            lines.append("")

    # Agent reports from state
    for prefix in ("analyst_", "researcher_", "trader_", "risk_"):
        for key, val in state_dict.items():
            if not key.startswith(prefix):
                continue
            raw = str(val) if val else ""
            if not raw.strip() or raw == "None":
                continue
            label = key.replace("_", " ").title()
            lines.append(f"## {label}")
            lines.append("")
            lines.append(raw)
            lines.append("")

    lines.append("---")
    lines.append(f"*Generated by DDDD TradingAgents pipeline*")

    report_text = "\n".join(lines)
    report_file = f"/tmp/{ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    Path(report_file).write_text(report_text)

    # ── Push to GitHub ────────────────────────────────────────────────────
    github_url = ""
    push_script = "/data/.openclaw/shared-skills/scripts/push_trading_report.py"
    if os.path.exists(push_script):
        import subprocess
        result_sub = subprocess.run(
            ["python3", push_script, ticker, report_file],
            capture_output=True, text=True, timeout=30
        )
        if result_sub.returncode == 0:
            # Extract URL from push script output
            for line in result_sub.stdout.split("\n"):
                if "GitHub:" in line:
                    github_url = line.split("GitHub:")[-1].strip()
                    break
            if not github_url:
                github_url = f"https://github.com/darinyu/deep-research-reports/blob/main/trading/{ticker}/{datetime.now().strftime('%Y-%m-%d')}/report.md"
            progress("github", f"Report pushed: {github_url}")
        else:
            progress("warning", f"GitHub push failed: {result_sub.stderr.strip()}")

    # ── Generate Slack text ───────────────────────────────────────────────
    slack_text_out = slack_text(report_text)

    # Truncate if too long (Slack has ~40K char limit)
    if len(slack_text_out) > 35000:
        slack_text_out = slack_text_out[:35000] + "\n\n*[Report truncated — see GitHub for full version]*"

    result = {
        "status": "ok",
        "ticker": ticker,
        "elapsed_seconds": round(elapsed, 1),
        "github_url": github_url,
        "slack_text": slack_text_out,
        "report_file": report_file,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
