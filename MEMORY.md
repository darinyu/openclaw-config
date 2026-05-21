# MEMORY.md

## Identity & Relationships
- **Darin** = the user, my human (darinyu27@gmail.com)
- **Paofu** = Darin's wife

## Google Calendar Integration (configured 2026-05-14)
- Connected via `google-workspace-byok` skill, personal account OAuth
- **Personal calendar** (darinyu27@gmail.com) — full read/write (owner)
- **Work calendar** (zyu@netflix.com) — read-only (reader, shared with personal Gmail)
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

**Stock report example** (best-in-class mobile format):
- Each bullet: `*TICKER* key stat — brief note (under ~60 chars)`
- VIX: `VIX: *22.5* (mean reversion)`
- Index perf: `SPY *+0.8%* DJI *-0.2%*`
- Total report under ~25 lines
