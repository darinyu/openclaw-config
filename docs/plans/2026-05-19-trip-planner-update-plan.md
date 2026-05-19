# XHS Trip Planner vs Travel-Planner (mcpmarket) — Comparison & Update Plan

## Summary of the Reference Skill

The travel-planner skill uses:
- **Local JSON files** (`~/.claude/travel_planner/preferences.json`, `trips.json`) — NO MCP servers, NO external DB, zero extra infra
- **Two Python scripts** (`travel_db.py` for data CRUD, `plan_generator.py` for output generation)
- **Web search** for destination research

It excels at: progressive preference learning, structured trip tracking, budget math, packing checklists, cultural etiquette, pre-trip timelines, and post-trip archiving.

---

## Comparison: What They Have vs What We Have

| Feature | travel-planner (them) | xhs-trip-planner (us) |
|---------|---------------------|----------------------|
| **User preference storage** | ✅ JSON file, persistent across trips | ❌ None — each trip starts from scratch |
| **Preference collection** | ✅ 6 categories (style, budget, diet, interests, pace, past trips) | ✅ Basic (budget, diet, interests, who) — no pace, no style |
| **Destination research** | Web search (generic) | XHS search (targeted, authentic) |
| **Practical research (visa, weather, safety, transport, currency)** | ✅ 10 categories, systematically searched | ❌ Not present |
| **Geography & transport map** | ❌ Not present | ✅ Added last round — transport mode, comfort |
| **Activities/food** | ✅ Per-day breakdown | ✅ XHS-sourced, ranked by engagement |
| **Hotel search** | ✅ Manual recommendation | ✅ Google Hotels via skill |
| **Daily itinerary format** | ✅ Structured with cost, booking notes, geo grouping, timing buffers, transport, sub-activity hierarchy | ❌ Basic text breakdown |
| **Budget breakdown** | ✅ Detailed %-based by category | ❌ Not present |
| **Packing checklist** | ✅ Destination/climate-aware | ❌ Not present |
| **Cultural do's & don'ts** | ✅ Country-specific guide | ❌ Not present |
| **Pre-trip timeline** | ✅ 2-month → day-before checklist | ❌ Not present |
| **Trip tracking** | ✅ Budget spent vs remaining | ❌ Not present |
| **Post-trip archiving** | ✅ Move trip to past, update preferences | ❌ Not present |
| **Progress updates** | ❌ Not present | ✅ Every 2 min rule |
| **Layered XHS research** | ❌ Not present | ✅ 3+ rounds, geography, activities, food |
| **GitHub persistence** | ❌ Local only | ✅ Committed to deep-research-reports |
| **Source links** | ❌ Not present | ✅ XHS permalinks on everything |
| **ADHD-friendly format** | ❌ Walls of text | ✅ Bold syntax, one-line-per-thing |
| **Transport comfort rating** | ❌ Not present | ✅ Per-leg mode/duration/comfort |
| **Pro tip extraction from comments** | ❌ Not present | ✅ XHS comment mining |
| **Language preference** | ❌ Not present | ✅ Chinese / English / Mixed |

---

## Proposed Update Plan

**Guiding constraint: NO new MCP servers, NO new databases.** Everything we add uses:
- Local JSON files (just like their approach)
- Python scripts if needed (our own, no external packages)
- Existing tools (web fetch, XHS search, hotel-research)

---

### Phase 1: Preference System (JSON file, zero deps)

Replace the current Step 1 interview with a **preference file at `~/.openclaw/data/travel_preferences.json`**:

```json
{
  "profile": {
    "name": "",
    "travel_style": "adventurous | relaxed | balanced",
    "budget_level": "budget | mid-range | luxury",
    "pace": "relaxed | moderate | packed",
    "accommodation": "hotel | boutique | resort",
    "companions": "solo | couple | family | group",
    "dietary": [],
    "interests": ["culture", "food", "hiking", ...],
    "languages": ["English", "中文"],
    "previous_destinations": [],
    "bucket_list": []
  },
  "trips": [],
  "last_updated": "ISO8601"
}
```

On first use, collect 6 multiple-choice questions (style, budget, pace, accommodation, companions, interests) then save. On subsequent trips, load preferences and only ask trip-specific questions (destination, dates, must-see items).

The reference skill uses `travel_db.py` for CRUD — we can write a lightweight `xhs_prefs.py` with just `load()`, `save()`, `add_trip()`, `get_preferences()`.

**Note:** No "previous destinations" auto-tracking. We only care about current knowledge of user's travel style. No post-trip feedback loop.

---

### Phase 2: Research Upgrade — Add Practical Web Searches

Currently the research phase runs XHS searches for activities, food, neighborhoods, and day trips. The reference skill also does **structured web searches across 10 categories**. We should add the following **between XHS rounds** (no extra infra, zero deps):

