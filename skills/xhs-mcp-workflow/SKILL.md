---
name: xhs-mcp-workflow
description: Unified workflow for Xiaohongshu (小红书/XHS/Rednote) via xiaohongshu-mcp MCP service. Covers the full pipeline: MCP health check, login guard, keyword search with pagination, parallel fetch of note details + comments, ranking by engagement, structured GitHub reports, and Slack-formatted summaries. Use whenever the user asks to search XHS, analyze XHS content, browse XHS notes, or any Rednote-related research, including food/restaurant searches, product research, travel planning, or trend analysis.
---

# XHS MCP Workflow — Shared Search Engine

This skill is the **single authoritative source** for all XHS search strategy. Other skills (xhs-food-research, xhs-trip-planner) reference this workflow rather than duplicating search logic. If you change how XHS searches work, change it here.

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

## Search Workflow (SHARED — all XHS skills use this)

If another skill says "Use xhs-mcp-workflow for search", this is the section they're referring to.

### Step 1: Search for keyword(s) — wide net first

```bash
mcporter call xiaohongshu-mcp.search_feeds --keyword "<keyword>"
```

If the keyword might have multiple language variants, search each and merge results.
**Use pagination** — pass `cursor` from response when `hasMore=true`. Collect **40-60+ total results** to have a wide pool.

### Step 1b: Filter by engagement threshold

After collecting all results, only proceed with posts that have meaningful engagement. This avoids wasting API calls and tokens on low-value posts:

```python
results.sort(key=lambda p: p['likes'] + p['collects'], reverse=True)
top_engagement = results[0]['likes'] + results[0]['collects']
threshold = max(top_engagement * 0.1, 30)

worthy = [p for p in results if (p['likes'] + p['collects']) >= threshold]
skipped = len(results) - len(worthy)
print(f'Top engagement: {top_engagement}, Threshold: {threshold}')
print(f'Worthy: {len(worthy)}/{len(results)} ({skipped} skipped — too low)')
```

**Rationale:** If top post has 1K+ likes, skip posts under 100. If top has 500, skip under 50. Only enrich posts worth your time.

Only use `worthy` posts for enrichment in Step 2. Skip the rest.

### Step 2: Fetch details + comments

From search results, extract **ALL** notes (not just top N) — every post that will be in data.json must have details fetched.
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

#### ⚠️ CRITICAL: search_feeds has NO desc — must call get_feed_detail separately

`search_feeds` only returns `noteCard` with 5 keys: `type, displayTitle, user, interactInfo, cover`. **It does NOT include `desc` (post body text) or comments.** The desc field is ONLY available via `get_feed_detail`.

Think of it like:
- `search_feeds` = Google SERP (titles, links, engagement counts)
- `get_feed_detail` = clicking into the actual article

This means:
1. **Never** assume a post from `search_feeds` has usable content. You MUST call `get_feed_detail` to get desc + comments.
2. Track which posts have been enriched with a `has_content` flag (True if desc is non-empty after get_feed_detail).
3. **Never use a post for recommendations if get_feed_detail returned empty desc.** No content = no recommendation.
4. All recommendations must come from reading and analyzing the actual desc + comments text.

#### ⚠️ CRITICAL: search_feeds has NO desc — must call get_feed_detail separately

`search_feeds` only returns `noteCard` with 5 keys: `type, displayTitle, user, interactInfo, cover`. **It does NOT include `desc` (post body text) or comments.** The desc field is ONLY available via `get_feed_detail`.

Think of it like:
- `search_feeds` = Google SERP (titles, links, engagement counts)
- `get_feed_detail` = clicking into the actual article

This means:
1. **Never** assume a post from `search_feeds` has usable content. You MUST call `get_feed_detail` to get desc + comments.
2. Track which posts have been enriched with a `has_content` flag (True if desc is non-empty after get_feed_detail).
3. **Never use a post for recommendations if get_feed_detail returned empty desc.** No content = no recommendation.
4. All recommendations must come from reading and analyzing the actual desc + comments text.

### Step 3: Aggregate structured data (with content validation)

After fetching details for all top posts, validate which ones actually have content:

```python
# After enrichment, build has_content tracking
usable_posts = []
skip_count = 0
for post in enriched_posts:
    has_content = bool(post.get('desc', '').strip()) and len(post.get('desc', '').strip()) >= 20
    post['has_content'] = has_content
    if has_content:
        usable_posts.append(post)
    else:
        skip_count += 1
        print(f'SKIP (no desc): {post["link"]}')

print(f'Posts with content: {len(usable_posts)}/{len(enriched_posts)} ({skip_count} skipped)')
```

Only use posts with `has_content=True` for analysis and recommendations.

Compile results into a reusable data format (include `desc` and `has_content`):

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
      "desc": "...",  # full post text, MANDATORY from get_feed_detail
      "has_content": true,  # whether get_feed_detail returned non-empty desc
      "top_comments": [
        {"content": "...", "nickname": "...", "likes": 5}
      ],
      "mentions": ["Restaurant A", "Restaurant B"]
    }
  ],
  "aggregated": { ... }
}
```

**Hard rule:** Do NOT include any result with `has_content=false` in `aggregated` analysis. They have no readable content.

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
