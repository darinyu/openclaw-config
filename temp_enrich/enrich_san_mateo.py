#!/usr/bin/env python3
"""Enrich San Mateo food posts by calling get_feed_detail and updating data.json"""
import json, subprocess, sys, time

# Post definitions: feed_id -> xsecToken
POSTS = {
    "69b2361f000000001b01ff41": {"token": "ABfxgwgPVhfGb3WpK5buqc96WopwelukmUTWsaqAB6lzw=", "rank": 5},
    "61a6d6e3000000002103f421": {"token": "ABDyFvhIYUjmapqsz7M96-hk0OOf3-rWh4TUYKybmHvnY=", "rank": 6},
    "68bd20c3000000001d016de4": {"token": "AB5aT7FgpYL0tkgWP5BreoWqU2bSOXarNzeA_I0WkLlh0=", "rank": 8},
    "6875b235000000000b02e1f5": {"token": "ABq23rZzGzjve1pv9QPwpU_FIBiXQVnw1TtVCjvjqi1Q0=", "rank": 9},
    "6803da3c000000001c017577": {"token": "AB9DJCP6sVRUEIlVn_8F3ps5jqG8B-MSE-oQqq5Im5IyU=", "rank": 10},
    "69fbd9c800000000380371d0": {"token": "ABbpmYhrSQgCLWQEMyubDbaEOALoAD793MK89igc2nsiQ=", "rank": 12},
    "687303a50000000010024781": {"token": "ABX1UYWU9KMU2lPH3PNX3cDrY24TqARAQ7vivazLTIiJ4=", "rank": 13},
    "69ed6e1a0000000010001c00": {"token": "ABtVlp6T3S9kzQC9keVJAnqxL72wfCOSLcsrY3xI9oiFk=", "rank": 14},
    "691d313f000000000d03a92f": {"token": "ABhZe44IJU8SA1_qUTdtJ8Sp68RNwNZ0XiBuS2_3M0PkE=", "rank": 15},
    "692bbe32000000001d03c9a9": {"token": "ABLWXfebtJNwbLyqWc5zXd7hAuy2lWVooYz6begt0S-9Y=", "rank": 16},
    "68eedfcc000000000301c327": {"token": "ABNJqlcETkzkWFGWcwCtM1RUXSEv8i6ZpWQwhZ4FfatQw=", "rank": 17},
    "6a0ba8420000000035032c05": {"token": "ABgbT-MFoXw9RqdzhFHOh0I2doCqA1nPLBqyRlafvx9FI=", "rank": 18},
    "678896fb0000000021001de4": {"token": "AB1eK6davUimO7vzKFd0SfxUL0l6aErC9VF169d2FyizE=", "rank": 19},
}

# Load data.json
with open("temp_enrich/san_mateo_food_data.json") as f:
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
    
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Small delay to be polite
    time.sleep(1)

# Save updated data
with open("temp_enrich/san_mateo_food_data_updated.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone! Saved updated data.json")
unknown = sum(1 for r in data['results'] if r.get('has_content') == 'unknown' or r.get('has_content') is False)
true_count = sum(1 for r in data['results'] if r.get('has_content') == True)
print(f"Posts with has_content=unknown/false: {unknown}")
print(f"Posts with has_content=True: {true_count}")
