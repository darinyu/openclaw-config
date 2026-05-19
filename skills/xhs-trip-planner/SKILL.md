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
10. *Hotel moves* — ONE hotel or OK switching? (MCQ)
    > 1️⃣ *One hotel preferred* — minimize moves
    > 2️⃣ *OK switching* — flexibility for better experience

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

### Step 6: Store all data and commit to deep-research-reports

After every significant research batch. Data goes to `darinyu/deep-research-reports`, NOT openclaw-config.

```bash
# Clone/pull the reports repo
REPO_URL="https://github.com/darinyu/deep-research-reports.git"
CLONE_DIR="/tmp/deep-research-reports"
if [ -d "$CLONE_DIR" ]; then
  cd "$CLONE_DIR" && git pull origin main
else
  git clone "$REPO_URL" "$CLONE_DIR"
fi

# Create/update data files
DEST="$CLONE_DIR/xhs-research/<destination>"
mkdir -p "$DEST/01_geography_days.md"  # remove the filename part
# Actually:
mkdir -p "$DEST"
cp <data_file> "$DEST/"

# Commit and push
cd "$CLONE_DIR"
git add xhs-research/
git commit -m "xhs-trip-plan: <destination> — added <round description>"
git push origin main
```

Or use the Python helper:
```bash
python3 /data/.openclaw/shared-skills/scripts/push_xhs_report.py \
  --keyword "xhs-research/<destination>/04_itinerary" \
  --file 04_itinerary.md
```

GitHub repo: `darinyu/deep-research-reports`
Path: `xhs-research/<destination>/`

**Send a progress update** after each commit.

### Step 7: Iterate on user feedback

After presenting the itinerary, ask:
- "Does this look good or do you want to refine anything?"
- If user wants changes: check if current data is sufficient, or run additional XHS searches to fill gaps
- Persist refinements back to the data files and re-commit
- Repeat until user is satisfied

### Step 8: Build ADHD-friendly itinerary with daily schedule

**Hotel moves rule:** If user selected "one hotel preferred", design the itinerary so all days are reachable from a single base hotel. Activities on the same side of the destination go on the same day. **Hard rule: no criss-crossing the city** — group activities by geographic area within each day.

**Timing rule:** Max 3-4 activities per day. Include realistic timing buffers between activities. Don't over-schedule.

**Language rule:** Report/summary in user's chosen language. Keep all restaurant names, hotel names, and location names in their original language (e.g. "Maguro Brothers" stays "Maguro Brothers", 巴黎 stays 巴黎).

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

#### Budget Breakdown (inline in final report)

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

#### Pre-Trip Timeline (inline in final report)

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

#### Packing Checklist (inline in final report)

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
