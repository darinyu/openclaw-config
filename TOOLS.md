---
summary: "Workspace template for TOOLS.md"
read_when:
  - Bootstrapping a workspace manually
---

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## MANDATORY: Pre-Send Checklist (GLOBAL — every Slack message)

**FAILING THIS CHECKLIST = BROKEN MESSAGE = ANGRY DARIN.**

Before ANY `message(action=send)` call to Slack, run through ALL THREE checks.

### ✅ Check 1: Thread Routing

Identify the SOURCE message that triggered this response:

| Source type | What to do |
|---|---|
| Direct @-mention of DDDD (standalone msg, no thread) | Reply in a **thread** under that message — use its `ts` as `threadId` |
| Reply in an existing thread (message has a `threadId`) | Reply in the **same thread** — use the parent `threadId` |
| General channel message (no tag, no thread) | Post directly to the channel (no threadId) |

**TO find the source message's ts:** Check the inbound context. The `reply_to_id` or `message_id` in the conversation info tells you what message to thread under. The triggering message's `ts` timestamp IS the threadId.

### ✅ Check 2: Zero Italic

**NEVER write `_underscore_` or `*asterisk italic*` in message text.** Period.

In Slack mrkdwn:
- `*bold*` = bold (single asterisks = Slack bold)
- `_italic_` = italic (this is what Darin hates)

Just write correct Slack mrkdwn from the start:
- Use `*bold*` for emphasis (NOT `**`, NOT `_`)
- Never use `_` for anything except code spans
- Never use single `*` around words you don't want bolded

### ✅ Check 3: Filter as Safety Net

After writing your message text to a file, run it through the italic filter:

1. Write message text to `/tmp/slack_msg.txt`
2. Run: `scripts/slack_format.sh < /tmp/slack_msg.txt` — read the output
3. If the output differs from your input, the filter caught italic — read carefully and use the filtered version
4. Use the FILTERED output as the `message` parameter

**The filter script:**
```
scripts/slack_format.sh
```
Wrapper around `scripts/slack_formatter.py` — converts BOTH `*italic*` and `_italic_` to `**bold**`. Test with: `python3 scripts/slack_formatter.py < /tmp/msg.txt`.

**SKIP REASONING:** Do not "but I didn't use italic" yourself out of this. The filter catches accidents. Run it.

### 🔴 Common Failures (learned the hard way)

| What I do | What Darin sees | Fix applied? |
|---|---|---|
| Write `_important_ thing` in message | *italic text* on Slack | ❌ — use `*important* thing` |
| Send message without `threadId` when replying to Darin | New standalone message in channel instead of thread | ❌ — always find and pass the source `ts` |
| Write directly in `message` param instead of file → filter → send | Italic slips through | ❌ — write to file first |

**Both failures here cost Darin time to call them out. Don't make him do that again.**

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## ⚠️ CRITICAL: Emoji First, Then Work (MANDATORY — do not skip)
When a Slack message routes here (any channel, any thread), the VERY FIRST tool call MUST be `message(action=react, emoji="👀")` on the inbound message. Not "I'll react soon" — actually do it immediately as the first action. No reading, no processing, no planning, no responding until the reaction is sent. Default to 👀. This is a hard standing order in AGENTS.md.

## ⚠️ CRITICAL: Slack Replies Must Be Explicit (always!)
> I keep failing at this. When a Slack message triggers work, the LAST thing I do MUST be `message(action=send)` — not a private reply here. Private replies don't reach Slack. Ever.
> **My final answer in this session is PRIVATE. To post to Slack, I MUST call the message tool.**
>
> This includes NO_REPLY decisions — in a thread context, a bare NO_REPLY won't thread correctly. Use `message(action=send)` with the proper `threadId` even for minimal replies.
>
> The `visibleReplies: message_tool` setting means ONLY explicit message tool sends show up in channels. Natural session responses are invisible.

