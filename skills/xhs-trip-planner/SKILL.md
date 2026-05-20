---
name: xhs-trip-planner
description: "Vacation trip planning using Xiaohongshu (小红书/XHS/Rednote) research. Covers the full pipeline: interviews user about their trip, checks existing GitHub XHS search reports from the past week, uses xhs-mcp-workflow to research activities/food on XHS, uses hotel-research skill for accommodations (hotels only, no Airbnb). Presents ADHD-friendly day-by-day itineraries with bold syntax. Use when user asks to: plan a vacation, plan a trip, plan a holiday, plan an itinerary, build a travel plan, what to do in [city], things to do in [country], where to eat in [city], where to stay in [city], travel recommendations, vacation planning, sightseeing, travel guide, 行程规划, 旅游攻略, 旅行计划, needs recommendations for things to do, places to eat, or where to stay. Also handles multi-city/country trips, road trips, honeymoon planning, family vacation planning, solo travel planning."
---

# XHS Trip Planner

This skill uses `xhs-mcp-workflow` to research destinations on Xiaohongshu, and `hotel-research` skill for hotels via Google Maps/Travel. No Airbnb.

## PROGRESS UPDATE RULE (CRITICAL)

**Every 2 minutes minimum**, send a planning update to the user detailing:
- Which steps are complete ✓
- Which step is in progress ⟳
- What was found so far (briefly)
- What's next

Format:
```
*Trip Planning Update — <elapsed>*  (thinking trace: <session_id>)

✓ Step 1: Interview complete
⟳ Step 2: XHS research round 2/3 — searching "<keyword>"
  - Found X popular itineraries so far
  - <interesting finding>

Next: Round 3 — searching "<keyword>"
```

## Workflow

### Step 1: Interview the user — with Preference System (MCQ format only)

**Preference file:** `skills/xhs-trip-planner/data/travel_preferences.json` — stored in workspace and checked into git.

**At start of Step 1, load preferences:**

```bash
python3 skills/xhs-trip-planner/scripts/xhs_prefs.py show 2>/dev/null || echo "No preferences yet"
```

Check if this is a first-time user (no saved prefs) or returning user.

#### First-time user: Full preference + trip interview

Ask ONE question at a time. Use MCQ for prioritization. Save to preference system after collecting.

**Preference questions (asked once, saved to JSON):**

1. *Travel style* — How do you usually travel?
   > 1️⃣ *Adventurous* — off the beaten path, local experiences
   > 2️⃣ *Relaxed* — comfortable, slow-paced, less planning
   > 3️⃣ *Balanced* — a mix of both

2. *Pace* — How packed do you like your days?
   > 1️⃣ *Relaxed* — 1-2 activities, lots of free time
   > 2️⃣ *Moderate* — 3-4 activities, structured but not rushed
   > 3️⃣ *Packed* — maximize every day, full schedule

3. *Accommodation preference*
   > 1️⃣ *Hotel* — standard comfort, reliable
   > 2️⃣ *Boutique* — unique design, local character
   > 3️⃣ *Resort* — all-inclusive, amenities-focused

4. *Main interests* (multi-select — number each)
   > 1️⃣ *Food* 2️⃣ *Nature* 3️⃣ *Culture* 4️⃣ *Shopping* 5️⃣ *Hiking* 6️⃣ *Photography* 7️⃣ *History* 8️⃣ *Nightlife*

5. *Dietary needs* (multi-select — number each)
   > 1️⃣ *None* 2️⃣ *Vegetarian* 3️⃣ *Vegan* 4️⃣ *Halal* 5️⃣ *Allergies* 6️⃣ *Other*

6. *Who usually travels with you?*
   > 1️⃣ *Solo* 2️⃣ *Couple* 3️⃣ *Family with kids* 4️⃣ *Group of friends*

**Trip-specific questions (asked every time):**

7. *Where* are you going? (If multi-city, list them all)
8. *How long*? (dates or number of days)
9. *Who's going on this trip?* — note any mobility concerns
10. *Hotel moves* — REMOVED (standing rule: permanently set to minimize moves, never ask) ✅

**Then ask prioritization (MCQ ONLY):**

> How should I prioritize recommendations?
> 1️⃣ *Cheapest* — budget-friendly options first
> 2️⃣ *Highest-rated* — best reviews
> 3️⃣ *Foodie* — best food spots prioritized
> 4️⃣ *Convenient* — closest to center / easy logistics
> 5️⃣ *Instagram* — most photogenic spots
> 6️⃣ *Balanced* — a mix of everything

**Then ask language preference (MCQ ONLY):**

> What language should I use for the itinerary and report?
> 1️⃣ *Chinese (中文)* — default
> 2️⃣ *English*
> 3️⃣ *Mixed* — keep names original, summary in [your choice]

**Save preferences after interview:**

```python
import json, os
from datetime import datetime, timezone

prefs = json.load(open("skills/xhs-trip-planner/data/travel_preferences.json"))
prefs["profile"] = { ... }  # update with answers
prefs["last_updated"] = datetime.now(timezone.utc).isoformat()
json.dump(prefs, open("skills/xhs-trip-planner/data/travel_preferences.json", "w"), indent=2, ensure_ascii=False)
```

