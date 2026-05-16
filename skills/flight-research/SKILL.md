---
name: flight-research
description: Multi-day flight research scanning Google Flights across +/- days of a target date. Gathers ticket prices, airlines, times, and stops into a structured dataset, then analyzes and recommends the best option. Use when the user asks about flight prices, booking flights, or finding the cheapest way to fly between cities. NOT for hotels, rental cars, or non-flight travel.
---

# Flight Research

Research flight options across multiple dates and recommend the best option considering price, comfort (non-stop, timing), and flexibility.

## Workflow

### 1. Understand the request

Parse what the user needs into variables:

| Variable | Example | How to derive |
|---|---|---|
| `{ORIGIN}` | SFO | Airport code from user's origin |
| `{DEST}` | LAX | Airport code from user's destination |
| `{TARGET_DATE}` | 2026-05-24 | Parsed date from user request (exact or best guess) |
| `{TRIP_TYPE}` | one-way / round-trip | Ask or infer from context |
| `{RETURN_DATE}` | 2026-05-27 | Only if round-trip, ask or infer |
| `{PREFERENCES}` | morning, non-stop | Optional, ask if unclear |
| `{ADULTS}` | 1 | Default 1, ask if group |
| `{CLASS}` | economy | Default economy, ask if premium |

**If the user is vague** ("next weekend", "around May"), resolve specific dates:
- Today's date: check via session_status
- "Next weekend" → the coming Fri-Sun
- "Around May 18" → +/- 3 days from May 18

### 2. Gather tickets

Construct commands dynamically using the parsed variables. Do **not** run the example literally — substitute the user's values.

#### If one-way:

```bash
# Scan target date +/- 2-3 days for comparison
python3 skills/flight-research/scripts/scan_flights.py {ORIGIN} {DEST} {FLEX_START} {FLEX_END} --limit 10 --pretty > /tmp/outbound.json
```

Where `{FLEX_START}` = `{TARGET_DATE} - 2 days` and `{FLEX_END}` = `{TARGET_DATE} + 2 days`.

#### If round-trip:

```bash
# Step 1: Scan outbound range
python3 skills/flight-research/scripts/scan_flights.py {ORIGIN} {DEST} {OUTBOUND_START} {OUTBOUND_END} --limit 10 --pretty > /tmp/outbound.json

# Step 2: Scan return range
python3 skills/flight-research/scripts/scan_flights.py {DEST} {ORIGIN} {RETURN_START} {RETURN_END} --limit 10 --pretty > /tmp/return.json
```

Where:
- `{OUTBOUND_START}` = `{TARGET_DATE} - 2 days`
- `{OUTBOUND_END}` = `{TARGET_DATE} + 2 days`
- `{RETURN_START}` = `{RETURN_DATE} - 2 days`
- `{RETURN_END}` = `{RETURN_DATE} + 2 days`

#### Fallback if scan fails

If `uvx flight-search` errors or returns empty results:

1. **Retry once** with `--limit 5` (smaller request sometimes succeeds)
2. **If still fails:** generate a Google Flights link for the user to check directly:
   `https://www.google.com/travel/flights?q=flights+from+{ORIGIN}+to+{DEST}+on+{DATE}`
3. **If `uvx` is not installed:** try `uvx` auto-installs, but if missing, suggest `pip install flight-search`
4. **Minimum viable fallback:** always provide a Google Flights search link — the user can always check manually

### 3. Analyze and rank

Run `analyze_flights.py` on the scan results:

```bash
python3 skills/flight-research/scripts/analyze_flights.py /tmp/outbound.json --target-date {TARGET_DATE} --trip-type {TRIP_TYPE}
```

Options:
- `--target-date YYYY-MM-DD` — preferred travel date (closer flights score higher)
- `--trip-type leisure|business` — adjusts weights (leisure = price first, business = comfort + timing)
- `--sort price|comfort|timing|combined` — sort by specific dimension

#### Round-trip: combine outbound + return

For round-trips, the best **pair** matters more than individual legs:

1. **Run analysis on each leg separately** to get ranked lists
2. **Find the cheapest pair:** pick the cheapest outbound + cheapest return that create a sensible itinerary (outbound before return)
3. **Also consider:** cheapest outbound + most convenient return, or vice versa
4. **Present both legs** in the recommendation

There is **no script** to auto-combine outbound + return yet. Analyze the two JSON files manually using the ranking logic below, or point the user to Google Flights for the complete round-trip search.

#### Scoring dimensions

| Dimension | What it measures | Leisure weight | Business weight |
|---|---|---|---|
| **Price** | Lower = higher score (normalized within range) | 40% | 20% |
| **Comfort** | Non-stop + shorter duration = higher score | 25% | 35% |
| **Timing** | Morning (6-10am) for business, late afternoon for leisure | 20% | 35% |
| **Date proximity** | Closer to target date = higher score | 15% | 10% |

### 4. Present results

**First produce generic structured data** — the analysis output with ranked flights, prices, links.

**Then reformat for the context:**

- **If responding in Slack:** use Slack mrkdwn. Summary first (Top Pick, Also Consider), then compact list with Google Flights links on every price. Use **bold** (double asterisks) for ALL emphasis. Never use italic (underscores). Avoid tables.
- **If responding in chat/console:** plain text summary with links.
- **If building an itinerary:** present as structured flight data (airline, price, departure/arrival, link) for inclusion in the itinerary.

**Always include Google Flights links** so the user can verify and book.

## Price accuracy note

The `flight-search` tool hits Google Flights' internal API directly — same backend the website uses. Prices are live and should match what Google Flights shows. The only known quirk is the protobuf decoder sometimes fails to map airline codes to names, producing "Unknown" airline entries. Include Google Flights links so the user can open and book on the real site.

## Scripts

### `scripts/scan_flights.py`

Scans flights across a date range using `uvx flight-search`. Outputs structured JSON.

```bash
python3 skills/flight-research/scripts/scan_flights.py ORIGIN DEST START_DATE END_DATE --limit 10 --pretty > output.json
```

Options:
- `--class business|premium-economy|first` — seat class
- `--adults N` — number of adults
- `--children N` — number of children
- `--limit N` — max results per day (default: 10)
- `--no-filter` — keep Unknown airline entries

Output includes `links.per_date` and `links.full_range` for direct Google Flights URLs.

### `scripts/analyze_flights.py`

Takes `scan_flights.py` JSON, cleans it, scores each flight across 4 dimensions, and outputs a Slack-formatted summary with links.

```bash
python3 skills/flight-research/scripts/analyze_flights.py /tmp/flights.json --target-date 2026-05-24 --trip-type leisure --sort combined
```

The `analyze_flights.py` output is **Slack-formatted** (summary first, links, bold). For non-Slack contexts, use the raw JSON output from `scan_flights.py` directly and format yourself.
