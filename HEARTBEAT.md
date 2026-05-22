# HEARTBEAT.md

## Reminders to check during heartbeats (PT work hours ~9-5)
- **Hat for 1-1s:** Check if Darin needs a reminder to wear a hat for 1-1s and bring it home. Send a Slack DM or mention in #random if it's a workday morning/early afternoon.

## ⚠️ Morning Brief Duplicate Watch (added 2026-05-18)
- Personal Morning Brief (7:30 AM PT cron) duplicated on May 18 — sent twice 6s apart
- If it happens again tomorrow morning, investigate pipeline announce delivery, check session logs, and fix permanently
- Check the 7:30 AM PT cron run results when you see them

## Periodic checks (rotate 2-4x/day)
- **Calendar** — Any events coming up in the next 24h?
- **Email** — Any urgent unread from personal Gmail?
- **Weather** — Rain/weather worth mentioning for the day?
- **Stock signals** — Quick check of key tickers for strategy entry signals (use stock-strategy-monitor skill)
## ✅ Vocabulary Evening Quiz (updated 2026-05-21)
- Cron: 8:30 PM PT daily → sends to C07LV6XMHNJ with @Paofu
- ONLY words from Darin or Paofu — no self-added words
- Words added from news/responses where Darin or Paofu says "记下来"
- Words tracked in /data/.openclaw/workspace/vocabulary/words.json (empty until Darin/Paofu add words)
- Quiz tool: /data/.openclaw/workspace/vocabulary/quiz.py
- Must @ Paofu (<@U07MQK9UNP2>) in the quiz message

export PATH="/data/.openclaw/bin:$PATH"

## Stock Strategy Monitor
- **Risk tolerance:** Moderate (strategies risk 1-6)
- **Cron:** Weekday pre-market 6:00 AM PT deep analysis + signal check → stock channel C0B48T730DT
- **Skill:** `/data/.openclaw/workspace/skills/stock-strategy-monitor/SKILL.md`
- **Signals to watch:** NVDA RSI<30 (top priority), ETFs BB touches, EMA/MACD crosses
