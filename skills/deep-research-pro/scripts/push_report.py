#!/usr/bin/env python3
"""Push a research report to the deep-research-reports repo.

Usage: python3 push_report.py <report.md>

Reads GH_TOKEN from ~/.config/gh/hosts.yml or environment.
Uploads to: darinyu/deep-research-reports/main/reports/<topic>/report.md
"""
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error


REPO = "darinyu/deep-research-reports"
BRANCH = "main"


def get_token():
    env_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if env_token:
        return env_token

    gh_config = os.path.expanduser("~/.config/gh/hosts.yml")
    if os.path.exists(gh_config):
        with open(gh_config) as f:
            content = f.read()
        m = re.search(r"(gh[ops]_[a-zA-Z0-9]+)", content)
        if m:
            return m.group(1)

    print("ERROR: No GitHub token found. Set GH_TOKEN env var.", file=sys.stderr)
    sys.exit(1)


def github_api(method, path, data=None, token=None):
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "deep-research-pro-skill"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 404:
            return None  # Not found
        print(f"ERROR: HTTP {e.code} - {body}", file=sys.stderr)
        sys.exit(1)


def push_report(filepath, token):
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r") as f:
        content = f.read()

    # Derive topic slug from directory name containing the file
    dirname = os.path.basename(os.path.dirname(os.path.abspath(filepath)))
    topic_slug = dirname
    filename = os.path.basename(filepath)

    # GitHub path: reports/<topic-slug>/report.md
    repo_path = f"reports/{topic_slug}/{filename}"

    # Check if file already exists (need SHA to update)
    existing = github_api("GET", f"/repos/{REPO}/contents/{repo_path}?ref={BRANCH}", token=token)

    encoded = base64.b64encode(content.encode()).decode()

    commit_data = {
        "message": f"Add research report: {topic_slug}",
        "content": encoded,
        "branch": BRANCH,
    }

    if existing and "sha" in existing:
        commit_data["sha"] = existing["sha"]
        commit_data["message"] = f"Update research report: {topic_slug}"

    result = github_api("PUT", f"/repos/{REPO}/contents/{repo_path}", data=commit_data, token=token)

    if result and "content" in result:
        html_url = f"https://github.com/{REPO}/blob/{BRANCH}/{repo_path}"
        print(html_url)
        return html_url
    else:
        print("ERROR: Failed to push to repo", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: push_report.py <filepath>", file=sys.stderr)
        sys.exit(1)

    token = get_token()
    url = push_report(sys.argv[1], token)
    print(url)
