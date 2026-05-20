---
name: xhs-food-research
description: "Xiaohongshu (小红书) food & restaurant research for any city or area. Search XHS for restaurant recommendations, then produce a Slack summary (grouped by cuisine category with dessert, timing/meal type, restaurant name + recommended dishes) and a detailed GitHub report with mentions count and XHS reference links. Use when user asks about: restaurant recommendations, food recs, where to eat, what to eat, what's good to eat in [city/area], find [city]好吃的/美食/必吃/餐厅推荐/吃什么/美食攻略/吃货/探店, XHS food research, 小红书美食攻略, 探店, 吃货攻略, 晚饭去哪里吃, 午饭推荐, 聚餐推荐, 宵夜推荐, local eats, hidden gems food, best restaurants in [city], 美食探店, 城市美食, 美食推荐, 餐厅探店, 好吃的地方, 小馆推荐, food guide, foodie guide, or any similar food-related XHS searches. Also handles: local cuisine research, specific cuisine types in a city (川菜/火锅/日料/越南菜/甜品/奶茶/烧烤/烤肉/brunch), finding breakfast/brunch/lunch/dinner/late night spots, and dessert shops on XHS."
---

# XHS Food Research Skill

## Overview

Research food/restaurant recommendations on XHS for any city/area. Produces:

1. **Slack summary** — category-grouped with restaurant names, recommended dishes, and timing context
2. **GitHub report** — detailed analysis with mentions count, XHS reference links, and comment sentiment

## Key Paths

- `XHS_SKILL_DIR`: `/data/.openclaw/workspace/skills/xiaohongshu-mcp-openclaw`
- `WORKFLOW_DIR`: `/data/.openclaw/workspace/skills/xhs-mcp-workflow`
- `SKILL_DIR`: `/data/.openclaw/workspace/skills/xhs-food-research`
- `PUSH_SCRIPT`: `/data/.openclaw/shared-skills/scripts/push_xhs_report.py`

## Pre-flight

```bash
mcporter list xiaohongshu-mcp 2>&1 >/dev/null && echo "OK" || echo "DOWN"
```

If DOWN:
```bash
bash <XHS_SKILL_DIR>/scripts/start_server.sh
```
Wait up to 20s, then re-check.

## Login Guard

```bash
python3 <XHS_SKILL_DIR>/scripts/xhs_mcp_client.py --server xiaohongshu-mcp ensure-login --strip-qr-image
```

If `status=logged_out`, run QR flow:
```bash
bash <XHS_SKILL_DIR>/scripts/login_qr.sh xiaohongshu-mcp
```

## Search Workflow

**Search strategy is managed by xhs-mcp-workflow (shared).** Follow that skill's Search Workflow (Step 1 wide net + Step 1b engagement threshold) for all generic search operations.

> Shorthand: Do Step 1 + Step 1b from xhs-mcp-workflow/SKILL.md.

### Food-specific keywords

Search with these keyword variants for maximum coverage:

```bash
mcporter call xiaohongshu-mcp.search_feeds --keyword "<city> 好吃的"
mcporter call xiaohongshu-mcp.search_feeds --keyword "<city> 美食"
mcporter call xiaohongshu-mcp.search_feeds --keyword "<city> 餐厅推荐"
mcporter call xiaohongshu-mcp.search_feeds --keyword "<city> 吃什么"
```

Merge results from all searches, deduplicate by feed `id`.
If the city has specific cuisine keyword density (e.g. "san mateo 川菜"), search those too.

### Save Raw Search Results Locally

After each search, save the raw results to local files for later GitHub push:

```bash
mkdir -p xhs-research/<city>-food/raw_search_results
mcporter call xiaohongshu-mcp.search_feeds --keyword "<keyword>" \
  > xhs-research/<city>-food/raw_search_results/<keyword>.json
```

Keep an `all_results` list that accumulates across all search rounds, storing `id` and `xsecToken` for enrichment:

```python
all_results = []  # defined at start

# After each search, extract clean fields and append to all_results
# Each entry MUST include: id, xsecToken (for get_feed_detail), title, nickname, likes, collects, comments, link
```

### Enrich Top Posts — MANDATORY (content source)

⚠️ **CRITICAL:** `search_feeds` does NOT return `desc` (post body). `noteCard` only has `type, displayTitle, user, interactInfo, cover`. To get actual post content + comments, you MUST call `get_feed_detail` separately.

