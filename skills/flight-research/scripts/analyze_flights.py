#!/usr/bin/env python3
"""Analyze scanned flight data: clean, rank, and recommend best options.

Usage:
  python3 scripts/scan_flights.py SFO LAX 2026-05-16 2026-05-25 --limit 10 --pretty > /tmp/flights.json
  python3 scripts/analyze_flights.py /tmp/flights.json --target-date 2026-05-24
  python3 scripts/analyze_flights.py /tmp/flights.json --target-date 2026-05-24 --sort price
"""

import argparse
import json
import re
import sys
from datetime import datetime


# ── Scoring weights ──────────────────────────────────────────────

WEIGHTS_LEISURE = {
    "price": 0.40,
    "comfort": 0.25,
    "timing": 0.20,
    "date_proximity": 0.15,
}

WEIGHTS_BUSINESS = {
    "price": 0.20,
    "comfort": 0.35,
    "timing": 0.35,
    "date_proximity": 0.10,
}

LEISURE_TIME_WINDOWS = [(6, 10), (14, 20)]
BUSINESS_TIME_WINDOWS = [(6, 9), (16, 20)]


def parse_duration(dur: str) -> int:
    """Parse '1 hr 46 min' to minutes. Returns 999 on failure."""
    dur = dur.strip()
    if not dur:
        return 999
    total = 0
    m_h = re.search(r"(\d+)\s*hr", dur)
    m_m = re.search(r"(\d+)\s*min", dur)
    if m_h:
        total += int(m_h.group(1)) * 60
    if m_m:
        total += int(m_m.group(1))
    return total if total > 0 else 999


def parse_hour(time_str: str | None) -> int | None:
    """Convert '7:26 PM' to 19 (24h). Returns None on failure."""
    if not time_str:
        return None
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", time_str.strip(), re.IGNORECASE)
    if not m:
        return None
    h, _, ampm = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ampm == "PM" and h != 12:
        h += 12
    if ampm == "AM" and h == 12:
        h = 0
    return h


def clean_flights(flights: list[dict]) -> list[dict]:
    """Remove Unknown airline entries with no timing, deduplicate."""
    cleaned = []
    seen = set()
    for f in flights:
        # Skip Unknown airlines with no timing data
        if f["airline"] == "Unknown" and not f.get("departure"):
            continue
        # Deduplicate
        key = (f["date"], f.get("departure") or "", f["airline"], f["price"])
        if key in seen:
            continue
        seen.add(key)
        entry = dict(f)
        # Normalize display
        entry["airline_display"] = "Various" if entry["airline"] == "Unknown" else entry["airline"]
        # Parse duration to minutes
        entry["duration_min"] = parse_duration(entry.get("duration", ""))
        entry["departure_hour"] = parse_hour(entry.get("departure"))
        entry["arrival_hour"] = parse_hour(entry.get("arrival"))
        cleaned.append(entry)
    return cleaned


def score_price(price: int, min_p: int, max_p: int) -> float:
    """Normalize price 0-100. Lower price = higher score."""
    if max_p == min_p:
        return 100.0
    return 100.0 * (1.0 - (price - min_p) / (max_p - min_p))


def score_comfort(duration_min: int, stops: int) -> float:
    """Score comfort: shorter + non-stop = better. 0-100."""
    stop_score = max(0.0, 100.0 - stops * 50.0)
    if duration_min >= 999:
        dur_score = 50.0
    elif duration_min <= 100:
        dur_score = 100.0
    else:
        dur_score = max(0.0, 100.0 - (duration_min - 100) / 2.0)
    return stop_score * 0.6 + dur_score * 0.4


def score_timing(hour: int | None, windows: list[tuple]) -> float:
    """Score a departure hour against preferred windows. 0-100."""
    if hour is None:
        return 50.0
    for w_start, w_end in windows:
        if w_start <= hour < w_end:
            return 100.0
    # Distance penalty from nearest window
    dist = min(min(abs(hour - ws), abs(hour - we)) for ws, we in windows)
    return max(0.0, 100.0 - dist * 15.0)