Alternatively use the helper:
```bash
python3 skills/xhs-trip-planner/scripts/xhs_prefs.py show  # inspect
```
Then write the updated prefs as described above (inline Python or manual edit).

#### Returning user: Load preferences, skip profile questions

Load existing preferences. Only ask trip-specific questions (#7-10 above) + prioritization + language.

*RULES:*
- Do NOT translate location names, restaurant names, or hotel names — keep original
- Keep XHS post content in its original language
- The overall report structure follows the user's chosen language

**Send a progress update** after interview is complete.

### Step 2: Check existing GitHub reports (past week)

Before searching XHS, check if recent reports exist:

```bash
curl -s "https://api.github.com/repos/darinyu/deep-research-reports/contents/xhs" \
  | jq -r '.[].name' | sort -r | head -7
```

This returns date folders. For each date, list keyword folders:

```bash
curl -s "https://api.github.com/repos/darinyu/deep-research-reports/contents/xhs/<date>" \
  | jq -r '.[].name'
```

If a keyword matches the destination (e.g. "paris", "france", "switzerland"), fetch and read the existing report instead of re-searching.

**Send a progress update** after checking GitHub.

### Step 3: Research on XHS — Layered Planning (MANDATORY: 3+ rounds)

For destinations without recent reports, research in layers. This is the most important step.

**Use the thinking log (`think.py`) for every search round.** Generate a session_id and log each reasoning step.

#### ⚠️ CRITICAL RULE: Recommendations MUST come from reading post content, not from counts

**The entire recommendation flow depends on reading the actual post desc (full text) and comments.** If you cannot get these, you cannot recommend that post.

1. **Before anything else:** Fetch `get_feed_detail` for every post you intend to use. Save to `enriched_map`.
2. **Filter out unusable posts:** Any post with empty `desc` (no content retrieved) must be **excluded entirely** from recommendations. You cannot use a post you can't read.
3. **Read, then recommend:** For each enriched post, read the full `desc` and top 5 `comments`. Extract:
   - **Positive sentiment**: Which activities/restaurants get praised? Specific quotes.
   - **Negative sentiment**: What gets warned about? Overpriced, overrated, tourist traps.
   - **Practical tips**: Booking advice, timing, what to avoid, hidden gems.
   - **Evidence quotes**: Short (≤25 words) quotes from desc or comments in original language.
4. **Cite your sources**: Every recommendation links back to the XHS post and includes a specific quote as evidence.
5. **No empty-content recommendations**: If a post has no `desc`, no amount of likes/saves qualifies it for a recommendation. Skip it.

**How to run content analysis in your process (inline, no external API):**
```python
# After enrichment, for each post with desc:
usable_posts = []
for link, enriched in enriched_map.items():
    if not enriched.get('desc') or len(enriched['desc'].strip()) < 20:
        print(f'SKIP (no content): {link}')
        continue
    
    desc = enriched['desc']
    comments = enriched.get('top_comments', [])
    
    # Extract positive mentions (you read and summarize these)
    positive_highlights = []  # specific things praised
    warnings = []  # negative sentiment from desc or comments
    tips = []  # practical tips from comments
    
    # Read desc for attractions, restaurants, tips, warnings
    # Read comments for opinion, additional tips, warnings
    
    usable_posts.append({
        'link': link,
        'desc': desc,
        'comments': comments,
        'highlights': positive_highlights,
        'warnings': warnings,
        'tips': tips
    })
```

**This content analysis IS the recommendation source.** The engagement metrics (likes, collects) are used for ranking — the recommendation text comes from reading the actual post content.

#### Layer 1: Days Allocation & Geography Map (Round 1 of 3+)

Search with keywords:
- `<destination> 旅游攻略 行程安排`
- `<destination> itinerary days`
- `<destination> 几天 行程`

For each search, fetch top 10+ note details and comments. Extract:
- Common day counts (e.g. "5天4夜", "7天6夜")
- Popular area-based day splits (e.g. "Day1-2 东京 / Day3-4 箱根 / Day5-7 京都")
- **Construct a geographic relationship map**:
  - Distance between cities/attractions (km, travel time)
  - Directional relationship (east/west/north/south)
  - Recommended transport between locations (train vs bus vs flight vs drive)
  - Comfort rating (direct train 🚄 1h vs. bus 🚌 3h vs. flight ✈️ 1h+transfers)
- Note which layouts are most recommended

**Store this layer** to a file: `xhs-research/<destination>/01_geography_days.md`

Format:
```
# <Destination> — Geography & Days Allocation

## Common Itinerary Lengths
- <N> days — most common, covers [areas]
- <M> days — rushed but doable, covers [areas]

## Geographic Map
<City A> ← <N km / N hrs by train> → <City B> (east of <City A>)
<City B> ← <N km / N hrs by bus> → <City C> (south-west of <City B>)
...

## Transport Recommendations
| Route | Options | Duration | Comfort |
|-------|---------|----------|---------|
| A → B | Shinkansen 🚄 | 1h | ★★★★★ |
| B → C | Express bus 🚌 | 3h | ★★★☆☆ |
| C → D | Flight ✈️ | 1h + transfers | ★★☆☆☆ |

## Day Allocation Patterns (from XHS)
- Pattern 1: Day 1-2 <Area A>, Day 3-4 <Area B>... [source: <xhs_url>]
- Pattern 2: Day 1-3 <Area B>, Day 4-6 <Area C>... [source: <xhs_url>]
```

**Send a progress update** after Layer 1 completes.

#### Layer 2: Activities & Food Collection (Rounds 2-3+)

Run at least 2 more search rounds with different keyword groups:

**Round 2 — Activities:**
- `<destination> 必去 景点`
- `<destination> things to do attractions`
- `<destination> 好玩 推荐`

**Round 3 — Food:**
- `<destination> 美食 推荐`
- `<destination> 必吃`
- `<destination> 餐厅`

#### Engagement threshold — use xhs-mcp-workflow (Step 1b)

After all search rounds, before enriching, apply the shared engagement threshold from xhs-mcp-workflow (Step 1b). The logic is:
```python
threshold = max(top_engagement * 0.1, 30)
```
If top post has 1K+ likes, skip posts under 100. If top has 500, skip under 50. Only enrich posts worth your time.

See `xhs-mcp-workflow/SKILL.md` → Search Workflow → Step 1b for the full implementation.

**For every search round, save a CLEANED JSON with only the fields we need. ALSO accumulate into a global list for the final `data.json` push:**

Accumulate all search results across rounds into a single Python list:
```python
all_results = []  # define at start of Step 3, grows with each round
```

After running `mcporter call xiaohongshu-mcp.search_feeds`, process the output to extract only useful fields. Save the cleaned version locally AND append to `all_results`:

```bash
mcporter call xiaohongshu-mcp.search_feeds --keyword "<keyword>" | python3 -c "
import json, sys
raw = json.load(sys.stdin)
feeds = raw.get('feeds', [])
cleaned = {
    'keyword': '<keyword>',
    'searched_at': '<timestamp>',
    'total_results': len(feeds),
    'results': [{
        'rank': i+1,
        'id': f.get('id', ''),
        'title': f.get('noteCard', {}).get('displayTitle', ''),
        'nickname': f.get('noteCard', {}).get('user', {}).get('nickname', ''),
        'likes': int(f.get('noteCard', {}).get('interactInfo', {}).get('likedCount', 0) or 0),
        'collects': int(f.get('noteCard', {}).get('interactInfo', {}).get('collectedCount', 0) or 0),
        'comments': int(f.get('noteCard', {}).get('interactInfo', {}).get('commentCount', 0) or 0),
        'shares': int(f.get('noteCard', {}).get('interactInfo', {}).get('sharedCount', 0) or 0),
        'desc': f.get('noteCard', {}).get('desc', ''),  # raw post text — full, no truncation
        'link': f'https://www.xiaohongshu.com/explore/{f.get("id", "")}'
        # NOTE: Intentionally excluded: xsecToken, userId, avatar, cover, imageList
    } for i, f in enumerate(feeds[:20])]
}
# Save per-keyword JSON locally
json.dump(cleaned, open('xhs-research/<destination>/xhs_search_results/001_<keyword>.json', 'w'),
          indent=2, ensure_ascii=False)
# Print the results as JSON so the calling script can capture them
print(json.dumps(cleaned['results'], ensure_ascii=False))
"
```

Capture the output into the `all_results` list:
```python
results_json = subprocess.check_output([...])  # or pipe the print output
all_results.extend(json.loads(results_json))
```

At the end of all search rounds, build the consolidated `data.json`:
### Enrichment step — fetch post details + comments for top posts

Before building `data.json`, enrich the top posts with full description and comments. This is **mandatory** for keeping raw data useful.

After all search rounds and deduplication:

```python
# Sort by likes, enrich ALL posts (not just top 10)
top_posts = unique_results[:len(unique_results)]  # ALL posts
unique_results.sort(key=lambda r: r['likes'], reverse=True)
top_posts = unique_results[:10]

# Fetch enriched data for each post using get_feed_detail
import subprocess, json as _json

enriched_map = {}  # link -> {desc, top_comments}

# You need id + xsec_token from the search results; look these up in the raw search data
for post in top_posts:
    fid = post['id']  # the feed_id from search
    token = post.get('xsecToken', '')  # store this during search collection!
    if not token:
        continue
    try:
        result = subprocess.run(
            ['mcporter', 'call', 'xiaohongshu-mcp.get_feed_detail',
             '--feed_id', fid, '--xsec_token', token,
             '--load_all_comments', 'true', '--limit', '10'],
            capture_output=True, text=True, timeout=30
        )
        raw = _json.loads(result.stdout)
        data = raw.get('data', {})
        note = data.get('note', {})
        comments_data = data.get('comments', {})
        comments_list = comments_data.get('list', []) if isinstance(comments_data, dict) else (comments_data if isinstance(comments_data, list) else [])
        
        enriched_map[post['link']] = {
            'desc': note.get('desc', '')[:3000],
            'has_content': bool(note.get('desc', '').strip()) and len(note.get('desc', '').strip()) >= 20,
            'top_comments': [{
                'content': c.get('content', '')[:500],
                'nickname': c.get('user_info', {}).get('nickname', ''),
                'likes': int(c.get('like_count', 0) or 0),
            } for c in comments_list[:5] if c.get('content')]
        }
        if not enriched_map[post['link']]['has_content']:
            print(f'SKIP (no desc): {post["link"]}')
        else:
            print(f'  ENRICHED: {post["link"]} — {len(enriched_map[post["link"]]["desc"])} chars, {len(enriched_map[post["link"]]["top_comments"])} comments')
    except Exception as e:
        print(f"Failed to enrich {fid}: {e}")

# Filter out posts with no content before building recommendations
usable_for_recommendation = {link for link, e in enriched_map.items() if e.get('has_content')}
print(f'Posts with content: {len(usable_for_recommendation)}/{len(enriched_map)}')

# When building 02_activities.md, 03_food.md, and 04_itinerary.md:
# ONLY use posts in usable_for_recommendation. Skip all others.
```

```python
# Then build data_json WITH enriched fields
import base64, json as _json, os, urllib.request
from datetime import datetime, timezone

data_json = {
    'keyword': '<destination>',
    'searched_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'searched_by': 'xiaohongshu-mcp',
    'total_results': len(unique_results),
    'searches_used': ['<keyword1>', '<keyword2>', ...],
    'results': [
        {
            'rank': i+1,
            'title': r['title'],
            'author': r['nickname'],
            'likes': r['likes'],
            'collects': r['collects'],
            'comments_count': r['comments'],  # renamed: comments → comments_count for clarity
            'link': r['link'],
            'desc': enriched_map.get(r['link'], {}).get('desc', ''),  # <-- full post text, MANDATORY
            'has_content': enriched_map.get(r['link'], {}).get('has_content', False),  # <-- whether we could read the desc
            'top_comments': enriched_map.get(r['link'], {}).get('top_comments', [])  # <-- top 5 comments, MANDATORY
        }
        for i, r in enumerate(unique_results)
    ]
}

# VALIDATION: warn if posts in data.json have no content
empty_content = [r['rank'] for r in data_json['results'] if not r.get('has_content')]
if empty_content:
    print(f'WARNING: {len(empty_content)} posts have no desc content (ranks: {empty_content})')
    print('These posts will be SKIPPED when building recommendations.')
```

**NOTE**: To enable enrichment, the `all_results[]` list must store `id` and `xsecToken` fields from search results:
```python
all_results.append({
    'rank': ..., 'title': ..., 'nickname': ...,
    'likes': ..., 'collects': ..., 'comments': ...,
    'desc': ..., 'link': ...,
    'id': f.get('id', ''),          # <-- needed for get_feed_detail
    'xsecToken': f.get('xsecToken', '')  # <-- needed for get_feed_detail
})
```

This gets pushed to `/xhs/YYYY-MM-DD/<destination>/data.json` at Step 6.

**Cleaned JSON fields:**
| Field | Source | Why |
|-------|--------|-----|
| `id` | feed id | Build XHS permalink `https://www.xiaohongshu.com/explore/<id>` |
| `title` | `noteCard.displayTitle` | Post title for identification |
| `nickname` | `noteCard.user.nickname` | Author name — NO userId, NO avatar |
| `likes` / `collects` / `comments` / `shares` | `interactInfo` | Engagement data for ranking |
| `desc` | `noteCard.desc` | Raw post text — full, no truncation — NO cover image |

Number sequentially (001_, 002_, ...) so they stay ordered.

For each result, fetch note details + top comments:

```bash
mcporter call xiaohongshu-mcp.get_feed_detail \
  --feed_id "<feed_id>" --xsec_token "<token>" \
  --load_all_comments true --limit 20 | python3 -c "
import json, sys
raw = json.load(sys.stdin)
data = raw.get('data', raw)
nc = data.get('noteCard', {})
ii = nc.get('interactInfo', {})
cleaned = {
    'id': data.get('id', ''),
    'title': nc.get('displayTitle', ''),
    'nickname': nc.get('user', {}).get('nickname', ''),
    'likes': int(ii.get('likedCount', 0) or 0),
    'collects': int(ii.get('collectedCount', 0) or 0),
    'comments_count': int(ii.get('commentCount', 0) or 0),
    'desc': nc.get('desc', ''),  # raw post text
    'link': f'https://www.xiaohongshu.com/explore/{data.get("id", "")}',
    'comments': [{
        'content': c.get('content', ''),
        'nickname': c.get('user_info', {}).get('nickname', ''),
        'likes': int(c.get('like_count', 0) or 0),
        'time': c.get('time', ''),
        # NOTE: Intentionally excluded: userId, avatar, cover, imageList
    } for c in data.get('comments', [])[:20]],
    'comment_summary': 'Comments range from helpful tips to personal experiences. '
        'Top comments mention practical advice, booking tips, and local recommendations.'
}
json.dump(cleaned, open('xhs-research/<destination>/xhs_search_results/detail_<feed_id>.json', 'w'),
          indent=2, ensure_ascii=False)
"
```

**Detail JSON fields:**
| Field | Source | Why |
|-------|--------|-----|
| `id` | feed id | Unique identifier |
| `title` | `displayTitle` | Post title |
| `nickname` | `user.nickname` | Author name — NO userId, NO avatar |
| `likes` / `collects` / `comments_count` | `interactInfo` | Engagement data |
| `desc` | `noteCard.desc` | Full raw post text — NO cover images |
| `comments[].content` | comment content | Raw comment text for analysis |
| `comments[].nickname` | comment user_info | Commenter name — NO userId, NO avatar |
| `comments[].likes` | comment like_count | Comment engagement |

Rank by engagement (likes + saves). Extract:
- Name, description, location area
- XHS permalink (`https://www.xiaohongshu.com/explore/<feed_id>`)
- Like/save counts
- Any pro tips from comments
- Specific quotes from the post or comments (short, ≤25 words, attributed)
- Estimated travel time from city center / nearby attractions

**Store to files:**
- `xhs-research/<destination>/02_activities.md`
- `xhs-research/<destination>/03_food.md`

**02_activities.md format (EVERY entry must have XHS permalink + pro tip + evidence quote from desc/comments + sentiment):**

⚠️ **Only include posts where `get_feed_detail` returned non-empty `desc`.** If you couldn't read the post content, you CANNOT include it here. No exceptions.
```
# <Destination> — Activities

## Top Picks
1. **<name>** — <description> | 👍<likes> ⭐<saves> | <area>
   - Pro tip: <from comments>
   - 💡 Booking: <ticket note if applicable>
   - Quote: "<short quote from XHS post or comment>"
   - [XHS post](https://www.xiaohongshu.com/explore/<feed_id>)

## Quick-Reference Table
| Activity | Area | Distance | Source |
|----------|------|----------|--------|
| <name> | <area> | <km from center> | [XHS](<url>) |
```

**03_food.md format (EVERY entry must have XHS permalink + sentiment + quote from desc/comments + price):**

⚠️ **Only include posts where `get_feed_detail` returned non-empty `desc`.** If you couldn't read the post content, you CANNOT include it here. No exceptions.
```
# <Destination> — Food Recommendations

## Top Picks
1. **<name>** — <cuisine> | 👍<likes> ⭐<saves> | <area>
   - Quote: "<short quote from XHS, in original language>"
   - Price: $/$$/$$
   - [XHS post](<url>)

## Quick-Reference Table
| Restaurant / Item | Type | Price | Sentiment | XHS Mentions |
|---|---|---|---|---|
| <name> | <type> | $ | Positive | [XHS](<url>) |

## Pro Tips from XHS
- <tip 1>
- <tip 2>
```

**Send a progress update** after each round.

#### Hotels (skip in XHS — use hotel-research skill instead)

Do NOT search for hotels on XHS. The hotel-research skill handles accommodations.

**Send a progress update** after XHS research is fully complete.

### Step 4: Practical Web Research (Phase 2 — added 2026-05-19)

After XHS research, run targeted web searches for practical trip info that XHS won't cover well. Use `web_search` for each category:

| Category | Search Query | Why |
|----------|-------------|-----|
| **Entry requirements** | `<destination> visa requirements <nationality>` | Passport/visa rules, fees |
| **Best time to visit** | `<destination> best time to visit weather <month>` | Seasons, festivals, weather |
| **Safety** | `<destination> safety tips scams` | Safe areas, common scams, advisories |
| **Local transport** | `<destination> metro bus app` | How to get around (DiDi/Uber equivalents, transit cards) |
| **Practical info** | `<destination> currency tipping power outlets` | Money, etiquette, plugs |

Search up to 3 categories in a single `web_search` call (combine related ones). Prioritize the categories most relevant to the destination (e.g. visa info matters for China, less for Schengen).

**Send a progress update** after practical research.

### Step 5: Search hotels

Use the `hotel-research` skill:
- Extract guest count from interview
- Use browser to search Google Hotels/Travel for the destination
- Extract hotel name, price, star rating, review count
- For multi-city trips, search hotels per city
- Consider **transport convenience** — how far is the hotel from key attractions / transit hubs
- Hotels only, no Airbnb

**Send a progress update** after hotel search.

### Step 6: Push ALL data to deep-research-reports

After every significant research batch. Data goes to `darinyu/deep-research-reports`, NOT openclaw-config.

**TWO locations — push BOTH:**

**Location A — RAW DATA** → `/xhs/YYYY-MM-DD/<destination>/`
- What: Single `data.json` with ALL search results consolidated (keyword, searched_at, searches_used[], results[{rank, title, author, likes, collects, comments, link}])
- Purpose: Backbone raw data. Reusable by future research.
- Organized by date, then keyword/destination.

**Location B — PROCESSED DATA** → `/xhs-research/<destination>/`
- What: `01_geography_days.md`, `02_activities.md`, `03_food.md`, `04_itinerary.md`, `xhs_search_results/*.json`
- Purpose: Final plans, itineraries, recommendations.

**Hard rules:**
- `/xhs/` NEVER contains processed reports — only raw `data.json`
- `/xhs-research/` NEVER replaces `/xhs/` — always push BOTH
- Push raw data BEFORE or WITH processed data, never after

**Python commit script (preferred):**
```python
import base64, json, os, urllib.request
from datetime import datetime, timezone

# Get GH token
with open(os.path.expanduser('~/.config/gh/hosts.yml')) as f:
    for line in f:
        if 'oauth_token:' in line:
            token = line.split(':', 1)[1].strip()
            break

def gh_put(path, content, message):
    # Check if file exists (get SHA for update)
    req = urllib.request.Request(f'https://api.github.com/repos/darinyu/deep-research-reports/contents/{path}')
    req.add_header('Authorization', f'Bearer {token}')
    sha = None
    try:
        existing = json.loads(urllib.request.urlopen(req).read())
        sha = existing['sha']
    except:
        pass
    body = {'message': message, 'content': base64.b64encode(content.encode()).decode(), 'branch': 'main'}
    if sha: body['sha'] = sha
    req2 = urllib.request.Request(f'https://api.github.com/repos/darinyu/deep-research-reports/contents/{path}',
                                   data=json.dumps(body).encode(), method='PUT')
    req2.add_header('Authorization', f'Bearer {token}')
    req2.add_header('Content-Type', 'application/json')
    urllib.request.urlopen(req2)

# Push raw data to /xhs/YYYY-MM-DD/<destination>/
# IMPORTANT: data.json MUST include desc + top_comments for each post.
# Pre-enrich top posts using get_feed_detail (see enrichment section above).
date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
data_json = {
    'keyword': '<destination>',
    'searched_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'searched_by': 'xiaohongshu-mcp',
    'total_results': <N>,
    'searches_used': ['<keyword1>', '<keyword2>', '<keyword3>'],
    'results': [{
        'rank': r['rank'], 'title': r['title'], 'author': r['nickname'],
        'likes': r['likes'], 'collects': r['collects'], 'comments_count': r['comments'],
        'link': r['link'],
        'desc': enriched_map.get(r['link'], {}).get('desc', ''),  # MANDATORY: full post text
        'has_content': enriched_map.get(r['link'], {}).get('has_content', False),  # MANDATORY: whether desc was retrievable
        'top_comments': enriched_map.get(r['link'], {}).get('top_comments', [])  # MANDATORY: top 5 comments
    } for r in all_results]
}

# Run validation before pushing
empty_content = [r['rank'] for r in data_json['results'] if not r.get('has_content')]
if empty_content:
    print(f'WARNING: {len(empty_content)} posts have no desc — will be skipped in recommendations')
    print(f'  Ranks without content: {empty_content}')
gh_put(f'xhs/{date_str}/<destination>/data.json', json.dumps(data_json, indent=2, ensure_ascii=False),
       'Add raw XHS search data for <destination>')

# Push processed markdown files to /xhs-research/<destination>/
with open('xhs-research/<destination>/01_geography_days.md') as f:
    gh_put(f'xhs-research/<destination>/01_geography_days.md', f.read(), 'Add geography & transport')
with open('xhs-research/<destination>/02_activities.md') as f:
    gh_put(f'xhs-research/<destination>/02_activities.md', f.read(), 'Add activities')
with open('xhs-research/<destination>/03_food.md') as f:
    gh_put(f'xhs-research/<destination>/03_food.md', f.read(), 'Add food recommendations')
with open('xhs-research/<destination>/04_itinerary.md') as f:
    gh_put(f'xhs-research/<destination>/04_itinerary.md', f.read(), 'Add final itinerary')
```

**Bash commit script (alternative):**
```bash
REPO_URL="https://github.com/darinyu/deep-research-reports.git"
CLONE_DIR="/tmp/deep-research-reports"
if [ -d "$CLONE_DIR" ]; then
  cd "$CLONE_DIR" && git pull origin main
else
  git clone "$REPO_URL" "$CLONE_DIR"
fi

DATE=$(date -u +%Y-%m-%d)
# Push raw data
mkdir -p "$CLONE_DIR/xhs/$DATE/<destination>"
cp data.json "$CLONE_DIR/xhs/$DATE/<destination>/"
# Push processed data
mkdir -p "$CLONE_DIR/xhs-research/<destination>/xhs_search_results"
cp 01_*.md 02_*.md 03_*.md 04_*.md "$CLONE_DIR/xhs-research/<destination>/"
cp xhs_search_results/*.json "$CLONE_DIR/xhs-research/<destination>/xhs_search_results/"

cd "$CLONE_DIR"
git add xhs/ xhs-research/
git commit -m "xhs-trip-plan: <destination> — raw data + processed report"
git push origin main
```

**Send a progress update** after each commit.

### Step 7: Iterate on user feedback

After presenting the itinerary, ask:
- "Does this look good or do you want to refine anything?"
- If user wants changes: check if current data is sufficient, or run additional XHS searches to fill gaps
- Persist refinements back to the data files and re-commit
- Repeat until user is satisfied

### Step 8: Build ADHD-friendly itinerary with daily schedule

**STANDING RULE — Always minimize hotel moves:** This is a hard-coded user preference, never ask about it.
- Per destination/city: 1 hotel only. If visiting 2 cities, 1 hotel in each. No mid-city hotel switches.
- Plan all activities from 1 base hotel per city. Group by geographic area — no criss-crossing.
- For multi-country trips (e.g. Italy + Greece): 1 country/city = 1 hotel. The only moves are between cities (flight/train).

**Timing rule:** Max 3-4 activities per day. Include realistic timing buffers between activities. Don't over-schedule.

**Language rule:** Report/summary in user's chosen language. Keep all restaurant names, hotel names, and location names in their original language (e.g. "Maguro Brothers" stays "Maguro Brothers", 巴黎 stays 巴黎).

#### ⚠️ RECOMMENDATION SOURCE RULE: desc + comments only, never title/likes alone

1. **Every** activity, restaurant, or tip in the itinerary MUST trace back to enriched post content (non-empty `desc`).
2. **Filter first**: Start with `usable_for_recommendation` (posts with non-empty desc). Discard all others.
3. **Read, extract, cite**: For each usable post, read the full desc + top 5 comments, then:
   - Extract specific activities mentioned (with context — what makes them good)
   - Extract specific restaurants/foods mentioned (with specific dish names)
   - Note warnings/negative sentiment ("overrated", "tourist trap", "skip this")
   - Extract practical tips ("go early to avoid crowds", "book 2 weeks in advance")
   - Pull a short evidence quote (≤25 words, original language, from desc or comments)
4. **Build the schedule**: Group extracted activities by geography and time of day. Each entry needs:
   - Activity/restaurant name (from post content)
   - Description/sentiment (derived from reading the post, not from title)
   - Evidence quote (directly from desc or comments)
   - XHS permalink
   - Pro tips from comments
5. **No empty-content entries**: If you couldn't read a post's content, you cannot list its recommendations. Period.

Format for quick scanning. **Bold** = key info. Keep it tight.

```
*<Destination> — <days> days*
*Trip style:* <self-guided / guided>   *Transport:* <transport mode>

*Priority:* <method>       *Budget:* <tier>      *Travellers:* <who>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Geography Map*
<City A> 🚄 1h → <City B> (east)
<City B> 🚌 2.5h → <City C> (south)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

***Day 1*** | <theme/location — geographically grouped>
  **AM** · <activity>
    ↳ <sub-spots> | <sub-spots>
    💡 Booking: <booking tip>
  **Lunch** · <restaurant> | <link> | ~€<cost>/pp
  **PM** · <activity> | <link>
    ↳ <sub-spots>
    💡 Booking: <booking tip>
  **Dinner** · <restaurant> | ~€<cost>/pp
  **Evening** · <evening activity>
  ───
  🚶 Transport: <route from hotel> (<mode>, <min>)
  💰 Day cost: ~€<total>/pp
  📍 Note: <geographic coherence note>

***Day 2*** | <theme/location>
  **AM** · <activity>
    ↳ <sub-spots>
  **Lunch** · <restaurant> | ~€<cost>/pp
  **PM** · <activity> | <link>
    💡 Booking: <booking tip>
  **Dinner** · <restaurant> | ~€<cost>/pp
  ───
  🚶 Transport: <route from hotel>
  💰 Day cost: ~€<total>/pp

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*Transport summary*
  * <City A> → <City B>: 🚄 Shinkansen 1h — comfortable ⭐⭐⭐⭐⭐
  * <City B> → <City C>: 🚌 Express bus 3h — less comfy ⭐⭐⭐

*Hotels*
  * <name> — <price>/night ⭐<rating> | <booking link> | 🚶 <min> to train station

*Pro tips from XHS*
  * <tip 1> | <source>
  * <tip 2> | <source>
```

**Format rules (upgraded):**
- **Time blocks**: Organize each day into `**AM**`, `**Lunch**`, `**PM**`, `**Dinner**`, `**Evening**`
- **Sub-activity hierarchy**: Use `↳` indented lines under main activities for sub-spots (e.g. under Walking Tour: `↳ Cathedral | Plaça Reial | Las Ramblas`)
- **Booking tips**: Add `💡 Booking:` line for activities that need advance booking ("sells out fast", "book online ~€15")
- **Daily transport**: `🚶 Transport:` line showing how to get from hotel to first activity
- **Daily cost**: `💰 Day cost:` line with estimated per-person total
- **Geographic note**: `📍 Note:` about walkability or travel coordination
- **Bold** for times, day numbers, section headers
- **One line per thing**. No paragraphs.
- **Emoji** for categories (🎯 activities, 🍜 food, 🏨 hotel, 🚄 transport)
- **XHS permalink** with each recommendation
- **Include transport mode + comfort** per leg
- **Avoid walls of text**

---

### GitHub Report Formatting Rules (for 04_itinerary.md and companion files)

The GitHub report is the full authoritative output. It MUST use **proper Markdown syntax** throughout:

1. **Bullet lists** use `- ` with proper blank line before/after — never indented paragraph-style items
2. **Tables** use proper pipe syntax with header separators (`|---|---|`)
3. **Headers** use `###` hierarchy, never raw bold text as headings
4. **Every recommendation MUST have an XHS source link** — no recommendation without attribution
   - Format: `[XHS post](https://www.xiaohongshu.com/explore/<feed_id>)` or `[XHS](<url>)` inline
5. **Include evidence quotes from XHS** for top picks — short quote (≤25 words) in original language
6. **Separate sections clearly** with `---` horizontal rules between major content blocks
7. **Appendix A: All Posts Analyzed** — table of every XHS post used with title, 👍, ⭐, link
8. **Appendix B: Web Research Sources** — URLs for practical research (transit, weather, safety, etc.)

**Do NOT use:**
- Raw HTML tags
- Inconsistent indentation
- Single-item bullet lists that could be inline text
- Loose text without structure

#### Budget Breakdown (inline in 04_itinerary.md)

After collecting activity/food/hotel costs, compute and include:

```
Total Budget: $X (N days)
Daily Average: $X

Breakdown:
- Accommodation: $X (35%) — $X/night
- Food: $X (25%) — $X/day
- Activities: $X (25%) — $X/day
- Transportation: $X (10%) — $X/day
- Miscellaneous: $X (5%)
```

No script needed — agent computes this inline from collected cost data.

#### Pre-Trip Timeline (inline in 04_itinerary.md)

Generate a timeline relative to departure date:

```
2 MONTH BEFORE:
  - Book flights & hotels
  - Check passport/visa requirements

1 MONTH BEFORE:
  - Book popular attraction tickets (sells out fast)
  - Notify bank of travel

2 WEEKS BEFORE:
  - Confirm all reservations
  - Check weather forecast
  - Download offline maps & transit apps

1 WEEK BEFORE:
  - Pack luggage (see checklist below)
  - Buy travel insurance
  - Arrange airport transfer

DAY BEFORE:
  - Re-check flight time & gate
  - Print/download documents
  - Set alarms & early sleep
```

Agent generates inline from departure date collected in interview.

#### Packing Checklist (inline in 04_itinerary.md)

Generate a simple climate/activity-aware checklist:

```
Essentials: passport, visa printout, phone, charger, power adapter
Clothing: [based on destination climate + season]
Footwear: [based on activities — hiking boots, sandals, walking shoes]
Tech: camera, power bank, earbuds
Health: [medications, first-aid, sunscreen, insect repellent]
Documents: booking confirmations, insurance, itineraries
Activity-specific: swimsuit, hiking gear, umbrella, etc.
```

Agent generates inline — context-aware based on destination climate, season, and user's listed activities.

---

### Step 9: Share GitHub report links (Slack = summary only)

In Slack thread, only post:
- rationale (1 line)
- pro tips (3–5 bullets)
- activities preview (by location)
- food preview (top clusters)
- hotel preview (2–3 options)
- GitHub report link

Full day-by-day schedule + appendix (posts + comment quotes) goes in the GitHub report.

```
Full report: <url>
```

Apply display conventions from xhs-mcp-workflow:
- :heart: for likes, :star: for saves
- Bold for emphasis
- Run through `scripts/slack_format.sh` before Slack

## Data Persistence Rules

### Two GitHub locations — NEVER confuse them

**Location 1 — RAW DATA** → `xhs/YYYY-MM-DD/<destination>/`
- A single `data.json` with ALL search results consolidated
- Organized by date, then destination keyword
- Purpose: Backbone, raw data store. Reusable by other research.
- **NEVER** put processed reports (01_*.md, 04_*.md) here
- Structure:
  ```
  xhs/
  └── YYYY-MM-DD/
      └── <destination>/
          ├── data.json       # Consolidated raw XHS results
          └── report.md       # Optional: auto-generated summary from raw data
  ```

**Location 2 — PROCESSED DATA** → `xhs-research/<destination>/`
- Final plans, itineraries, recommendations
- Structure:
  ```
  xhs-research/
  └── <destination>/
      ├── 01_geography_days.md     # Geography map, days allocation, transport
      ├── 02_activities.md          # Activities with XHS links
      ├── 03_food.md                # Food recommendations with XHS links
      ├── 04_itinerary.md           # Final itinerary
      ├── xhs_search_results/       # Raw XHS search JSON (per keyword)
      │   ├── 001_<keyword>.json
      │   └── ...
      └── README.md                 # Summary of all findings
  ```

**Hard rules:**
- `/xhs/` is ONLY for raw data. Never push markdown reports there.
- `/xhs-research/` is ONLY for processed data. Never push raw data.json there.
- Always push BOTH locations. Raw data first, then processed.
- Search `/xhs/` BEFORE searching, to reuse existing raw data.

## Transport Consideration

For every route between locations, always note:
- **Mode**: train (Shinkansen / express / local), bus, flight, ferry, drive
- **Duration**: actual travel time (not just distance)
- **Comfort**: comfort level with reasoning (direct vs transfers, luggage-friendly, crowding)
- **Cost**: approximate ticket price
- **Recommendation**: which option balances time/comfort/cost best for the trip profile
