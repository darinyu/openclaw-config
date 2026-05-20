# Strategy Catalog — Stock Strategy Monitor

## Risk Tolerance Mapping (Darin: Moderate)
- Conservative: Risk 1-3
- **Moderate: Risk 1-6 ← Darin's level**
- Aggressive: Risk 7-8
- Speculative: Risk 9-10

## Strategy #1: RSI Mean Reversion (Risk: 4)

**Best Strategy For:** NVDA, AMZN, TSM, CRM, NET, CRWV, NBIS, MRVL, APP, QQQ, XLK, SOXX, AAPL, AVGO (ranked #1 or est. best on 17 of 23 symbols)

**Entry Signal:** RSI(14) < 30 (oversold)
**Exit Signal:** RSI(14) > 60 (recovered)
**Alternative Entry (wider):** RSI(14) < 35 (more signals, higher frequency)
**Alternative Exit:** RSI(14) > 50 or price returns above 20-SMA

**Filters:**
- Volume > 20-day average
- Price > 200-day MA (bull market filter)
- VIX < 35 (avoid crisis volatility)

**Key Backtest Results (2yr daily):**
| Symbol | Return | Win Rate | Sharpe | Max DD | WFA Verdict |
|--------|--------|----------|--------|--------|-------------|
| NVDA   | +136%  | 100%     | 29.09  | 0.0%   | **Moderate (0.5)** |
| AVGO   | +52%   | 80%      | 13.96  | -2.7%  | **Moderate (0.75)** |
| AAPL   | +27%   | 87.5%    | 9.14   | -8.9%  | Overfitted (0.0) |
| CRWV   | —      | —        | —      | —      | New IPO (est RSI MR) |
| NBIS   | —      | —        | —      | —      | New listing (est RSI MR) |
| MRVL   | —      | —        | —      | —      | New addition (est RSI MR) |
| APP    | —      | —        | —      | —      | New addition (est RSI MR) |
| TSM    | +63%   | 83.3%    | 17.61  | -6.8%  | — |
| AMZN   | +19%   | 66.7%    | 9.13   | -4.0%  | — |
| CRM    | +23%   | 83.3%    | 6.88   | -12.5% | — |
| NET    | +125%  | 100%     | 17.97  | 0.0%   | — |
| QQQ    | +17%   | 83.3%    | 9.70   | -5.1%  | — |
| SMH    | +19%   | 75.0%    | 8.91   | -5.6%  | — |
| XLK    | +19%   | 83.3%    | 10.71  | -5.5%  | — |
| SOXX   | +52%   | 83.3%    | 18.14  | -0.3%  | — |

**When to Use:** Pullbacks in bull market, after VIX spikes, earnings dip
**When to Avoid:** Strong momentum trends (let trend strategies handle), VIX > 40, gap-down > 3% overnight

## Strategy #2: Bollinger Band Mean Reversion (Risk: 3)

**Best Strategy For:** MSFT, SMH, SOXX, XLK, ASML, DDOG

**Entry Signal:** Price touches or crosses below lower Bollinger Band (20,2)
**Exit Signal:** Price returns to or crosses above middle band (20-SMA)

**Parameters:**
- BB Length: 20
- BB StdDev: 2.0
- Timeframe: Daily

**Key Backtest Results:**
| Symbol | Return | Win Rate | Sharpe | Max DD | Profit Factor |
|--------|--------|----------|--------|--------|-------------|
| AAPL   | +15%   | 77.8%    | 7.58   | -3.7%  | 3.33 |
| MSFT   | +12%   | 63.6%    | 4.06   | -7.1%  | 1.95 |
| QQQ    | +2.6%  | 57.1%    | 3.35   | -2.7%  | 1.70 |
| SMH    | +27%   | 77.8%    | 9.90   | -5.1%  | 4.56 |
| SOXX   | +48%   | 80.0%    | 15.30  | -3.6%  | 12.44 |
| XLK    | +15%   | 77.8%    | 10.61  | -2.5%  | 4.67 |
| ASML   | +29%   | —        | 7.64   | -10.6% | — |
| DDOG   | +64%   | —        | 9.46   | -16.2% | — |

**When to Use:** Range-bound markets, lower volatility periods, ETFs
**When to Avoid:** Strong trending markets (gives back gains), VIX < 12 (too calm)

## Strategy #3: EMA 20/50 Golden/Death Cross (Risk: 5)

**Best Strategy For:** GOOGL, TSM, NET, SNOW, SOXX

**Entry Signal:** EMA(20) crosses ABOVE EMA(50) — "Golden Cross"
**Exit Signal:** EMA(20) crosses BELOW EMA(50) — "Death Cross"

**Parameters:**
- Fast EMA: 20 periods
- Slow EMA: 50 periods
- Timeframe: Daily

**Key Backtest Results:**
| Symbol | Return | Win Rate | Sharpe | Trades | Notes |
|--------|--------|----------|--------|--------|-------|
| GOOGL  | +86%   | 100%     | 12.89  | 2      | Perfect in trending market |
| TSM    | +59%   | 66.7%    | 8.64   | 3      | Strong |
| NET    | +34%   | 100%     | —      | 1      | Few signals |
| SNOW   | +27%   | 66.7%    | 8.94   | 3      | Decent |
| SOXX   | +21%   | 25.0%    | 4.25   | 4      | Mixed |
| QQQ    | +14%   | 66.7%    | 7.15   | 3      | OK |

**Very few trades per year (2-5).** Works well in trending markets, poorly in range-bound.

**When to Use:** Clear uptrend/downtrend, after consolidation breakout, VIX < 15
**When to Avoid:** Choppy/range-bound markets (many false signals)

## Strategy #4: MACD Crossover (Risk: 5)

**Best Strategy For:** AMD, META, GOOGL, SMH

**Entry Signal:** MACD line crosses ABOVE signal line
**Exit Signal:** MACD line crosses BELOW signal line

**Parameters:**
- Fast Length: 12
- Slow Length: 26
- Signal Smoothing: 9
- Timeframe: Daily

**Key Backtest Results:**
| Symbol | Return | Win Rate | Sharpe | Max DD | Trades |
|--------|--------|----------|--------|--------|--------|
| AMD    | +131%  | 33.3%    | 4.09   | -35.3% | ~15-23 |
| META   | +31%   | 50.0%    | 3.60   | -15.5% | — |
| GOOGL  | +72%   | 52.4%    | 5.12   | -16.4% | — |
| SMH    | +24%   | 31.8%    | 2.14   | -34.8% | — |

**Note:** Many trades, lower win rate (30-40%), larger drawdowns. Suffers from whipsaws in choppy markets.

**When to Use:** Strong trending semis, after IV expansion
**When to Avoid:** Low-volatility, range-bound periods

## Strategy #5: Supertrend (Risk: 7) — ABOVE MODERATE THRESHOLD

**Best Strategy For:** AVGO, GOOGL, NET

**Entry:** Price closes above Supertrend line (long)
**Exit:** Price closes below Supertrend line
**Parameters:** ATR(10), Factor=3.0

**Walk-Forward Verdict: OVERFITTED on most symbols.** Only use on trending names with strict risk management.

**Not recommended for moderate risk tolerance.** Included for awareness only.

## Strategy #6: Covered Call / Buy-Write (Risk: 1-2)

**Only for ETF holdings:** QQQ, SMH, XLK, SOXX
**Expected Return:** 10-20% annualized premium
**Entry:** Sell call when IV rank > 50%
**Strike:** 2-5% OTM
**Expiration:** 30-day (monthly)

## Strategy #7: Cash-Secured Put (Risk: 2-3)

**Best for:** AAPL, MSFT, GOOGL, QQQ (lower vol names)
**Expected Return:** 8-15% annualized
**Entry:** Sell put when IV rank > 50%
**Strike:** ATM or slightly OTM
**Expiration:** 30-45 days

## VIX Regime Switching

VIX level determines which strategy class performs best:
- **VIX < 15:** Trend following (EMA Cross, MACD) — trending markets
- **VIX 15-25:** Mean reversion (RSI, Bollinger) — pullback/reversal
- **VIX > 25:** Mean reversion + tighter stops or reduce exposure
- **VIX > 40:** Skip new entries entirely — crisis mode

## Eligible Strategies for Moderate Risk (Darin)

| # | Strategy | Risk | Check During Heartbeat |
|---|----------|------|----------------------|
| 1 | RSI Mean Reversion | 4 | Yes — check RSI(14) < 30/35 |
| 2 | Bollinger Band M.R. | 3 | Yes — check price vs lower BB |
| 3 | EMA 20/50 Cross | 5 | Yes — check cross status |
| 4 | MACD Cross | 5 | Yes — check cross status |
| 5 | Covered Call | 1-2 | Advisory — check IV rank for ETFs |
| 6 | Cash-Secured Put | 2-3 | Advisory — check IV rank for quality names |
| 7 | Supertrend | 7 | No — above moderate threshold |
| 8 | Pair Trading | 7 | No — above moderate threshold |
| 9 | Short-dated Options | 10 | Never — speculative |
| 10 | Earnings Straddle | 9 | Never — speculative |