## 🛑 Send Rule — Draft First, Confirm (set by Darin 2026-05-16)

Never send emails or any outbound messages directly. Always:
1. Draft the content
2. Present the draft to Darin for approval
3. Only send after he explicitly confirms

This applies to ALL outbound sends — email, Slack messages on his behalf, etc.

## 🔔 Drive Folder Watch Rule (set by Darin 2026-05-15)

- **Folder ID:** `1-I3xydVuGTGNMj5oH7mA5J_OGF1NxQFZ`
- **Rule:** Whenever reading from or modifying any document in this folder, send Darin a Slack DM (`U07MEG6NMED`).
- **Scope:** This covers the personal account (its Drive scope has read-only access).

## Channel Routing

**Slack → Control UI:**

When a Slack message routes to this session (webchat/Control UI), ALWAYS send the reply back to Slack using the `message` tool. Do not just reply here.

**RULE: Messages originating from Slack MUST be replied to in Slack.**

How to detect: if the session's delivery context has `channel: "slack"` or the message came with Slack @-mention formatting (e.g. `<@U...>`), the origin is Slack. Reply goes to Slack only — or Slack + Control UI if convenient.

**Thread rules for Slack replies (STRICT):**
- **Direct @-mention/tag** of DDDD → MUST reply in a **thread** under that message. Use the source message's `ts` timestamp as `threadId` in `message(action=send)`.
- **Thread reply** (message has a threadId/topic_id) → MUST reply in the **same thread**. Use the existing `threadId`/`topic_id` from the inbound context.
- **General channel message** (no tag, no thread) → post directly to the channel (no threadId).

**How to find the ts/threadId:** Check the inbound metadata JSON — it has `message_id` (= the Slack ts) and `reply_to_id` (= the parent message ts if this is a thread reply). Use these values.

This applies to `#random` and any other Slack channels that route here.

## #learning Posting Rules (set by Darin 2026-05-14)

When posting articles in the Slack channel **#learning**:
- **Summarize** each article — 2-4 sentence overview of what it's about and why it's worth reading
- **Section format** — separate articles with clear sections (title, summary, key takeaways)
- **Mind unfurls** — link previews create visual clutter, so keep blurbs tight and targeted. Don't let the wall of text make the previews harder to read

## HackerNews Rule

When Darin asks for top news on HackerNews:
- Fetch from the current front page
- Rank stories by *points* (highest first)
- Give trending stories — the ones with the most discussion/engagement right now
- Include: title, points, comment count, and link

## Web Search (set by Darin 2026-05-17)
- **Primary:** Use `liang-tavily-search` skill (`skills/liang-tavily-search/scripts/search.mjs`) with `TAVILY_API_KEY` env var
- **Fallback:** If Tavily returns no credits or errors, use the built-in `web_search` tool
- Example: `node skills/liang-tavily-search/scripts/search.mjs "query"`

## Weather (set by Darin 2026-05-15, reaffirmed 2026-05-16)
- **Always use Celsius** for all temperature/weather responses
- **Default location:** Sunnyvale, CA 94086 (near Sunnyvale Library)
- wttr.in: append `&m` or `?m` to force metric (US defaults to Fahrenheit)
- Wind in km/h, temperature in °C

## Calendar Event Creation (2026-05-15)
- Can create/delete events using the Google Calendar API via `calendar.events.insert/delete`
- Run from: `~/.openclaw/workspace/skills/google-workspace-byok/scripts/`
- Need `NODE_PATH=./node_modules` to resolve googleapis
- Calendar IDs:
  - Personal: `darinyu27@gmail.com`
  - Family: `family03280057382472202100@group.calendar.google.com`
  - Paofu & D: `a083de30704edd3b8a3ef5e846c5c6396e236a7a1244a41ca67db9c92591f3ce@group.calendar.google.com`
  - Work (read-only): `zyu@netflix.com`
