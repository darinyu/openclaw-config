#!/usr/bin/env python3
"""
XHS Trip Planner — Preference System
=====================================
Zero dependencies (stdlib only: json, os).
Provides load/save/get_preferences/add_trip for a JSON preference file
checked into the skill directory.
"""

import json
import os
import sys

# Preference file lives inside the skill directory, checked into git
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, "data")
PREFS_FILE = os.path.join(DATA_DIR, "travel_preferences.json")

DEFAULT_PREFS = {
    "profile": {
        "travel_style": None,        # adventurous | relaxed | balanced
        "budget_level": None,        # budget | mid-range | luxury
        "pace": None,                # relaxed | moderate | packed
        "accommodation": None,       # hotel | boutique | resort
        "companions": None,          # solo | couple | family | group
        "dietary": [],               # list of restrictions
        "interests": [],             # list of interest areas
        "languages": ["English"],    # user's preferred planning languages
        "previous_destinations": [], # NOT auto-tracked, manual only
        "bucket_list": []            # optional
    },
    "trips": [],
    "last_updated": None
}


def _ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load():
    """Load preferences from JSON file. Returns dict (never None)."""
    if not os.path.exists(PREFS_FILE):
        # Initialize with defaults and save
        prefs = dict(DEFAULT_PREFS)
        save(prefs)
        return prefs

    try:
        with open(PREFS_FILE, "r") as f:
            prefs = json.load(f)
    except (json.JSONDecodeError, IOError):
        # Corrupted file — reset to defaults
        prefs = dict(DEFAULT_PREFS)
        save(prefs)

    # Fill in any missing keys from defaults
    return _merge_defaults(prefs)


def save(prefs):
    """Save preferences to JSON file (pretty-printed)."""
    _ensure_data_dir()
    from datetime import datetime, timezone
    prefs["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_preferences():
    """Convenience: load and return just the profile section."""
    prefs = load()
    return prefs.get("profile", {})


def add_trip(trip_data):
    """Append a completed trip to the trips list. Trip_data is a dict."""
    prefs = load()
    if "trips" not in prefs:
        prefs["trips"] = []
    prefs["trips"].append(trip_data)
    save(prefs)


def get_trips():
    """Return list of past trips."""
    prefs = load()
    return prefs.get("trips", [])


def _merge_defaults(prefs):
    """Recursively merge saved prefs with defaults to handle schema upgrades."""
    result = {}
    for key, default_val in DEFAULT_PREFS.items():
        if key not in prefs:
            result[key] = default_val
        elif isinstance(default_val, dict) and isinstance(prefs.get(key), dict):
            merged = dict(default_val)
            merged.update(prefs[key])
            result[key] = merged
        else:
            result[key] = prefs[key]
    return result


def is_first_run():
    """Return True if no saved preferences exist (default fresh file)."""
    return not os.path.exists(PREFS_FILE) or load() == dict(DEFAULT_PREFS)


def cli():
    """Simple CLI for manual inspection/testing."""
    action = sys.argv[1] if len(sys.argv) > 1 else "show"

    if action == "show":
        prefs = load()
        print(json.dumps(prefs, indent=2, ensure_ascii=False))
    elif action == "reset":
        if input("Reset all preferences? [y/N]: ").lower() == "y":
            save(dict(DEFAULT_PREFS))
            print("Preferences reset.")
    elif action == "path":
        print(PREFS_FILE)
    elif action == "is-first-run":
        print("yes" if is_first_run() else "no")
    else:
        print(f"Unknown action: {action}")
        print("Usage: xhs_prefs.py [show|reset|path|is-first-run]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
