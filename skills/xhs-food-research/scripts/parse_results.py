#!/usr/bin/env python3
"""
Parse XHS search results JSON into structured data.
Reads from stdin or --input file, outputs tabular text.

Usage:
  mcporter call xiaohongshu-mcp.search_feeds --keyword "keyword" | python3 parse_results.py
  python3 parse_results.py --input results.json
  python3 parse_results.py --input results.json --output json  # structured JSON output
"""

import json
import sys

def parse_feeds(data):
    feeds = data.get("feeds", [])
    results = []
    for f in feeds:
        mt = f.get("modelType", "")
        if mt != "note":
            continue
        nc = f.get("noteCard", {})
        ii = nc.get("interactInfo", {})
        title = nc.get("displayTitle", "").strip()
        if not title:
            continue
        likes = int(ii.get("likedCount", 0) or 0)
        collects = int(ii.get("collectedCount", 0) or 0)
        comments = int(ii.get("commentCount", 0) or 0)
        shares = int(ii.get("sharedCount", 0) or 0)
        engagement = likes + collects
        author = nc.get("user", {}).get("nickname", "") or nc.get("user", {}).get("nickName", "")
        feed_id = f.get("id", "")
        xsec = f.get("xsecToken", "")
        results.append({
            "title": title,
            "author": author,
            "likes": likes,
            "collects": collects,
            "comments": comments,
            "shares": shares,
            "engagement": engagement,
            "feed_id": feed_id,
            "xsec_token": xsec,
            "link": f"https://www.xiaohongshu.com/explore/{feed_id}" if feed_id else "",
        })
    results.sort(key=lambda r: r["engagement"], reverse=True)
    return results


def print_table(results):
    print(f"{'👍':>4} {'⭐':>4} {'💬':>3} {'Eng':>4} | {'Title':<55} | {'Author':<12}")
    print("-" * 100)
    for r in results:
        print(f"{r['likes']:>4} {r['collects']:>4} {r['comments']:>3} {r['engagement']:>4} | {r['title'][:54]:<55} | {r['author'][:11]:<12}")


def print_json(results):
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    data = None
    output = "table"

    args = list(sys.argv[1:])
    for i, a in enumerate(args):
        if a == "--input" and i + 1 < len(args):
            with open(args[i + 1]) as f:
                data = json.load(f)
        elif a == "--output" and i + 1 < len(args):
            output = args[i + 1]
        elif a == "--all":
            output = "table"

    if data is None:
        data = json.load(sys.stdin)

    results = parse_feeds(data)
    if output == "json":
        print_json(results)
    else:
        print_table(results)


if __name__ == "__main__":
    main()