Before building final data.json, enrich **ALL posts** with full description + comments via `get_feed_detail`. Do NOT skip any — if a post isn't enriched, mark `has_content: 'unknown'`, not `false`.

**Parallelize enrichment:** batch 3-5 concurrent `mcporter call` calls to speed up.

```bash
mcporter call xiaohongshu-mcp.get_feed_detail \
  --feed_id "<id>" --xsec_token "<token>" \
  --load_all_comments true --limit 15 | python3 -c "
import json, sys
raw = json.load(sys.stdin)
data = raw.get('data', raw)
note = data.get('note', {}) or data.get('noteCard', {})
desc = note.get('desc', '')
has_content = bool(desc.strip()) and len(desc.strip()) >= 20
print(f'desc_len={len(desc)}, has_content={has_content}')
print(desc[:2000])
"
```

**Store with `has_content` flag:**
```python
enriched_map[link] = {
    'desc': desc,
    'has_content': bool(desc.strip()) and len(desc.strip()) >= 20,
    'top_comments': [...]
}
```

**RULES:**
1. Posts with `has_content=False` (empty desc) must be **excluded** from all recommendations.
2. All recommendations must come from reading the actual `desc` text + comments, not from title/likes alone.
3. Every entry must cite a specific evidence quote from desc or comments.

### Parse Results Script

Use the helper script to extract structured data from search results:

```bash
python3 <SKILL_DIR>/scripts/parse_results.py --input <json_file>
```

This extracts: title, author, likes, collects, comments count, and key text for each post.

## Compilation Rules (CRITICAL — always follow)

### Group by Category

Group all restaurants into these categories (add more as needed):

| Emoji | Category | Examples |
|-------|----------|---------|
| 🌶️ | 川菜 (Sichuan) | 麻辣、毛血旺、水煮鱼 |
| 🥘 | 湘菜 (Hunan) | 小炒肉、剁椒鱼头 |
| 🍲 | 火锅 (Hotpot) | 重庆火锅、螺蛳粉火锅、AYCE |
| 🍜 | 面食/西北 (Noodles) | 兰州拉面、山西面、biangbiang面 |
| 🥟 | 饺子/点心 (Dumplings) | 煎饺、小笼包 |
| 🐔 | 海南鸡/粤菜 (Cantonese) | 海南鸡、烧腊、茶餐厅 |
| 🦐 | 粤菜/早茶 (Dim Sum) | 虾饺、烧卖、叉烧包 |
| 🐟 | 烤鱼/鱼鲜 (Fish) | 烤鱼、酸菜鱼、水煮鱼 |
| 🥩 | 烤肉/韩式 (BBQ) | 韩式烤肉、日式烧肉 |
| 🍣 | 日料 (Japanese) | 寿司、拉面、刺身 |
| 🇻🇳 | 越南菜 (Vietnamese) | Pho、春卷、越南包 |
| 🇹🇭 | 泰餐 (Thai) | 冬阴功、咖喱 |
| 🇰🇷 | 韩餐 (Korean) | 拌饭、炸鸡、豆腐锅 |
| 🦞 | 手抓海鲜 (Cajun/Seafood) | 手抓海鲜、Cajun |
| 🍕 | 西餐/其他 (Western) | 意面、汉堡、牛排 |
| 🥟 | 融合菜 (Fusion) | 新派融合 |
| 🍖 | 特色肉类 (Meat) | 猪肘、羊肉 |
| 🍰 | 甜品/奶茶 (Dessert) | 椰子冻、奶茶、蛋糕 |
| 🥐 | Brunch/Café | 早午餐、咖啡、西式早餐 |

**ALWAYS include Dessert category** — even if few results, look for it explicitly.

**ALWAYS consider timing/meal type as a secondary label:**
- ☀️ 早午餐 (Brunch/Breakfast) — cafes, morning offerings
- 🌤️ 午餐 (Lunch) — set lunches, quick eats
- 🌙 晚餐 (Dinner) — full dinner spots
- 🌃 夜宵 (Late Night) — late-night eats
- 🕐 不限 (Anytime) — always available

### Restaurant Entry Format

Every restaurant entry MUST include:

