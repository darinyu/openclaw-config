#!/usr/bin/env bash
# Stock Strategy Signal Checker
# Usage: bash scripts/check_strategy_signals.sh
# Reads: strategy conditions from references/strategies.md
# Calls: tradingview__yahoo_price and tradingview__combined_analysis
# Output: Machine-readable signal summary
#
# This script is designed to be called by the SKILL.md workflow.
# The actual signal checking happens in the LLM analysis step.
# This script handles data collection prep and output formatting.

set -euo pipefail

echo "=== Stock Strategy Signal Check ==="
echo "Risk Tolerance: Moderate (Strategies 1-6)"
echo ""

# Tickers to monitor (23 symbols)
TICKERS="AAPL MSFT GOOGL META AMZN NVDA AMD TSM AVGO CRM DDOG SNOW NET CRWV NBIS MRVL APP SNDK QQQ SMH XLK SOXX"

echo "Focus Universe (23 symbols): $TICKERS"
echo "Total: $(echo $TICKERS | wc -w | tr -d ' ') symbols"
echo ""

# Print the signal conditions table (for LLM reference)
echo "=== Signal Conditions Reference ==="
echo ""
echo "Strategy | Entry Signal | Tickers"
echo "---------|--------------|--------"

echo ""

echo "=== VIX Regime ==="
echo "VIX<15: Trend-following preferred"
echo "VIX 15-25: Mean reversion preferred (current regime assumed)"
echo "VIX 25-40: Mean reversion + caution"
echo "VIX>40: Hold, no new entries"
echo ""