def score_date_proximity(date_str: str, target: str | None) -> float:
    """Score how close the flight date is to target. 0-100."""
    if not target:
        return 100.0
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        t = datetime.strptime(target, "%Y-%m-%d")
        diff = abs((d - t).days)
        if diff == 0:
            return 100.0
        return max(0.0, 100.0 - diff * 20.0)
    except ValueError:
        return 50.0


def rank_flights(
    flights: list[dict],
    target_date: str | None = None,
    sort_by: str = "combined",
    trip_type: str = "leisure",
) -> list[dict]:
    """Rank flights by multi-dimensional scoring."""
    if not flights:
        return []

    weights = WEIGHTS_BUSINESS if trip_type == "business" else WEIGHTS_LEISURE
    time_windows = BUSINESS_TIME_WINDOWS if trip_type == "business" else LEISURE_TIME_WINDOWS

    prices = [f["price"] for f in flights]
    min_p, max_p = min(prices), max(prices)

    scored = []
    for f in flights:
        p_score = score_price(f["price"], min_p, max_p)
        c_score = score_comfort(f["duration_min"], f["stops"])
        t_score = score_timing(f["departure_hour"], time_windows)
        d_score = score_date_proximity(f["date"], target_date)

        combined = (
            p_score * weights["price"]
            + c_score * weights["comfort"]
            + t_score * weights["timing"]
            + d_score * weights["date_proximity"]
        )

        scored.append({
            **f,
            "score_price": round(p_score, 1),
            "score_comfort": round(c_score, 1),
            "score_timing": round(t_score, 1),
            "score_date": round(d_score, 1),
            "score_combined": round(combined, 1),
        })

    sort_key_map = {
        "price": lambda x: (-x["score_price"], x["price"]),
        "comfort": lambda x: (-x["score_comfort"], x["duration_min"]),
        "timing": lambda x: (-x["score_timing"], x.get("departure_hour") or 0),
        "combined": lambda x: (-x["score_combined"], x["price"]),
    }
    key_fn = sort_key_map.get(sort_by, sort_key_map["combined"])
    scored.sort(key=key_fn)

    for i, f in enumerate(scored, 1):
        f["rank"] = i

    return scored


def make_gf_url(origin: str, dest: str, date_str: str) -> str:
    return f"https://www.google.com/travel/flights?q=flights+from+{origin}+to+{dest}+on+{date_str}"


def format_option_line(f: dict, origin: str, dest: str) -> str:
    """One-line flight option with embedded GF link on price."""
    dep = f.get("departure") or "-"
    arr = f.get("arrival") or "-"
    dur = f.get("duration") or f"{f['duration_min']}m"
    stop_display = "✈" if f["stops"] == 0 else f"{f['stops']}✈"
    gf = make_gf_url(origin, dest, f["date"])
    return f"• <{gf}|${f['price']}> *{f['airline_display']}* {f['date']} {dep}→{arr} ({dur}) {stop_display}"