```
**{Restaurant Name}** ({Address/Area} if known) · {Likes}👍/{Collects}⭐
推荐理由: {1-2 sentence why this is recommended, based on XHS data}
推荐菜品: {List of recommended dishes from XHS posts}
💬 XHS评价: {Brief comment sentiment summary}
🕐 适合: {Meal type — brunch/lunch/dinner/late night/anytime}
```

### Post-Compilation Checks

- [ ] Every restaurant has a recommended dishes list
- [ ] Dessert category is present
- [ ] At least one restaurant has a brunch/lunch timing label
- [ ] Each entry has likes/collects where available
- [ ] No duplicate restaurants

## GitHub Push: Two Locations (RAW + PROCESSED)

Push to **two separate locations** on `darinyu/deep-research-reports`, following the same pattern as the trip planner:

### Location A — RAW DATA → `/xhs/<YYYY-MM-DD>/<city>-food/`

Save all raw search results as `data.json` with enriched fields (desc + has_content + top_comments). Push via Python `gh_put()` helper (see trip planner for full pattern).

```python
import json, os, subprocess

# Build enriched data.json from all search results
# Each result MUST include: rank, title, author, likes, collects, comments, link, desc, has_content, top_comments
# Enrich top posts using get_feed_detail BEFORE building this
data_json = {
    'keyword': '<city>-food',
    'searched_at': '<timestamp>',
    'searched_by': 'xiaohongshu-mcp',
    'total_results': <N>,
    'searches_used': ['<keyword1>', '<keyword2>', ...],
    'results': [{
        'rank': r['rank'],
        'title': r['title'],
        'author': r['nickname'],
        'likes': r['likes'],
        'collects': r['collects'],
        'comments_count': r['comments'],
        'link': r['link'],
        'desc': enriched_desc,           # MANDATORY: from get_feed_detail
        'has_content': has_content_flag,  # MANDATORY: True if desc is non-empty
        'top_comments': top_5_comments,   # MANDATORY: top 5 from get_feed_detail
    } for i, r in enumerate(all_results)]
}

# VALIDATE: warn about posts with no content
empty_posts = [r['rank'] for r in data_json['results'] if not r.get('has_content')]
if empty_posts:
    print(f'WARNING: {len(empty_posts)} posts have no desc (ranks: {empty_posts}) — will be skipped in recommendations')
```
```

### Location B — PROCESSED REPORT → `/xhs-research/<city>-food/`

Push the formatted markdown report using the template at `references/report-template.md`:

```bash
python3 /data/.openclaw/shared-skills/scripts/push_xhs_report.py \
  --keyword "<city>-food-research" --file <report.md>
```

This saves to: `darinyu/deep-research-reports/blob/main/xhs-research/<city>-food/research/report.md`

### Hard Rules

- `/xhs/` is ONLY for raw `data.json`. Never push markdown reports there.
- `/xhs-research/` is ONLY for processed reports. Never push raw data there.
- Always push BOTH. Raw data first, then processed report.
- Before searching, check if `/xhs/<YYYY-MM-DD>/<city>-food/data.json` already exists and is ≤7 days old.

## Slack Summary Format

Keep the Slack message **concise but complete**. Include:

1. Brief intro ("搜到了！{City} 美食攻略，从 XHS 高赞笔记整理")
2. Category groups with key restaurants under each (name + recommended dishes)
3. Always include Dessert category
4. Mark a few timing labels (brunch, late night) where relevant
5. End with a **Top Picks** section (3-5 recommendations)
6. Link to full GitHub report

**Formatting for Slack:**
- Use `*bold*` for restaurant names and category headers
- Use `:heart:` = 👍, `:star:` = ⭐
- Use `:sunny:` / `:night:` / `:city_sunrise:` for timing indicators
- Use `:arrow_down:` separator between categories
- Run through `scripts/slack_format.sh` before sending

## Top Picks Section

After the category listing, always include a Top Picks ranking:

```
**🏆 {City} Top Picks**
🥇 {Restaurant} — {one-line reason}
🥈 {Restaurant} — {one-line reason}
🥉 {Restaurant} — {one-line reason}
4. {Restaurant} — {one-line reason}
5. {Restaurant} — {one-line reason}
```

Rank by: XHS engagement (likes+collects), uniqueness of cuisine, and overall recommendation strength.

## Language Rules

- Ask the user what language they prefer. Default: Chinese
- Do NOT translate restaurant names, dish names, or location names
- Keep XHS post content in its original language
- Overall report in user's preferred language