| Category | Tool | When |
|----------|------|------|
| **Entry requirements** (visa, passport) | `web_search` | After destination confirmed |
| **Best time to visit** (weather, seasons, festivals) | `web_search` | After destination + dates |
| **Safety** (scams, advisories, safe areas) | `web_search` | After destination confirmed |
| **Local transportation** (metro/bus, apps like DiDi/Uber) | `web_search` | Before transport section |
| **Practical info** (currency, tipping, power outlets) | `web_search` | In final report generation |

These are quick 1–2 search queries each. Bundle them into 1–2 `web_search` calls during the research phase.

---

### Phase 3: Itinerary Format Upgrade — Daily Breakdown with Structure

This is the biggest upgrade. The reference skill's Step 5 ("Generate Detailed Travel Plan") has a format with 6 things ours is missing:

1. **Estimated cost per day** (e.g. €120/person) — gives immediate sense of daily spend
2. **Booking notes on activities** ("Book tickets online, sells out fast")
3. **Geographic grouping as a hard rule** — no criss-crossing the city
4. **Realistic timing with buffers** — max 3–4 activities per day, don't over-schedule
5. **Transportation per day** — how to get from hotel to first activity
6. **Sub-activity hierarchy** — clean indented bullet lists under main activities

**Proposed format upgrade for daily itinerary output:**

```
***Day 1*** | Gothic Quarter & Old City
  **AM** · Gothic Quarter walking tour
    ↳ Cathedral | Plaça Reial | Las Ramblas
    💡 Book: Free self-guided
  **Lunch** · Cal Pep (tapas) | ~€25/pp
  **PM** · Picasso Museum | <link>
    💡 Tickets book online ~€15, sells out
  **Dinner** · El Born neighborhood | ~€40/pp
  **Evening** · Waterfront stroll
  ───
  🚶 Transport: Metro L1 from hotel (10 min)
  💰 Day cost: ~€105/pp
  📍 Note: All activities walkable from each other
```

Key changes from current format:
- **AM / PM / Evening** time blocks for natural pacing
- **Sub-activity hierarchy** with `↳` indents
- **💡 Booking tips** per activity
- **💰 Day cost** at the bottom
- **🚶 Transportation** line per day (hotel → first activity)
- **📍 Note** for geographic coherence

All of this is **format-only changes to the itinerary text output**. Zero additional scripts or dependencies. The agent generates this inline.

---

### Phase 4: Budget Breakdown

After collecting activities/food/hotel costs, calculate:

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

No script needed — this is pure math the agent can compute inline during the final report step.

---

### Phase 5: Pre-Trip Timeline

Generate a timeline relative to departure date:

```
2 MONTH BEFORE:
- Book flights, hotels
- Check passport/visa

1 MONTH BEFORE:
- Book popular attractions
- Notify bank

2 WEEKS BEFORE:
- Confirm reservations
- Check weather

1 WEEK BEFORE:
- Pack luggage
- Download apps, maps

DAY BEFORE:
- Re-check flight
- Set alarms
```

Agent generates this inline based on departure date from interview.

---

### Phase 6: Packing Checklist (Optional)

Generate a simple climate/activity-aware checklist:

```
Essentials: passport, phone, charger, adapter
Clothing: [based on season/destination]
Gear: [based on activities — hiking boots, swimsuit, etc.]
Documents: [visa printout, insurance, confirmations]
```

Agent generates inline — context-aware based on destination climate and user's listed activities.

---

### Phase 7: Trip Tracking & Post-Trip (Deferred)

Skip for now — these require user input during/after the trip, which isn't the main planning flow. Can add later as a separate "trip companion" mode.

---

## Implementation Order

| Priority | Phase | Effort | Deps | Value |
|----------|-------|--------|------|-------|
| 1 | Phase 3 — Itinerary Format Upgrade | Low (format changes only) | None | **High** — transforms output quality immediately |
| 2 | Phase 2 — Research Upgrade | Low (add web_search calls) | None | **High** — fills practical info gaps |
| 3 | Phase 1 — Preference System | Medium (write xhs_prefs.py + JSON schema) | Python stdlib | **High** — repeat user experience |
| 4 | Phase 4 — Budget Breakdown | Low (inline math) | None | Medium |
| 5 | Phase 5 — Pre-Trip Timeline | Low (inline generation) | None | Medium |
| 6 | Phase 6 — Packing Checklist | Low (inline generation) | None | Low-Medium |

---

## Architecture (Zero New Dependencies)

```
xhs-trip-planner
├── SKILL.md                    # Updated with all new steps
├── scripts/
│   └── xhs_prefs.py            # NEW — JSON file CRUD (load/save/add_trip)
└── ~/.openclaw/data/
    └── travel_preferences.json # NEW — persistent preference file
```

No new npm packages. No new Go binaries. No databases. No MCP servers.

**File format:** The preference file lives in `~/.openclaw/data/` which already exists and is persistent. The Python script uses only `json` and `os` (stdlib). Zero pip installs.
