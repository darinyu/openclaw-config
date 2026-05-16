---
name: hotel-research
description: "Hotel research, live price comparison, and booking link generation across Google Hotels, Booking.com, and Agoda. Use when users ask to: find hotels, compare prices, check availability, plan accommodation for a trip, research hotel options in a city, or find the cheapest/best hotel deals. Not for non-hotel lodging (Airbnb, hostels)."
---

# Hotel Research

Live hotel price search and comparison. Uses Google Hotels via browser for real-time data.

## Step 1: Parse Request

Extract from user's natural language:

| Field | Required | Default |
|-------|----------|---------|
| Destination | Yes | — |
| Check-in | Yes | Ask if unclear |
| Check-out | Yes | Ask if unclear |
| Guests (adults) | No | 2 |
| Rooms | No | 1 |
| Currency | No | USD |

Parse naturally from phrases like:
- "hotels in Sunnyvale this weekend" → destination=Sunnyvale, check-in=next Friday, check-out=next Sunday
- "find me a place in Tokyo for 3 nights in June" → destination=Tokyo, check-in=June 1, check-out=June 4
- "Sunnyvale 94086 today" → destination=Sunnyvale 94086, check-in=today, check-out=tomorrow

If dates are ambiguous, ask the user in one message (not multiple back-and-forths).

## Step 2: Search Google Hotels

Open browser and navigate to:

```
https://www.google.com/travel/search?q=hotels%20in%20{DESTINATION}&hl=en
```

Use the browser tool with `action=open` or `action=navigate`. Then take a snapshot to extract results.

## Step 3: Extract Results

From the snapshot, extract per hotel:
- Name
- Price (starting from / nightly)
- Star rating
- Review count
- Deal badges (e.g. "25% less than usual", "GREAT DEAL")
- Any featured amenities (pool, pet-friendly, free cancellation, eco-certified)

## Step 4: Generate Booking Links

Build booking URLs per hotel (URL-encode hotel name as `{H}`):

| Site | Booking URL |
|------|-------------|
| Booking.com | `https://www.booking.com/searchresults.html?ss={H}&checkin={CHECK_IN}&checkout={CHECK_OUT}&group_adults={ADULTS}&no_rooms={ROOMS}` |
| Agoda | `https://www.agoda.com/search?q={H}&checkIn={CHECK_IN}&checkOut={CHECK_OUT}&los={LOS}&rooms={ROOMS}&adults={ADULTS}` |
| Trip.com | `https://www.trip.com/hotels/list?keyword={H}&checkin={CHECK_IN}&checkout={CHECK_OUT}` |
| Hotels.com | `https://www.hotels.com/search.do?q={H}&checkin={CHECK_IN}&checkout={CHECK_OUT}` |
| Expedia | `https://www.expedia.com/Hotel-Search?destination={H}&d1={CHECK_IN}&d2={CHECK_OUT}&adults={ADULTS}&rooms={ROOMS}` |

## Step 5: Present Results

Present results organized by price tier. Never use markdown tables. Use bullet lists with bold labels.

Format:
- Section header: destination + dates + guests
- Budget-friendly (under $X)
- Mid-range ($X-$Y)
- Premium ($Y+)

Each hotel entry:
- **Name** — $Price/night, X.X stars (X reviews) — Deal badge, amenities
- Booking links: [Booking.com](url) | [Agoda](url) | [Trip.com](url)

## Error Handling

- Google Hotels blocks → try adding `&hl=en` or using `action=navigate` instead of `action=open`
- No results → suggest nearby cities or ask user to broaden search
- Price shows as "not shown" → note it in the listing

## Scripts

No external scripts needed. All operations use browser + web.
