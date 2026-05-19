---
name: xhs-trip-planner
description: Vacation trip planning using Xiaohongshu (小红书/XHS/Rednote) research. Covers the full pipeline: interviews user about their trip, checks existing GitHub XHS search reports from the past week, uses xhs-mcp-workflow to research activities/food on XHS, uses hotel-research skill for accommodations (hotels only, no Airbnb). Presents ADHD-friendly day-by-day itineraries with bold syntax. Use when user asks to: plan a vacation, plan a trip, plan a holiday, plan an itinerary, build a travel plan, what to do in [city], things to do in [country], where to eat in [city], where to stay in [city], travel recommendations, vacation planning, sightseeing, travel guide, 行程规划, 旅游攻略, 旅行计划, needs recommendations for things to do, places to eat, or where to stay. Also handles multi-city/country trips, road trips, honeymoon planning, family vacation planning, solo travel planning.
---

# XHS Trip Planner

This skill uses `xhs-mcp-workflow` to research destinations on Xiaohongshu, and `hotel-research` skill for hotels via Google Maps/Travel. No Airbnb.

## Workflow

### Step 1: Interview the user (MCQ format only)

Gather trip info. Ask ONE question at a time. Use MCQ for prioritization.

**Questions to ask (adapt to natural conversation):**

1. *Where* are you going? (If multi-city, list them all)
2. *How long*? (dates or number of days)
3. *Who's going*? (solo, couple, family with kids, group)
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

### Step 3: Research on XHS (if no existing report)

For categories without existing reports, use `xhs-mcp-workflow`:

1. **Activities** — Search: `<destination> 攻略`, `<destination> things to do`, `<destination> 必去`
2. **Food** — Search: `<destination> 美食`, `<destination> food`, `<destination> 必吃`
3. **Hotels** (skip this — use hotel-research instead)

Follow full pipeline: Health check → Login guard → Search → Fetch details + comments → Rank by :heart:+:star:
Push each category's report to GitHub.

### Step 4: Search hotels

Use the `hotel-research` skill:
- Extract guest count from interview
- Use browser to search Google Hotels/Travel for the destination
- Extract hotel name, price, star rating, review count
- Hotels only, no Airbnb

### Step 5: Build ADHD-friendly itinerary

Format for quick scanning. **Bold** = key info. Keep it tight.

```
*<Destination> — <days> days*

*Priority:* <method>       *Budget:* <tier>      *Travellers:* <who>

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

*Hotels*
  * <name> — <price>/night ⭐<rating> | <booking link>

*Pro tips from XHS*
  * <tip 1>
  * <tip 2>
```

Key rules:
- **Bold** for times (AM/PM/Lunch/Dinner), day numbers, section headers
- One line per thing. No paragraphs.
- Emoji for categories (🎯 activities, 🍜 food, 🏨 hotel)
- XHS permalink with each recommendation
- Avoid walls of text

### Step 6: Share GitHub report links

```
Full research: <url>
```

Apply display conventions from xhs-mcp-workflow:
- :heart: for likes, :star: for saves
- Bold for emphasis
- Run through `scripts/slack_format.sh` before Slack
