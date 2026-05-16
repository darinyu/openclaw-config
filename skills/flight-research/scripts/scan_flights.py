#!/usr/bin/env python3
"""Multi-day flight scan: runs flight-search across a date range and outputs structured JSON.

Usage:
  python3 scripts/scan_flights.py SFO LAX 2026-05-17 2026-05-20
  python3 scripts/scan_flights.py SFO LAX 2026-05-17 2026-05-20 --adults 2 --class business --limit 5
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from urllib.parse import urlencode, quote


def make_gf_link(origin: str, dest: str, date_str: str) -> str:
    """Build a Google Flights search URL for a single date."""
    params = {
        "q": f"flights from {origin} to {dest} on {date_str}",
    }
    return f"https://www.google.com/travel/flights?{urlencode(params)}"


def make_gf_range_link(origin: str, dest: str, start: str, end: str) -> str:
    """Build a Google Flights search URL for a date range."""
    params = {
        "q": f"flights from {origin} to {dest} from {start} to {end}",
    }
    return f"https://www.google.com/travel/flights?{urlencode(params)}"


def parse_flight_output(text: str, scan_date: str) -> list[dict]:
    """Parse flight-search text output into structured records."""
    flights = []

    # Extract price level from header
    price_level = "unknown"
    for line in text.split("\n"):
        m = re.search(r"Prices are currently:\s*(\w+)", line)
        if m:
            price_level = m.group(1)
            break

    # Parse individual flights — each flight block separated by horizontal rules
    blocks = re.split(r"─{20,}", text)
    for block in blocks:
        block = block.strip()
        if not block or "✈️" in block:
            continue

        airline = None
        dep_time = None
        arr_time = None
        dep_date = None
        arr_date = None
        duration = None
        stops = None
        price = None
        is_best = False
        stop_info = None

        for line in block.split("\n"):
            line = line.strip()

            # Airline line: "Frontier ⭐ BEST" or just "United" — no emoji prefix
            m = re.match(r"^([A-Za-z][A-Za-z\s&]+?)(?:\s+⭐\s+BEST)?$", line)
            if m and not any(
                emoji in line for emoji in ["🕐", "⏱️", "✅", "💰", "✈️"]
            ) and not line.startswith("─"):
                candidate = m.group(1).strip()
                # Avoid false matches on header lines
                if candidate.lower() not in ("one way", "round trip", "prices are currently"):
                    airline = candidate
                    if "⭐ BEST" in line:
                        is_best = True

            # Time line: 🕐 7:26 PM on Mon, May 18 → 9:12 PM on Mon, May 18
            m = re.search(
                r"🕐\s+(\d{1,2}:\d{2}\s*[AP]M)\s+on\s+(\w+,\s*\w+\s+\d+)\s*→\s*(\d{1,2}:\d{2}\s*[AP]M)\s+on\s+(\w+,\s*\w+\s+\d+)",
                line,
            )
            if m:
                dep_time = m.group(1).strip()
                dep_date_str = m.group(2).strip()
                arr_time = m.group(3).strip()
                arr_date_str = m.group(4).strip()
                try:
                    dep_dt = datetime.strptime(f"{dep_date_str} {scan_date[:4]}", "%a, %b %d %Y")
                    dep_date = dep_dt.strftime("%Y-%m-%d")
                except ValueError:
                    dep_date = scan_date
                try:
                    arr_dt = datetime.strptime(f"{arr_date_str} {scan_date[:4]}", "%a, %b %d %Y")
                    arr_date = arr_dt.strftime("%Y-%m-%d")
                except ValueError:
                    arr_date = scan_date

            # Duration line: ⏱️  1 hr 46 min
            m = re.search(r"⏱️\s+(.+)", line)
            if m:
                duration = m.group(1).strip()

            # Stops line: ✅ Nonstop or ✅ 1 stop in XYZ
            m = re.search(r"✅\s+(.+)", line)
            if m:
                stops_text = m.group(1).strip()
                if stops_text.lower() == "nonstop":
                    stops = 0
                    stop_info = "nonstop"
                else:
                    sm = re.search(r"(\d+)\s+stop(?:\s+in\s+(.+))?", stops_text, re.IGNORECASE)
                    stops = int(sm.group(1)) if sm else 99
                    stop_info = sm.group(2) if sm and sm.group(2) else stops_text

            # Price line: 💰 $139
            m = re.search(r"💰\s+\$?([\d,]+)", line)
            if m:
                price = int(m.group(1).replace(",", ""))

        if airline and price:
            flights.append(
                {
                    "date": scan_date,
                    "airline": airline,
                    "departure": dep_time,
                    "arrival": arr_time,
                    "departure_date": dep_date or scan_date,
                    "arrival_date": arr_date or scan_date,
                    "duration": duration or "",
                    "stops": stops if stops is not None else 0,
                    "stop_info": stop_info or ("nonstop" if stops == 0 else f"{stops} stop(s)"),
                    "price": price,
                    "is_best": is_best,
                    "price_level": price_level,
                }
            )

    return flights


def run_flight_search(origin: str, dest: str, date_str: str, **kwargs) -> list[dict]:
    """Run flight-search for a single date and return parsed flights."""
    cmd = [
        "uvx",
        "flight-search",
        origin.upper(),
        dest.upper(),
        "--date",
        date_str,
        "--limit",
        str(kwargs.get("limit", 10)),
    ]
    if kwargs.get("adults"):
        cmd.extend(["--adults", str(kwargs["adults"])])
    if kwargs.get("children"):
        cmd.extend(["--children", str(kwargs["children"])])
    if kwargs.get("seat_class"):
        cmd.extend(["--class", kwargs["seat_class"]])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout or result.stderr
        if not output.strip():
            return []
        return parse_flight_output(output, date_str)
    except subprocess.TimeoutExpired:
        print(f"  [WARN] Timeout for {date_str}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  [WARN] Error for {date_str}: {e}", file=sys.stderr)
        return []


def date_range(start: str, end: str) -> list[str]:
    """Generate YYYY-MM-DD strings from start to end inclusive."""
    fmt = "%Y-%m-%d"
    start_dt = datetime.strptime(start, fmt).date()
    end_dt = datetime.strptime(end, fmt).date()
    dates = []
    d = start_dt
    while d <= end_dt:
        dates.append(d.strftime(fmt))
        d += timedelta(days=1)
    return dates


def main():
    parser = argparse.ArgumentParser(description="Scan flights across a date range")
    parser.add_argument("origin", help="Origin airport code (e.g. SFO)")
    parser.add_argument("dest", help="Destination airport code (e.g. LAX)")
    parser.add_argument("start_date", help="Start date YYYY-MM-DD")
    parser.add_argument("end_date", nargs="?", help="End date YYYY-MM-DD (default: same as start)")
    parser.add_argument("--adults", type=int, default=1)
    parser.add_argument("--children", type=int, default=0)
    parser.add_argument("--class", dest="seat_class", default=None, help="economy|premium-economy|business|first")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--no-filter", action="store_true", help="Keep Unknown airline entries")

    args = parser.parse_args()
    end = args.end_date or args.start_date

    all_dates = date_range(args.start_date, end)
    all_flights = []

    print(f"Scanning {args.origin.upper()} → {args.dest.upper()}", file=sys.stderr)
    print(f"  Dates: {args.start_date} to {end} ({len(all_dates)} days)", file=sys.stderr)
    print(file=sys.stderr)

    for i, d in enumerate(all_dates, 1):
        print(f"  [{i}/{len(all_dates)}] {d} ...", file=sys.stderr, end=" ", flush=True)
        flights = run_flight_search(
            args.origin,
            args.dest,
            d,
            adults=args.adults,
            children=args.children,
            seat_class=args.seat_class,
            limit=args.limit,
        )
        print(f"{len(flights)} flights found", file=sys.stderr)
        all_flights.extend(flights)

    # Filter out Unknown airline entries on dates that have real data
    if not args.no_filter:
        # Group by date
        by_date = {}
        for f in all_flights:
            by_date.setdefault(f["date"], []).append(f)

        filtered = []
        for date_str, flights in by_date.items():
            has_real = any(f["airline"] != "Unknown" for f in flights)
            if has_real:
                # Only keep non-Unknown entries for this date
                filtered.extend(f for f in flights if f["airline"] != "Unknown")
            else:
                # No real data, keep Unknown entries as-is
                filtered.extend(flights)
        all_flights = filtered

    # Deduplicate: same airline, same price, same departure time on same date
    seen = set()
    unique_flights = []
    for f in all_flights:
        key = (f["date"], f["airline"], f["price"], f.get("departure") or "")
        if key not in seen:
            seen.add(key)
            unique_flights.append(f)
    all_flights = unique_flights

    # Sort by price then date then departure time
    all_flights.sort(key=lambda f: (f["price"], f["date"], f.get("departure") or ""))

    # Build links
    links = {}
    for d in all_dates:
        links[d] = make_gf_link(args.origin, args.dest, d)

    output = {
        "origin": args.origin.upper(),
        "destination": args.dest.upper(),
        "scan_start": args.start_date,
        "scan_end": end,
        "total_flights": len(all_flights),
        "links": {
            "per_date": links,
            "full_range": make_gf_range_link(args.origin, args.dest, args.start_date, end),
        },
        "flights": all_flights,
    }

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
