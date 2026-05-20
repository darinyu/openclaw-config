---
name: stock-strategy-monitor
description: >
  Monitor focus universe stocks for trading strategy entry signals based on
  backtested quantitative strategies. Use during heartbeats and weekday
  pre-market cron to check RSI Mean Reversion, Bollinger Band Mean Reversion,
  EMA Cross, MACD Cross signals for 23 symbols. Also flags sell call/put
  premium selling opportunities when IV rank is elevated. Alerts Darin when
  tickers satisfy strategy entry conditions. Records personal risk tolerance
  (moderate, strategies 1-6). Trigger keywords: check signals, strategy
  monitor, stock alerts, signal scan, trading signals, strategy check, 信号检查,
  策略监控.
---

# Stock Strategy Monitor

## Darin's Profile
- **Risk Tolerance:** Moderate (strategies with Risk 1-6 eligible)
- **Focus Universe:** 23 symbols (tech, semi, cloud, infra, ETFs)
- **Role:** Advisory only — never place trades, only alert
- **Delivery:** Report to Slack (stock channel or DM)

## When to Use
- During **heartbeat** checks (check for signals)
- During **pre-market cron** (6:00 AM PT weekday — deliver full analysis)
- When Darin asks "check signals" or "any entries today"

## Workflow

### 1. Load Strategy Data
Read `references/strategies.md` for full strategy catalog with signal conditions.
Read `references/ticker-profiles.md` for per-ticker best strategies.

### 2. Collect Market Data
Use TradingView MCP tools to fetch current data:

**Required calls:**
- `tradingview__market_snapshot()` — overall market context
- `tradingview__yahoo_price("SPY")` for VIX proxy or check VIX directly
- `tradingview__yahoo_price` for each ticker in the focus universe

**For depth (during pre-market cron):**
- `tradingview__combined_analysis` for NVDA, QQQ, SPY (gets RSI, BB, MACD, sentiment in one call)
- `tradingview__financial_news` for breaking news

### 3. Check Signal Conditions

For each ticker, evaluate its **best 1-2 strategies** against current market data:

**RSI Mean Reversion (Risk 4):**
- If ticker's best strategy is RSI MR AND RSI(14) < 30/35 → **SIGNAL: RSI Oversold Entry**
- Check VIX < 35, price > 200-MA as confirmation filters

**Bollinger Band Mean Reversion (Risk 3):**
- If ticker's best strategy is BB MR AND price near/at lower BB(20,2) → **SIGNAL: BB Lower Touch**
- Most reliable on ETFs (SMH, SOXX, XLK)

**EMA 20/50 Cross (Risk 5):**
- If ticker's best strategy is EMA Cross AND EMA(20) > EMA(50) trending up → **SIGNAL: Golden Cross Active**
- Alert when a NEW cross occurs (not just existing state)

**MACD Cross (Risk 5):**
- If ticker's best strategy is MACD AND MACD > Signal AND trending up → **SIGNAL: MACD Bullish Cross**
- Alert when a NEW cross occurs

**Options Advisory — Sell Call/Put (Risk 1-3):**
- If IV rank > 50% on ETF holdings → suggest covered calls
- If IV rank > 50% on quality names → suggest cash-secured puts
- Use `tradingview__coin_analysis` or check IV from option chain data
- Covered calls: sell 30-45 DTE, 2-5% OTM strike
- Cash-secured puts: sell 30-45 DTE, ATM or slightly OTM on quality names

### 4. VIX Regime Assessment
Check VIX level and determine regime:
- **< 15:** Trend-following favored (EMA, MACD strategies)
- **15-25:** Mean reversion favored (RSI, BB strategies) — default
- **25-40:** Mean reversion + caution — reduce position size
- **> 40:** New entries on hold

### 5. Rank Signals by Priority

1. **Red alert:** RSI entry on NVDA, AVGO, or NET (most robust strategies)
2. **Orange alert:** Bollinger touch on SMH, SOXX, XLK (high Sharpe, consistent)
3. **Yellow alert:** New EMA/MACD cross on GOOGL, TSM (large potential moves)
4. **Info:** Options opportunity (IV rank elevation)
5. **Note:** VIX regime shift

### 6. Format Report for Slack (Mobile-First)

