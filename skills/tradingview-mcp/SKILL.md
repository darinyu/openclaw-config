---
name: tradingview-mcp
description: AI Trading Intelligence — live prices, 30+ technical indicators, backtesting (6 strategies), walk-forward overfitting detection, Reddit sentiment, news, market screening (top gainers/losers, Bollinger squeezes, volume breakouts, candlestick patterns), and multi-timeframe analysis. Supports US stocks, crypto, ETFs, indices, forex, Turkish (BIST), and Egyptian (EGX) markets.
metadata: { "openclaw": { "emoji": "📈", "always": true, "homepage": "https://github.com/atilaahmettaner/tradingview-mcp" } }
---

# TradingView MCP — AI Trading Intelligence

You have access to a full trading intelligence toolkit via MCP tools (preferred) and a bash wrapper fallback.

**MCP tools available:** `backtest_strategy`, `compare_strategies`, `walk_forward_backtest_strategy`, `yahoo_price`, `market_snapshot`, `get_technical_analysis`, `get_candlestick_patterns`, `get_multi_timeframe_analysis`, `market_sentiment`, `financial_news`, `combined_analysis`, `screen_stocks`, `scan_by_signal`, `top_gainers`, `top_losers`, `bollinger_scan`, `coin_analysis`, `multi_agent_analysis`, `volume_breakout_scanner`, and more.

**Bash fallback:** `python3 /data/.openclaw/tools/trading.py <command> [args]`

## Behavior Guidelines

1. **Run immediately** — for any trading/market question, execute tools directly. Don't ask for clarification on defaults.
2. **Combine signals** — for "should I buy X?" run price + technical analysis + sentiment together.
3. **Default timeframe** is `1D` for technicals, `1y` for backtests, unless specified.
4. **Explain metrics** — Sharpe (risk-adjusted return), Win Rate, Max Drawdown, Profit Factor.
5. **Add disclaimer** — on all backtests: "⚠️ Past performance does not guarantee future results."
6. **Be concise** — use bold for key numbers, bullet lists, no raw JSON in replies.

## Tool Quick Reference

### Prices & Market Overview
| Intent | Tool |
|--------|------|
| "AAPL price?" | MCP: `yahoo_price(symbol="AAPL")` / Bash: `price AAPL` |
| "Show me BTC, ETH, SOL" | MCP: `yahoo_price(symbol="BTC-USD")` (run multiple) / Bash: `price BTC-USD` |
| "How are markets today?" | MCP: `market_snapshot()` / Bash: `snapshot` |

### Technical Analysis
| Intent | Tool |
|--------|------|
| "Analyze AAPL technically" | MCP: `get_technical_analysis(symbol="AAPL", exchange="NASDAQ", interval="1h")` / Bash: `technical AAPL NASDAQ 1h` |
| "Candlestick patterns for BTC?" | MCP: `get_candlestick_patterns(symbol="BTC-USD", exchange="BINANCE")` / Bash: `candlestick BTC-USD BINANCE` |
| "Multi-timeframe view of NVDA" | MCP: `get_multi_timeframe_analysis(symbol="NVDA", exchange="NASDAQ")` / Bash: `multi_timeframe NVDA NASDAQ` |

### Backtesting
| Intent | Tool |
|--------|------|
| "Backtest RSI strategy 1 year" | MCP: `backtest_strategy(symbol="AAPL", strategy="rsi", period="1y")` / Bash: `backtest AAPL rsi 1y` |
| "Which strategy is best for BTC?" | MCP: `compare_strategies(symbol="BTC-USD", period="2y")` / Bash: `compare BTC-USD 2y` |
| "Is this strategy overfitted?" | MCP: `walk_forward_backtest_strategy(symbol="AAPL", strategy="rsi", period="2y")` / Bash: `walkforward AAPL rsi 2y` |

### Sentiment & News
| Intent | Tool |
|--------|------|
| "What's Reddit saying about NVDA?" | MCP: `market_sentiment(symbol="NVDA")` / Bash: `sentiment NVDA stock` |
| "Latest news on AAPL" | MCP: `financial_news(symbol="AAPL")` / Bash: `news AAPL` |
| "Full picture on TSLA" | MCP: `combined_analysis(symbol="TSLA", exchange="NASDAQ")` / Bash: `combined TSLA NASDAQ` |

### Screening & Market Scanning
| Intent | Tool |
|--------|------|
| "Today's top gainers on NASDAQ" | MCP: `top_gainers(exchange="NASDAQ", timeframe="1D")` / Bash: `top_gainers NASDAQ 1D` |
| "Top losers on Binance" | MCP: `top_losers(exchange="BINANCE", timeframe="4h")` / Bash: `top_losers BINANCE 4h` |
| "Bollinger squeeze on NYSE" | MCP: `bollinger_scan(exchange="NYSE", timeframe="1D")` / Bash: `bollinger_scan NYSE 1D` |
| "Find oversold stocks on NASDAQ" | MCP: `scan_by_signal(exchange="NASDAQ", signal_type="oversold")` / Bash: `screener NASDAQ oversold` |

## Supported Symbols

- **US Stocks:** AAPL, TSLA, NVDA, MSFT, GOOGL, META, AMZN
- **Crypto:** BTC-USD, ETH-USD, SOL-USD, BNB-USD, XRP-USD
- **ETFs:** SPY, QQQ, GLD, VTI, IWM
- **Indices:** ^GSPC (S&P500), ^IXIC (NASDAQ), ^DJI (Dow), ^VIX
- **FX:** EURUSD=X, GBPUSD=X, JPYUSD=X

## Backtesting Strategies

| Strategy | Key | Best For |
|----------|-----|----------|
| RSI Mean Reversion | `rsi` | Ranging/sideways markets |
| Bollinger Band | `bollinger` | Mean reversion in volatile markets |
| MACD Crossover | `macd` | Trend following |
| EMA 20/50 Cross | `ema_cross` | Medium-term trends |
| Supertrend (ATR) | `supertrend` | Strong trending markets |
| Donchian Channel | `donchian` | Breakout / Turtle Trading |

**Institutional metrics:** Win Rate, Total Return, Sharpe Ratio, Calmar Ratio, Max Drawdown, Profit Factor, Expectancy, Best/Worst Trade, vs Buy-and-Hold. Includes realistic commission + slippage simulation.

## Example Response Formats

### Price Query
```
📊 AAPL — Apple Inc.
💵 Price: $189.42
📈 Change: +1.23%
📅 52w High: $199.62 | Low: $164.08
🏦 Exchange: NASDAQ | Market: REGULAR
```

### Backtest Summary
```
🔬 AAPL — RSI Strategy (1Y daily)
────────────────────────────────
📊 Trades: 8 | Win Rate: 62.5%
💰 Return: +14.3% vs B&H: +21.2%
📉 Max Drawdown: -6.8%
⚡ Sharpe: 1.42 | Calmar: 2.10
🏆 Profit Factor: 2.31

⚠️ Past performance does not guarantee future results.
```

### Technical Analysis
```
📈 AAPL Technical Analysis (1D)
─────────────────────────────────
🟢 RSI(14): 54.2 — NEUTRAL
🟢 MACD: 1.24 — BULLISH
🟡 BB(20,2): Upper $195 | Mid $188 | Lower $181
🟢 EMA 20/50: Golden cross intact
🟢 ADX(14): 25.3 — TRENDING
📊 Signal: STRONG BUY (8/13 bullish)
```
