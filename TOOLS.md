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
When a new Slack channel message or thread message routes here, react with an 👀 or 👍 via `message(action=react, emoji="👀")` BEFORE doing any work. This is not optional. This is the first thing, always. No work, no reading, no processing until the emoji is sent.

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

## Weather (set by Darin 2026-05-15)
- Always use **metric system / Celsius**
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

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.