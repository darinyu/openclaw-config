---
name: xhs-mcp-workflow
description: "Unified workflow for Xiaohongshu (小红书/XHS/Rednote) via xiaohongshu-mcp MCP service. Covers the full pipeline: MCP health check, login guard, keyword search with pagination, parallel fetch of note details + comments, ranking by engagement, structured GitHub reports, and Slack-formatted summaries. Use whenever the user asks to search XHS, analyze XHS content, browse XHS notes, or any Rednote-related research, including food/restaurant searches, product research, travel planning, or trend analysis."
---

# XHS MCP Workflow

Key paths:
- `XHS_SKILL_DIR` = `/data/.openclaw/workspace/skills/xiaohongshu-mcp-openclaw`
- `WORKFLOW_DIR` = `/data/.openclaw/workspace/skills/xhs-mcp-workflow`

## Naming Convention

xiaohongshu, xhs, and rednote are the same platform. Use any interchangeably.

## MCP Health Check

### Pre-flight check (on every XHS request)

Before any xiaohongshu operation, check MCP server availability:

```bash
mcporter list xiaohongshu-mcp 2>&1 >/dev/null && echo "OK" || echo "DOWN"
```

If DOWN, reboot immediately:
```bash
bash <XHS_SKILL_DIR>/scripts/start_server.sh
```

Wait for port to be ready (up to 20s), then re-check.

### Cronjob (30-min heartbeat)

A cronjob named **XHS MCP Health Check** runs every 30 minutes.
Script: `<WORKFLOW_DIR>/scripts/xhs_mcp_health_check.sh`

The cronjob:
1. Checks `mcporter list xiaohongshu-mcp`
2. If DOWN, attempts to restart via `start_server.sh`
3. Posts status to Slack

## Login Guard

Every XHS request MUST check login status first:

```bash
python3 <XHS_SKILL_DIR>/scripts/xhs_mcp_client.py \
  --server xiaohongshu-mcp ensure-login --strip-qr-image
```

If the response shows `status=logged_out` or `already_logged_in=false`, run the QR login flow:
```bash
bash <XHS_SKILL_DIR>/scripts/login_qr.sh xiaohongshu-mcp
```
Then present the QR image to the user for scanning.

If the login flow itself fails (e.g. QR doesn't scan), retro on the issue and update this skill.

## Display Conventions

- Use `:heart:` for likes, `:star:` for saves/collections
- Always rank results by `likedCount + collectedCount` (descending)
- Include permalink: `https://www.xiaohongshu.com/explore/<feed_id>`
- Use `**bold**` for emphasis — run through `scripts/slack_format.sh` before sending to Slack
- Keep summaries in the post's original language (prefer Chinese)
- Show progress periodically for multi-step operations

## Relevance Check

Before committing to a full search workflow, check if the keyword/topic is relevant to Xiaohongshu content:

1. **Assess the topic** — Is this something users post about on XHS? (e.g. travel, food, beauty, fashion, lifestyle, local recommendations, product reviews)
2. **If relevant** → Proceed with full search workflow
3. **If unclear** — Do a quick light search first (`search_feeds` with limit=3), check if results have meaningful engagement (likes > 0), then decide

Relevant topics that work well on XHS:
- Travel destinations & itineraries
- Restaurant/food reviews & recommendations
- Product reviews & shopping
- Beauty/fashion/style
- Local hidden gems & tips
- Life hacks & how-tos
- Things to do in [city/area]

## Search Workflow

### Step 1: Search for keyword(s)

```bash
mcporter call xiaohongshu-mcp.search_feeds --keyword "<keyword>"
```

If the keyword might have multiple language variants, search each and merge results.
Handle pagination if `hasMore` is true — pass `cursor` from the previous response.

### Step 2: Fetch details + comments

From search results, extract top N notes by `likedCount + collectedCount`.
Fetch their details with comments:

```bash
mcporter call xiaohongshu-mcp.get_feed_detail \
  --feed_id "<id>" \
  --xsec_token "<token>" \
  --load_all_comments true \
  --limit 20
```

Parallelize by spawning multiple `mcporter call` requests concurrently (up to 5 at a time).
Collect **text and comments only** (`.desc` + `.comments[].content`) — skip video/image data.

### Step 3: Aggregate structured data

Compile results:
- keyword, timestamp, account name
- per-note: title, author, likes, collects, comments count, link, text, top N comments

### Step 4: Push report to GitHub

```bash
python3 /data/.openclaw/shared-skills/scripts/push_xhs_report.py \
  --keyword "<keyword>" --file <report.md>
```

This pushes to `darinyu/deep-research-reports/blob/main/xhs/<YYYY-MM-DD>/<keyword>/<HHMMSS>/report.md`

### Step 5: Present summary to user

Use `summarize-pro` skill (or inline summary) to organize data into a concise readable format.
Apply display conventions: bold, :heart:/:star:, original language, ranked.

## Progress Reporting

For multi-step ops, send periodic Slack updates:
- Step announcement when starting
- Progress mid-way
- Final summary when done

## Error Recovery

| Failure | Action |
|---|---|
| mcporter not found | `npm install -g mcporter` |
| MCP server down | Run `bash <XHS_SKILL_DIR>/scripts/start_server.sh` |
| Login expired | Run `bash <XHS_SKILL_DIR>/scripts/login_qr.sh xiaohongshu-mcp` |
| Search returns 0 results | Try alternate language keywords or broader terms |
| Rate limited / 429 | Wait 10s, retry once; if persists, alert user |
| "This page isn't available" | Note is private/deleted — skip it |