def format_slack(ranked: list[dict], ctx) -> str:
    """Format ranked flights for Slack readability: summary first, then details, links everywhere."""
    if not ranked:
        return "No flights found in the date range."

    target_label = ctx.target_date if ctx.target_date else "any date in range"
    trip_label = "Leisure trip" if ctx.trip_type == "leisure" else "Business trip"

    lines = []
    lines.append(f"*Flight Research: {ctx.origin} → {ctx.destination}*")
    lines.append(f"*{trip_label}* · {ctx.scan_start} to {ctx.scan_end} · *Target:* {target_label}")
    lines.append("")

    # ── Summary: Top Pick ──
    best = ranked[0]
    stop_display = "nonstop" if best["stops"] == 0 else f"{best['stops']} stop(s)"
    dep = best.get("departure") or "various"
    arr = best.get("arrival") or "various"
    dur = best.get("duration") or f"{best['duration_min']} min"
    gf_best = make_gf_url(ctx.origin, ctx.destination, best["date"])

    lines.append("*Top Pick*")
    lines.append(
        f"*{best['airline_display']}* — ${best['price']} ({dur}, {stop_display})  "
        f"{best['date']} {dep}→{arr}"
    )
    lines.append(f"<{gf_best}|View on Google Flights>")
    lines.append("")

    # Also consider (if close enough to top)
    second = ranked[1] if len(ranked) > 1 and ranked[1]["score_combined"] >= best["score_combined"] * 0.85 else None
    if second:
        stop2 = "nonstop" if second["stops"] == 0 else f"{second['stops']} stop(s)"
        dep2 = second.get("departure") or "various"
        arr2 = second.get("arrival") or "various"
        dur2 = second.get("duration") or f"{second['duration_min']} min"
        gf2 = make_gf_url(ctx.origin, ctx.destination, second["date"])
        lines.append("*Also Consider*")
        lines.append(
            f"*{second['airline_display']}* — ${second['price']} ({dur2}, {stop2})  "
            f"{second['date']} {dep2}→{arr2}"
        )
        lines.append(f"<{gf2}|View on Google Flights>")
        lines.append("")

    # ── All Options (compact list) ──
    lines.append("*All Options (by rank)*")
    for f in ranked[:15]:
        lines.append(format_option_line(f, ctx.origin, ctx.destination))

    # ── Quick stats ──
    lines.append("")
    cheapest = min(ranked, key=lambda x: x["price"])
    gf_cheapest = make_gf_url(ctx.origin, ctx.destination, cheapest["date"])
    lines.append(
        f"*Cheapest:* ${cheapest['price']} *{cheapest['airline_display']}* on *{cheapest['date']}* "
        f"<{gf_cheapest}|View>"
    )
    if ctx.target_date:
        on_date = [f for f in ranked if f["date"] == ctx.target_date]
        if on_date:
            best_on = on_date[0]
            gf_on = make_gf_url(ctx.origin, ctx.destination, ctx.target_date)
            lines.append(
                f"*On target date ({ctx.target_date}):* from *${best_on['price']}* "
                f"<{gf_on}|View>"
            )
    lines.append(
        f"*Full range:* "
        f"<https://www.google.com/travel/flights?q=flights+from+{ctx.origin}+to+{ctx.destination}+from+{ctx.scan_start}+to+{ctx.scan_end}|See all dates>"
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze and rank scanned flight data")
    parser.add_argument("input_file", help="JSON output file from scan_flights.py")
    parser.add_argument("--target-date", help="Preferred travel date (YYYY-MM-DD)")
    parser.add_argument("--sort", choices=["combined", "price", "comfort", "timing"], default="combined")
    parser.add_argument("--trip-type", choices=["leisure", "business"], default="leisure")
    parser.add_argument("--top", type=int, default=0, help="Only show top N (0 = all)")
    args = parser.parse_args()

    with open(args.input_file) as f:
        data = json.load(f)

    raw_flights = data.get("flights", [])
    if not raw_flights:
        print("No flight data found in input file.")
        sys.exit(1)

    cleaned = clean_flights(raw_flights)
    if not cleaned:
        print("All flights filtered out (Unknown airlines with no timing).")
        sys.exit(1)

    ranked = rank_flights(
        cleaned,
        target_date=args.target_date,
        sort_by=args.sort,
        trip_type=args.trip_type,
    )

    if args.top > 0:
        ranked = ranked[:args.top]

    ctx = type("Args", (), {
        "origin": data.get("origin", "???"),
        "destination": data.get("destination", "???"),
        "scan_start": data.get("scan_start", ""),
        "scan_end": data.get("scan_end", ""),
        "target_date": args.target_date,
        "trip_type": args.trip_type,
        "sort": args.sort,
    })

    print(format_slack(ranked, ctx))


if __name__ == "__main__":
    main()
