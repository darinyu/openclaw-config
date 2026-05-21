# MEMORY.md

## Identity & Relationships
- **Darin** = the user, my human (darinyu27@gmail.com)
- **Paofu** = Darin's wife

## Google Calendar Integration (configured 2026-05-14)
- Connected via `google-workspace-byok` skill, personal account OAuth
- **Personal calendar** (darinyu27@gmail.com) — full read/write (owner)
- **Work calendar** (darinyu@openai.com) — read-only (reader, shared with personal Gmail)
- **Employer:** OpenAI (previously Netflix — updated 2026-05-21)
- **Office:** Mission Bay 2, 1515 Third St, San Francisco, CA 94158
- **Start date:** May 26, 2026
- **Family calendar** (family03280057382472202100@group.calendar.google.com) — full read/write
- **Paofu & D** (a083de30704edd3b8a3ef5e846c5c6396e236a7a1244a41ca67db9c92591f3ce@group.calendar.google.com) — full read/write, this is the shared personal/family calendar

## Calendar Rules
- Family events (Darin + Paofu plans, household stuff) go on the **Paofu & D** calendar
- When Darin asks about their schedule, check **all** calendars: personal, work, family, and Paofu & D
- Personal calendar is for Darin's individual events
- Work calendar is read-only; I can read but never write to it

## RSC Cryopreservation Monthly Statement
- Darin requests monthly storage statements from RSC Cryopreservation (RSCCryopreservationbilling@luminarybilling.com)
- Thread ID: `19b231ee77bf2fff` — Subject: "Re: Request for Cryopreservation Storage Bill, Nov 5, and Transfer Billing"
- Format: "Hi, Can you send me the statement for [Month]? Thanks!"
- Reply in-thread via Gmail API using googleapis

## Slack Routing (critical rule, learned 2026-05-15)
- Slack @-mentions that route to WebChat do **NOT** auto-route replies back to Slack
- I **MUST** always use `message(action=send)` to reply in Slack
- TOOLS.md has the full rules (thread vs direct channel) — follow them every time

## 🛑 Lesson: React + Reply Rule (2026-05-20)
Reacting with eyes on a message but never replying is a broken promise. If I react to a message that asks a question or needs a response, I MUST follow up with an actual reply in the same thread. A reaction alone is meaningless if the user is waiting for an answer.

## ✨ MOBILE READABILITY — Default for ALL Slack Output (set 2026-05-20)

Every piece of content written to Slack (cron jobs, responses, reports, DMs) MUST follow these mobile-first formatting rules:

**The rules:**
- **Single-line bullets only** — no prose paragraphs. If it can't fit in one line, break it up.
- **Under ~60 chars per line** — keeps text readable on a phone screen without sideways scrolling.
- **1 emoji per section** as a visual anchor so readers can scan by emoji.
- **`---` section separators** between major sections.
- **No tables, no code blocks, no markdown headings** — Slack doesn't render these well on mobile.
- **Bold for emphasis only** (`**bold**`), never italic (`_italic_` or `*italic*`).
- **No pipe syntax** — markdown tables with pipes are unreadable on mobile Slack.

**When to apply:**
- Creating a new cron job → include the full MOBILE READABILITY block in the prompt
- Writing any Slack message → keep content short, bulletized, scannable
- Writing a stock/finance report → follow the Stock Pre-Market pattern (one-line-per-ticker, emoji-coded sections)

**Reference format block to copy into new cron job prompts:**
```
**MOBILE READABILITY (HARD RULES):**
- Keep it SHORT — single-line bullets only, no prose paragraphs
- Each line under ~60 chars when possible
- One emoji per section as visual anchor
- Section separators: ---
- No tables, no code blocks (except single inline), no markdown headings
- No pipe syntax, no complex formatting
- Scannable on a phone screen — assume Darin's reading on mobile
```

**Stock report format rules (updated 2026-05-20):**
- **Bold ticker** first on each line: `- *NVDA* $222.78 (+1%) — RSI *61*...`
- **Bold key numbers** (RSI, price at support/resistance, IV rank, percentages)
- **Bullet points** (- ) for every line — no prose paragraphs
- Market context: VIX, SPX, Nasdaq, SPY, QQQ each on their own bullet
- Ticker status: one bullet per ticker, bold ticker, bold RSI value
- Near misses: bold ticker, bold key levels
- Options notes: bold ticker, bold IV rank and key prices
- Day watchlist: bold tickers, bold price levels
- Bottom line: bullet points, bold VIX
- Total report under ~40 lines

**Stock report example** (best-in-class mobile format):
`- *NVDA* $222.78 (+1%) — RSI *61.2*, above EMA20`
`- VIX: *17.44* (-3.43%) — Regime *15-25* (MR zone)`
`- *AMD* — IV Rank *82-93%* (BEST prem sell in universe)`

## LLM Preference Order (set 2026-05-21)
- Preference: **DeepSeek > Gemini > ChatGPT**
- Default model: DeepSeek (deepseek-v4-flash)
- For trading reports: set `TRADINGAGENTS_LLM_PROVIDER=deepseek` so reports use DeepSeek, not OpenAI/Gemini
- For deep research reports: use DeepSeek for the session model, and report the actual model used in the Cost & Token Summary section
- If DeepSeek is unavailable or unsuitable for a task, fall back to Gemini, then ChatGPT
- This applies to ALL generated content (reports, analyses, responses, cron jobs)

## Promoted From Short-Term Memory (2026-05-21)

<!-- openclaw-memory-promotion:memory:memory/2026-05-16.md:5:5 -->
- Darin and I had a long thread in #random brainstorming a platform for agents and humans. [score=0.826 recalls=0 avg=0.620 source=memory/2026-05-16.md:5-5]