- Use ISO strings with explicit timezone (America/Los_Angeles)
- Events on Paofu & D calendar = visible to both Darin and Paofu

## Cron Job Routing (set by Darin 2026-05-16)

### Channel IDs
- `C07MEFVCDHP` = #random
- `C07LV6XMHNJ` = #learning (used by Personal Morning Brief, Tech+Finance)
- `C0B41EQGXC3` = Daily Journal Summary target
- `C0B420KCYAV` = Daily Weather Brief target
- `C0B4EK31NCU` = <#C0B4EK31NCU> (used for cron job status/confirmation fallback)

### Cron Delivery
| # | Job | Channel | Notes |
|---|---|---|---|
| 1 | Git auto-sync workspace | `slack:C0B4EK31NCU` (<#C0B4EK31NCU>) | Changed 2026-05-17: now posts status to <#C0B4EK31NCU> |
| 2 | Daily Journal Summary | `slack:C0B4EK31NCU` (<#C0B4EK31NCU>) | Changed 2026-05-17: was C0B41EQGXC3 |
| 3 | Daily Weather Brief | `slack:C0B420KCYAV` | Already correct |
| 4 | Personal Morning Brief | `slack:C07LV6XMHNJ` (#learning) | |
| 5 | Work Meeting + Email Alert | `slack:U07MEG6NMED` (DM Darin) | |
| 6 | Tech + Finance Daily Digest | `slack:C07LV6XMHNJ` (#learning) | |
| 8 | Memory Dreaming Promotion | `slack:C0B4EK31NCU` (<#C0B4EK31NCU>) | System-managed, delivery set to <#C0B4EK31NCU> |
| 9 | Correction Retrospective | `slack:C0B4EK31NCU` (<#C0B4EK31NCU>) | Changed 2026-05-17: was 'last' |

## Activities & Live Events Rule (set by Darin 2026-05-16)
When suggesting or answering about any live activity — shows, meetups, concerts, comedy nights, sports games, events, flea markets, farmers markets, or anything happening in-person:
- **Always include a resource link** (ticket page, venue website, eventbrite, official site, etc.)
- If multiple options, link each one
- Don't just name the event/venue — provide a clickable way for Darin to learn more or buy tickets

## 💪 Cron Job Rules (set by Darin 2026-05-17)

### ⚠️ Pre-Send Checklist APPLIES TO ALL CRON OUTPUT

The same Pre-Send Checklist from the MANDATORY section above applies to EVERY cron job Slack message:
1. ✅ Thread routing correct? (cron jobs are standalone messages, no threadId needed unless replying in a thread)
2. ✅ Zero italic? (`_text_` never appears)
3. ✅ Filter run? (pipe through `scripts/slack_format.sh`)

### Rule 1: Bold Only — Zero Italic

All cron job output that delivers to Slack MUST use bold over italic. No exceptions.
- In Slack mrkdwn: bold = `*text*`, italic = `_text_` (never use).
- Every cron job prompt MUST include formatting instructions: use *bold* for emphasis, never use italic.
- Even one italic underscore in cron output is a bug.

### Rule 2: Always Output — Never Complete Silently

Every cron job MUST output something. If a job has nothing to report (no events, no changes, nothing urgent), it MUST post a brief status message to <#C0B4EK31NCU> (C0B4EK31NCU).
- Never use NO_REPLY as a way to silently skip.
- Never complete silently (no output, no errors, nothing).
- Acceptable silent exits: only for system-managed internal jobs (like Memory Dreaming Promotion) that the system itself manages.
- **Fallback channel:** C0B4EK31NCU (<#C0B4EK31NCU>) — for status confirmations, "nothing to report", and silent job outputs.
- Jobs that actively send to other channels (DM Darin, #learning, weather channel) should use message tool for those destinations, and if the final decision is "nothing to say", post to <#C0B4EK31NCU> instead of NO_REPLY.

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
