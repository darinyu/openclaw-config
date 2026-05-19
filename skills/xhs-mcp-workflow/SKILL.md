---
name: xhs-mcp-workflow
description: Unified workflow for Xiaohongshu (小红书/XHS/Rednote) via xiaohongshu-mcp MCP service. Covers the full pipeline: MCP health check, login guard, keyword search with pagination, parallel fetch of note details + comments, ranking by engagement, structured GitHub reports, and Slack-formatted summaries. Use whenever the user asks to search XHS, analyze XHS content, browse XHS notes, or any Rednote-related research, including food/restaurant searches, product research, travel planning, or trend analysis.
---

# XHS MCP Workflow

Key paths:
- `XHS_SKILL_DIR` = `/data/.openclaw/workspace/skills/xiaohongshu-mcp-openclaw`
- `WORKFLOW_DIR` = `/data/.openclaw/workspace/skills/xhs-mcp-workflow`
- `REPORT_REPO` = `darinyu/deep-research-reports` (push via `push_xhs_report.py`)

**Do NOT write reports to darinyu/openclaw-config.** Use `push_xhs_report.py` which targets `darinyu/deep-research-reports`.

## Report Push Script

```bash
python3 /data/.openclaw/shared-skills/scripts/push_xhs_report.py \
  --keyword "<keyword>" --file <report.md>
```

Pushes to: `darinyu/deep-research-reports/blob/main/xhs/<YYYY-MM-DD>/<keyword>/report.md`

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

## Language Rules (CRITICAL)

1. **Ask the user** what language they prefer for the output. Default is Chinese.
2. **DO NOT translate** location names, restaurant names, or hotel names — keep them in their original language (e.g. "Maguro Brothers" stays "Maguro Brothers", not translated to Chinese).
3. **Keep all content from XHS posts in their original language** — if the post is in Chinese, keep the summary in Chinese. If the post is in English, keep it in English.
4. The overall report/summary should be in the language the user requested.

## Display Conventions (Slack Summaries)

Slack summaries should be **brief and scannable** — NOT the full report.

**What goes in Slack:**
- Rationale (1 line)
- Pro tips (3-5 bullet points)
- Activities preview (what's covered, not the schedule)
- Food preview (cuisines available, not the list)
- Link to full report on GitHub

**Formatting:**
- Use `:heart:` for likes, `:star:` for saves/collections
- Always rank results by `likedCount + collectedCount` (descending)
- Use `*bold*` for emphasis — run through `scripts/slack_format.sh` before sending
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

Compile results into a reusable data format:

```json
{
  "keyword": "honolulu food",
  "searched_at": "2026-05-19T05:26:00Z",
  "searched_by": "xiaohongshu-mcp",
  "total_results": 22,
  "results": [
    {
      "rank": 1,
      "title": "...",
      "author": "...",
      "likes": 1179,
      "collects": 2128,
      "comments": 34,
      "link": "https://www.xiaohongshu.com/explore/<feed_id>",
      "desc_excerpt": "...",
      "comment_sentiment": "positive/mixed/negative",
      "mentions": ["Restaurant A", "Restaurant B"]
    }
  ],
  "aggregated": {
    "top_restaurants": [
      {"name": "Maguro Brothers", "mentions": 3, "avg_stars": 850, "sentiment": "positive"},
      {"name": "Island Vintage Coffee", "mentions": 2, "avg_stars": 720, "sentiment": "positive"}
    ],
    "top_activities": [
      {"name": "Lanikai Pillbox Hike", "location": "Kailua", "mentions": 2, "avg_stars": 900, "sentiment": "positive"}
    ],
    "pro_tips": ["Rent car for one day only", "..."]
  }
}
```

This JSON should be checked into the GitHub report alongside the markdown.

### Step 4: Build the full report

The full report lives on GitHub (NOT in Slack). Structure:

```markdown
# XHS Research: <keyword>

**Date:** YYYY-MM-DD
**Account:** xiaohongshu-mcp

---

## Summary
> 1-2 sentence overview

## Rationale
> Why this research was done, what questions we're answering

## Activities
Grouped by location/area. For each activity:
- Name, location, key details
- XHS post links that recommend it
- Comment sentiment summary
- Pro tips from commenters
- **Evidence**: include 1–2 short quotes (≤25 words each) from the post or comments + link

### [Location 1]
### [Location 2]
...

## Food & Restaurants
For each restaurant:
- Name, cuisine type, approximate price
- Number of XHS posts mentioning it (with links)
- Comment sentiment (positive/mixed/negative — summarize what people say)
- Pro tips
- **Evidence**: include 1–2 short quotes (≤25 words each) from the post or comments + link

### Quick-reference table
| Restaurant | Type | Price | Mentions | Sentiment | XHS Links |
|---|---|---|---|---|---|
...

## Daily Itinerary

**One hotel base preferred** — minimize hotel moves. Stay in one hotel for the whole trip if the destination allows.

### Day 1 | Date — Theme
  **AM** · activity
  **Lunch** · restaurant
  **PM** · activity
  **Dinner** · restaurant
  **Evening** · optional activity

### Day 2 | Date — Theme
  ...

### Transport Map
| Leg | Route | Duration | Mode | Comfort |
|-----|-------|----------|------|---------|
| 1 | Place A → Place B | 30min | Walk 🚶 | ★★★★★ |
| 2 | Place B → Place C | 15min | Bus 🚌 | ★★★★☆ |

## Pro Tips (from XHS users)
- Tip 1
- Tip 2

---

## Appendix A: All Posts Analyzed
Full list of XHS posts with links and metadata.

| # | Title | Author | 👍 | ⭐ | 💬 | Link |
|---|-------|--------|----|----|----|------|
| 1 | ... | ... | ... | ... | ... | ... |

## Appendix B: Post Summaries + Comments
For each top post:
- Title + Link
- Full description excerpt (if useful)
- Top comments (with likes, sentiment notes)
```

### Step 5: Push report to GitHub

```bash
python3 /data/.openclaw/shared-skills/scripts/push_xhs_report.py \
  --keyword "<keyword>" --file <report.md>
```

Also save the structured JSON alongside the report (same filename, `.json` extension).

### Step 6: Present brief summary in Slack

Only include: rationale, pro tips, activities preview, food preview, and the GitHub link. NOT the full schedule or full food list.

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
