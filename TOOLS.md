---
summary: "Workspace template for TOOLS.md"
read_when:
  - Bootstrapping a workspace manually
---

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

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

## 🔔 Drive Folder Watch Rule (set by Darin 2026-05-15)

- **Folder ID:** `1-I3xydVuGTGNMj5oH7mA5J_OGF1NxQFZ`
- **Rule:** Whenever reading from or modifying any document in this folder, send Darin a Slack DM (`U07MEG6NMED`).
- **Scope:** This covers the personal account (its Drive scope has read-only access).

## Channel Routing

**Slack → Control UI:**

When a Slack message routes to this session (webchat/Control UI), ALWAYS send the reply back to Slack using the `message` tool. Do not just reply here.

**RULE: Messages originating from Slack MUST be replied to in Slack.**

How to detect: if the session's delivery context has `channel: "slack"` or the message came with Slack @-mention formatting (e.g. `<@U...>`), the origin is Slack. Reply goes to Slack only — or Slack + Control UI if convenient.

**Thread rules for Slack replies:**
- **Direct @-mention/tag** of DDDD → reply in a **thread** under that message (use the message's `ts` as `threadId`).
- **Thread reply** (message has a threadId) → reply in the same thread.
- **General channel message** (no tag, no thread) → post directly to the channel.

This applies to \`#random\` and any other Slack channels that route here.

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

### Cron Delivery
| # | Job | Channel | Notes |
|---|---|---|---|
| 1 | Git auto-sync workspace | none | Internal, no delivery |
| 2 | Daily Journal Summary | `slack:C0B41EQGXC3` | Fixed 2026-05-16, was error on `last` |
| 3 | Daily Weather Brief | `slack:C0B420KCYAV` | Already correct |
| 4 | Personal Morning Brief | `slack:C07LV6XMHNJ` (#learning) | |
| 5 | Work Meeting + Email Alert | `slack:U07MEG6NMED` (DM Darin) | |
| 6 | Personal Calendar Morning Brief | `slack:U07MEG6NMED` (DM Darin) | |
| 7 | Tech + Finance Daily Digest | `slack:C07LV6XMHNJ` (#learning) | |

## Activities & Live Events Rule (set by Darin 2026-05-16)
When suggesting or answering about any live activity — shows, meetups, concerts, comedy nights, sports games, events, flea markets, farmers markets, or anything happening in-person:
- **Always include a resource link** (ticket page, venue website, eventbrite, official site, etc.)
- If multiple options, link each one
- Don't just name the event/venue — provide a clickable way for Darin to learn more or buy tickets

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.