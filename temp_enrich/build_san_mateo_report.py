#!/usr/bin/env python3
"""Build comprehensive San Mateo food report from enriched data.json"""
import json

with open("temp_enrich/san_mateo_food_data_updated.json") as f:
    data = json.load(f)

results = data["results"]

# Print all enriched data for review
for r in results:
    print(f"\n{'='*60}")
    print(f"RANK {r['rank']}: {r['title']}")
    print(f"Author: {r.get('author','')}")
    print(f"👍{r['likes']} ⭐{r['collects']} 💬{r['comments_count']}")
    print(f"has_content: {r['has_content']}")
    desc = r.get('desc','')
    print(f"Desc ({len(desc)} chars):")
    print(desc[:500])
    print()
