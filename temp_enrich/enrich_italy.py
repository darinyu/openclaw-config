#!/usr/bin/env python3
"""Enrich Italy+Greece posts by calling get_feed_detail and updating data.json"""
import json, subprocess, sys, time

# Post definitions: feed_id -> xsecToken, and rank for matching
POSTS = {
    "6927c2df000000001e0304bc": {"token": "ABADUYTukRV436L_htVVmbiRMZ1SAvxr4cc7ACwjysdUs=", "rank": 1, "done": False},
    "68b29ca1000000001d00244b": {"token": "ABn6YhWIEkFUcDSNwSPZDHc5Mx-4EywQdBU_UiHO6oZhI=", "rank": 2, "done": False},
    "6957d7c8000000001e0360fd": {"token": "ABZhPuY6NIvIdcCCAB-zaYuVGqdjLdFzKhjlQp9Tawysk=", "rank": 7, "done": False},
    "69f5853800000000380350cf": {"token": "ABsnpqFZiqOjuXMYfz1EjG17aVL6KaSixg-TN1KEM7whk=", "rank": 10, "done": False},
    "69fb039d000000001f003018": {"token": "ABbpmYhrSQgCLWQEMyubDbaBomkG4enxMhfnJIbVW-ANE=", "rank": 11, "done": False},
    "69e8aa9b000000001d01c5d2": {"token": "ABoXartc02VE-qnNpxBdUxMMN1nkh-epznvVx7ya10cfU=", "rank": 12, "done": False},
    "68ec47620000000004002a70": {"token": "ABUkQhuhxwJ2uXOCGXINU0rF-IMR1vENz6xkfdwKFkg-M=", "rank": 14, "done": False},
}

# Load data.json
with open("temp_enrich/italy_greece_data.json") as f:
    data = json.load(f)

results_by_id = {}
for r in data["results"]:
    fid = r["link"].split("/explore/")[-1]
    results_by_id[fid] = r

# Process each post
for fid, info in POSTS.items():
    print(f"\n=== Processing rank {info['rank']} (id: {fid}) ===")
    cmd = [
        "mcporter", "call", "xiaohongshu-mcp.get_feed_detail",
        "--feed_id", fid,
        "--xsec_token", info["token"],
        "--limit", "5"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        resp = json.loads(result.stdout)
        note = resp.get("data", {}).get("note", {})
        desc = note.get("desc", "")
        
        has_content = bool(desc.strip()) and len(desc.strip()) >= 20
        
        comments_raw = note.get("comments", {}).get("comments", [])
        top_comments = []
        for c in comments_raw[:5]:
            content = c.get("content", "")
            if content:
                top_comments.append({
                    "content": content,
                    "nickname": c.get("user_info", {}).get("nickname", ""),
                    "likes": c.get("likes_count", 0)
                })
        
        print(f"  desc_len={len(desc)}, has_content={has_content}, comments={len(top_comments)}")
        
        # Update the result
        if fid in results_by_id:
            results_by_id[fid]["desc"] = desc
            results_by_id[fid]["has_content"] = has_content
            if top_comments:
                results_by_id[fid]["top_comments"] = top_comments
            print(f"  UPDATED {fid}")
        else:
            print(f"  WARNING: {fid} not found in data.json results!")
    
        info["done"] = True
    
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Small delay to be polite
    time.sleep(1)

# Save updated data
with open("temp_enrich/italy_greece_data_updated.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone! Saved updated data.json")
print(f"Posts still with has_content=False: {sum(1 for r in data['results'] if r.get('has_content') == False)}")
print(f"Posts with has_content=True: {sum(1 for r in data['results'] if r.get('has_content') == True)}")
