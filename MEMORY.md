# MEMORY.md

## Identity & Relationships
- **Darin** = the user, my human (darinyu27@gmail.com)
- **Paofu** = Darin's wife

## Paofu English Level & Annotation Guide (set 2026-05-21, updated 2026-05-22)
- Estimated B2+ (Upper-Intermediate)
- Can read AI/tech news overall but needs help with: idioms/collocations (breakneck speed), formal/academic vocab (constituency), phrasal verbs, compound concepts

### Annotation Rules (from Paofu's original request, pending her confirmation on format)
- **Format:** inline in the text — **word(中文翻译)** right where the word appears in the sentence
- **Judgment-based:** annotate SOME words she might not know, no minimum count per story
- **Prioritize:** phrasal verbs & fixed collocations > cultural metaphors & idioms without Chinese equivalent > formal/academic vocab
- **For idioms/metaphors:** first give literal meaning, then explain actual usage
- **DON'T annotate:** basic/common words, or metaphors with direct Chinese equivalents (泼冷水/泼冷水, 冰山一角/冰山一角)
- **Keep it readable** — don't annotate every word, only ones worth learning but hard to guess from context
- **PAOFU'S ASSESSMENT (2026-05-21):** She self-reports that metaphors with clear Chinese parallels are easy. The hard stuff is phrasal verbs (fell through), cultural references (Slop Grenade), and collocations where simple words combine unexpectedly.
- **⚠️ FORMAT NOT FINALIZED —** Need to test with Paofu and confirm she likes this format before making permanent

### Nightly Quiz (set 2026-05-21)
- **After posting:** automatically select annotated words, add them to vocab list (can edit/curate later)
- **Nightly quiz:** interactive, ask Paofu if she knows the word/idiom, then reveal answer
- **Ongoing assessment:** find opportunities to assess level and adjust difficulty

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

## Promoted From Short-Term Memory (2026-05-25)

<!-- openclaw-memory-promotion:memory:memory/2026-05-19.md:18:18 -->
- Scanned session transcripts, memory files, and Slack channels (#C0B4EK31NCU, DM, threads) for corrections from Darin. [score=0.856 recalls=0 avg=0.620 source=memory/2026-05-19.md:18-18]
<!-- openclaw-memory-promotion:memory:memory/2026-05-19.md:22:22 -->
- Darin's only interactions in the window: [score=0.856 recalls=0 avg=0.620 source=memory/2026-05-19.md:22-22]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:5:5 -->
- Scanned last 24h for corrections from Darin. Sessions list returned 0 results (no visible sessions), relied on memory files. [score=0.850 recalls=0 avg=0.620 source=memory/2026-05-18.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:9:9 -->
- **1. Stock Analysis Pipeline — Darin caught 3 bugs** [score=0.850 recalls=0 avg=0.620 source=memory/2026-05-18.md:9-9]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:14:14 -->
- **Fix verification: ALL VERIFIED ✅** [score=0.850 recalls=0 avg=0.620 source=memory/2026-05-18.md:14-14]
<!-- openclaw-memory-promotion:memory:memory/2026-05-18.md:1:40 -->
- # 2026-05-18 ## Correction Retrospective (cron, 11:00 UTC) Scanned last 24h for corrections from Darin. Sessions list returned 0 results (no visible sessions), relied on memory files. ### Corrections found from 2026-05-17 **1. Stock Analysis Pipeline — Darin caught 3 bugs** - Wrong thread (reports in their own thread, not reply under his message) - Italic in Slack output - No progress updates or GitHub push **Fix verification: ALL VERIFIED ✅** - `scripts/stock_analysis.py` exists with full TradingAgents pipeline + JSON progress + Slack formatting + GitHub push - TOOLS.md has full #stock Channel Rules protocol (threading, italic filter, progress updates) - `scripts/slack_format.sh` / `slack_formatter.py` exist and work - `shared-skills/scripts/push_trading_report.py` exists **2. Slack Routing (from 2026-05-15, reaffirmed)** - Darin called out replying in WebChat instead of Slack **Fix verification: ALL VERIFIED ✅** - TOOLS.md: "CRITICAL: Slack Replies Must Be Explicit" section - TOOLS.md: Channel Routing with thread rules - AGENTS.md: Standing Order for Slack reaction protocol **3. Auto-log every conversation (set by Darin 2026-05-17)** - Think.py logging required for every Slack conversation **Fix verification: ALL VERIFIED ✅** - AGENTS.md has full think.py integration rules with session_id format - `shared-skills/scripts/think.py` exists **4. Cron job output rules (set by Darin 2026-05-17)** - Pre-Send Checklist applies to all cron output - Bold only, zero italic - Always output (never silent NO_REPLY) - Fallback channel: C0B4EK31NCU [score=0.849 recalls=7 avg=0.385 source=memory/2026-05-18.md:1-40]
<!-- openclaw-memory-promotion:memory:memory/2026-05-19.md:15:15 -->
- Time window: 2026-05-18 15:07 UTC → 2026-05-19 15:07 UTC [score=0.846 recalls=0 avg=0.620 source=memory/2026-05-19.md:15-15]
