---
name: xhs-trip-planner
description: Vacation trip planning using Xiaohongshu (小红书/XHS/Rednote) research. Interviews the user about their trip, then uses the xhs-mcp-workflow skill to search XHS for activities, food recommendations, and accommodation options. Presents a structured itinerary ranked by user-chosen prioritization method (price, comfort, food focus, etc.). Use when the user asks to plan a vacation, trip, holiday, travel itinerary, or needs recommendations for things to do, places to eat, or where to stay at a destination.
---

# XHS Trip Planner

This skill uses `xhs-mcp-workflow` to research trip destinations on Xiaohongshu and plan a complete itinerary.

## Workflow

### Step 1: Interview the user

Gather the following information systematically:

| Question | Purpose | Example |
|---|---|---|
| **Destination** | Where are you going? | Honolulu, Tokyo, Paris |
| **Dates / Duration** | How long is the trip? | 5 days, June 1-7 |
| **Travelers** | Who's going? | Solo, couple, family with kids |
| **Budget tier** | Budget level? | Budget, mid-range, luxury |
| **Interests** | What matters most? | Food, hiking, shopping, culture, beach |
| **Dietary needs** | Any food restrictions? | Vegetarian, halal, no restrictions |
| **Priority method** | HOW to rank recommendations? | Price, comfort, food quality, convenience, instagram-worthy |

**Critical:** Always ask about **prioritization method** — how should recommendations be ranked? Options:
- *Price* — cheapest options first
- *Comfort* — highest-rated, most comfortable
- *Food quality* — best food recommendations prioritized
- *Convenience* — closest to hotel, easiest logistics
- *Instagram-worthy* — best photo spots
- *Balanced* — mix of everything

### Step 2: Research each category on XHS

Use `xhs-mcp-workflow` to search Xiaohongshu for each category:

1. **Activities** — Search keywords like `"<destination> things to do"`, `"<destination> 攻略"`, `"<destination> must visit"`, `"<destination> 必去"`
2. **Food** — Search keywords like `"<destination> 美食"`, `"<destination> restaurant"`, `"<destination> 必吃"`
3. **Stay** — Search keywords like `"<destination> hotel"`, `"<destination> 酒店"`, `"<destination> where to stay"`

For each search, follow the full xhs-mcp-workflow pipeline:
- Health check → Login guard → Search → Fetch details + comments → Rank by :heart:+:star:
- Apply user's prioritization method when ranking (e.g. if price-focused, weight comments about cost higher)
- Push each category's report to GitHub

### Step 3: Send progress updates

Periodic Slack updates during research:
- "Researching activities in <destination>..."
- "Food research complete — found top 5 restaurants"
- "Finding accommodation..."
- "Building your itinerary..."

### Step 4: Present the itinerary

Organize into a structured travel plan:

```
*<Destination> Trip Plan for <dates>*

*Prioritization:* <method>

*Day 1 | <date>*
  🎯 Activities: <top picks with XHS links>
  🍜 Food: <top restaurant picks with XHS links>
  🌙 Evening: <evening recommendations>

*Day 2 | <date>*
  ...

*Accommodation Recommendations*
  - <option 1> | XHS link
  - <option 2> | XHS link

*Tips from XHS users*
  - <user insights from comments>
```

Apply all display conventions from `xhs-mcp-workflow`:
- `:heart:` for likes, `:star:` for saves
- Bold for emphasis
- Include XHS permalinks
- Roll through `scripts/slack_format.sh` before Slack

### Step 5: Share GitHub report links

After presenting the itinerary, share links to the GitHub reports so the user can reference them later:
```
Full research reports saved to GitHub:
- Activities: <url>
- Food: <url>
- Stay: <url>
```
