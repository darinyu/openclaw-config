#!/usr/bin/env python3
"""Create a private GitHub gist from a report file.

Usage: python3 create_gist.py <filepath> <description>

Reads GH_TOKEN from ~/.config/gh/hosts.yml or environment.
"""
import json
import os
import re
import sys
import urllib.request


def get_token():
    """Get GitHub token from env, gh config, or fallback paths."""
    env_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if env_token:
        return env_token

    # Try gh config file
    gh_config = os.path.expanduser("~/.config/gh/hosts.yml")
    if os.path.exists(gh_config):
        with open(gh_config) as f:
            content = f.read()
        m = re.search(r"(gh[ops]_[a-zA-Z0-9]+)", content)
        if m:
            return m.group(1)

    return None


def create_gist(filepath, description, token):
    if not token:
        print("ERROR: No GitHub token found. Set GH_TOKEN env var.", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r") as f:
        content = f.read()

    filename = os.path.basename(filepath)

    payload = json.dumps({
        "description": description,
        "public": False,
        "files": {
            filename: {"content": content}
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/gists",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "deep-research-pro-skill"
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result["html_url"]
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} - {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: create_gist.py <filepath> <description>", file=sys.stderr)
        sys.exit(1)

    token = get_token()
    url = create_gist(sys.argv[1], sys.argv[2], token)
    print(url)
