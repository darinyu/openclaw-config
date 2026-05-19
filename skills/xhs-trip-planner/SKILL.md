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

### Step 1: Interview the user (MCQ format only)

Gather trip info. Ask ONE question at a time. Use MCQ for prioritization.

**Questions to ask (adapt to natural conversation):**

1. *Where* are you going? (If multi-city, list them all — e.g. Tokyo, Osaka, Kyoto)
2. *How long*? (dates or number of days)
3. *Who's going*? (solo, couple, family with kids, group — note any mobility concerns)
4. *Budget tier*? (budget / mid-range / luxury)
5. *Dietary needs*? (none / vegetarian / halal / allergies)
6. *Main interests*? (food / nature / culture / shopping / hiking / photography / mix)

**Then ask prioritization (MCQ ONLY):**

> How should I prioritize recommendations?
> 1️⃣ *Cheapest* — budget-friendly options first
> 2️⃣ *Highest-rated* — best reviews, most comfortable
> 3️⃣ *Foodie* — best food spots prioritized
> 4️⃣ *Convenient* — closest to center / easy logistics
> 5️⃣ *Instagram* — most photogenic spots
> 6️⃣ *Balanced* — a mix of everything

Pick one number. No free-text.

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

For each result, fetch note details + top comments. Rank by engagement (likes + saves). Extract:
- Name, description, location area
- XHS permalink
- Like/save counts
- Any pro tips from comments
- Estimated travel time from city center / nearby attractions

**Store to files:**
- `xhs-research/<destination>/02_activities.md`
- `xhs-research/<destination>/03_food.md`

Format:
```
# <Destination> — Activities

| Activity | Area | Distance | Source |
|----------|------|----------|--------|
| <name> | <area> | <km from center / nearby landmark> | [XHS](<url>) |

## Top Picks
1. **<name>** — <description> | 👍<likes> ⭐<saves> | <area>
   - Pro tip: <from comments>
   - [XHS post](<url>)
```

**Send a progress update** after each round.

#### Hotels (skip in XHS — use hotel-research skill instead)

Do NOT search for hotels on XHS. The hotel-research skill handles accommodations.

**Send a progress update** after XHS research is fully complete.

### Step 4: Search hotels

Use the `hotel-research` skill:
- Extract guest count from interview
- Use browser to search Google Hotels/Travel for the destination
- Extract hotel name, price, star rating, review count
- For multi-city trips, search hotels per city
- Consider **transport convenience** — how far is the hotel from key attractions / transit hubs
- Hotels only, no Airbnb

**Send a progress update** after hotel search.

### Step 5: Store all data and commit to GitHub

After every significant research batch:

```bash
# Create/update data files in workspace
mkdir -p xhs-research/<destination>
# All files: 01_geography_days.md, 02_activities.md, 03_food.md

# Commit to GitHub
cd /data/.openclaw/workspace
git add xhs-research/<destination>/
git commit -m "xhs-trip-plan: <destination> — added <round description>"
git push origin main
```

GitHub repo: `darinyu/deep-research-reports`
Path in workspace: `xhs-research/<destination>/`

**Send a progress update** after each commit.

### Step 6: Iterate on user feedback

After presenting the itinerary, ask:
- "Does this look good or do you want to refine anything?"
- If user wants changes: check if current data is sufficient, or run additional XHS searches to fill gaps
- Persist refinements back to the data files and re-commit
- Repeat until user is satisfied

### Step 7: Build ADHD-friendly itinerary

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

***Day 1*** | <theme/location>
  **AM** · <activity> | <link>
  **Lunch** · <restaurant> | <link>
  **PM** · <activity>
  **Dinner** · <restaurant> | <link>

***Day 2*** | <theme/location>
  **AM** · <activity>
  **Lunch** · <restaurant>
  **PM** · <activity>
  **Dinner** · <restaurant>

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

Key rules:
- **Bold** for times (AM/PM/Lunch/Dinner), day numbers, section headers
- One line per thing. No paragraphs.
- Emoji for categories (🎯 activities, 🍜 food, 🏨 hotel, 🚄 transport)
- XHS permalink with each recommendation
- Include transport mode + comfort per leg
- Avoid walls of text

### Step 8: Share GitHub report links

```
Full research: <url>
```

Apply display conventions from xhs-mcp-workflow:
- :heart: for likes, :star: for saves
- Bold for emphasis
- Run through `scripts/slack_format.sh` before Slack

## Data Persistence Rules

All research artifacts go in `xhs-research/<destination>/`:

```
xhs-research/<destination>/
├── 01_geography_days.md     # Layer 1: geography map, days allocation, transport
├── 02_activities.md          # Layer 2: activities with XHS links
├── 03_food.md                # Layer 3: food recommendations with XHS links
├── 04_itinerary.md           # Final itinerary
├── xhs_search_results/       # Raw XHS search output (pushed by xhs-mcp-workflow)
│   ├── 001_<keyword>.json
│   └── ...
└── README.md                 # Summary of all findings
```

## Transport Consideration

For every route between locations, always note:
- **Mode**: train (Shinkansen / express / local), bus, flight, ferry, drive
- **Duration**: actual travel time (not just distance)
- **Comfort**: comfort level with reasoning (direct vs transfers, luggage-friendly, crowding)
- **Cost**: approximate ticket price
- **Recommendation**: which option balances time/comfort/cost best for the trip profile