Structure the report:
1. *Market Context* — VIX regime, major index performance (1-2 lines)
2. *Active Signals* — tickers with entry conditions met (sorted by priority)
3. *Near Misses* — tickers close to entry but not yet triggered
4. *Sell Call/Put Opportunities* — IV rank > 50% tickers with premium recs
5. *Day Watchlist* — what to look for

**Mobile readability rules (CRITICAL — Slack mobile is the primary viewing surface):**
- Keep each bullet line under ~60 chars where possible
- Ticker first on each line: `*NVDA* RSI 28 — oversold entry`
- No prose paragraphs — break into single-line bullets
- Emoji as visual anchor: :red_circle: active signal, :large_orange_diamond: near miss, :moneybag: options
- Each section = 1 line header separator (`---`) + bullets
- No embedded tables or code blocks (unreadable on mobile)
- VIX section: `VIX: *22.5* (mean reversion regime)` — one line
- Signal priority grouped:
  - Active signals first (most important)
  - Then near misses
  - Then options opportunities
  - Then watchlist

**Formatting rules (Slack mrkdwn):**
- Bold = *asterisks* (Slack format, NOT double asterisks)
- NEVER use _underscore_ or italic
- No markdown tables or headings
- Use bullet lists (- ) for all lists
- Concise, natural tone

### 7. Push to GitHub (Optional for long-term tracking)
When running the pre-market cron:
```
/data/.openclaw/shared-skills/scripts/push_trading_report.py <TICKER> <report_content>
```
Store daily signal check under `stock-signals/YYYY-MM-DD/`.

## Ticker-Strategy Quick Reference

## Ticker-Strategy Quick Reference (23 symbols)

**Tech Giants (5):**
- *NVDA* RSI MR (R4) RSI<30
- *AAPL* RSI MR (R4) RSI<30
- *MSFT* Bollinger MR (R3) Price<Lower BB
- *GOOGL* EMA Cross (R5) EMA20>EMA50
- *META* MACD Cross (R5) MACD>Signal

**Cloud/Infra (9):**
- *AMZN* RSI MR (R4) RSI<30
- *CRM* RSI MR (R4) RSI<30
- *DDOG* Bollinger MR (R3) Price<Lower BB
- *SNOW* EMA Cross (R5) EMA20>EMA50
- *NET* RSI MR (R4) RSI<30
- *CRWV* RSI MR (R4) RSI<30
- *NBIS* RSI MR (R4) RSI<30
- *MRVL* RSI MR (R4) RSI<30
- *APP* RSI MR (R4) RSI<30

**Semis (5):**
- *AVGO* RSI MR (R4) RSI<35
- *AMD* MACD Cross (R5) MACD>Signal
- *TSM* RSI MR (R4) RSI<30
- *ASML* Bollinger MR (R3) Price<Lower BB
- *SNDK* Bollinger MR (R3) Price<Lower BB

**ETFs (4):**
- *QQQ* RSI MR (R4) RSI<30 or IV>50%
- *SMH* Bollinger MR (R3) Price<Lower BB or IV>50%
- *XLK* RSI MR (R4) RSI<30 or IV>50%
- *SOXX* RSI MR (R4) RSI<30 or Price<Lower BB or IV>50%

## Fallback
## Sell Call/Put Opportunity Assessment
When IV rank is elevated on any focus ticker, flag it as a premium selling opportunity.

**Covered calls (best for ETF holdings):**
- QQQ, SMH, XLK, SOXX — liquid options, steady IV
- Sell monthly 2-5% OTM calls when IV>50%
- ~10-20% annualized premium potential

**Cash-secured puts (best for quality names):**
- AAPL, MSFT, GOOGL, QQQ — lower vol, stable names
- AVGO, MRVL, NVDA — higher IV = more premium
- Sell 30-45 DTE, ATM or slightly OTM
- ~8-15% annualized premium potential

**High-premium targets (IV consistently high):**
- AMD (IV rank 82-93% — highest in universe)
- NVDA (IV rank 65-76%)
- AVGO (IV rank ~65%)
- CRWV (new IPO, expect elevated IV)
- APP (high growth, expect elevated IV)

Include in report section *Sell Call/Put Opportunities* with ticker, IV estimate, and recommendation.

## Fallback
If TradingView MCP tools return errors, use `tradingview__yahoo_price` for prices and build the report from available data. Strategy signal checks require at minimum: current price, RSI (can estimate from recent price action), and VIX level.
