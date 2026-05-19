#!/bin/bash
# git-sync.sh — Commit and push workspace changes to GitHub
# Never checks in credentials (handled by .gitignore + explicit safety checks)
#
# Runs as an OpenClaw cron job.
# Output: structured JSON to stdout for cron job to parse.
# Exits silently when there's nothing to commit.

set -euo pipefail

WORKSPACE="/data/.openclaw/workspace"
cd "$WORKSPACE"

# ---- Safety check: ensure credential patterns are not being tracked ----
# Abort if any file matching credential patterns is staged or tracked
CRED_PATTERNS=(
  "credentials.json"
  "*.key"
  "*.pem"
  ".env"
  "*-token*"
  "*.oauth*"
  "*client_secret*"
)

for pattern in "${CRED_PATTERNS[@]}"; do
  if git ls-files "$pattern" 2>/dev/null | grep -q .; then
    echo "[git-sync] SAFETY ABORT: credential pattern '$pattern' is tracked!"
    echo "[git-sync] Files: $(git ls-files "$pattern" | tr '\n' ' ')"
    exit 1
  fi
done

# ---- Safety check 2: gitignore should ignore these patterns ----
# Warn if any new untracked file matches credential patterns
for pattern in "${CRED_PATTERNS[@]}"; do
  if git ls-files --others --exclude-standard "$pattern" 2>/dev/null | grep -q .; then
    echo "[git-sync] SAFETY WARNING: credential pattern '$pattern' is untracked and not gitignored."
    echo "[git-sync] Files: $(git ls-files --others --exclude-standard "$pattern" | tr '\n' ' ')"
    echo "[git-sync] Skipping commit until .gitignore is updated."
    exit 1
  fi
done

# ---- Check for any changes ----
if ! git diff --quiet HEAD && git status --porcelain | grep -q .; then
  # Collect file list before staging (status --porcelain shows staged/unstaged changes)
  FILE_LIST=$(git status --porcelain | sed 's/^.. //' | sort -u | head -20)
  CHANGED_COUNT=$(echo "$FILE_LIST" | wc -l)
  TRUNCATED=false
  TOTAL_COUNT=$(git status --porcelain | sed 's/^.. //' | sort -u | wc -l)
  if [ "$CHANGED_COUNT" -lt "$TOTAL_COUNT" ]; then
    TRUNCATED=true
  fi

  git add -A

  # Generate commit message
  TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
  CHANGES=$(git diff --cached --stat --no-color | tail -1 || echo "0 files changed")

  git commit \
    -m "Auto-sync: workspace changes at $TIMESTAMP" \
    -m "$CHANGES"

  # Capture commit SHA
  COMMIT_SHA=$(git rev-parse HEAD)
  COMMIT_SHORT=$(git rev-parse --short HEAD)

  # Push
  echo "[git-sync] Pushing to origin..."
  PUSH_RESULT=""
  if git push origin master 2>&1; then
    PUSH_RESULT="pushed"
  else
    PUSH_RESULT="local-only"
    echo "[git-sync] Push failed (network? auth?) — commit saved locally"
  fi

  # Output structured JSON for the cron job
  FILE_LIST_JSON=$(echo "$FILE_LIST" | jq -R -s -c 'split("\n") | map(select(. != ""))' 2>/dev/null || echo "[]")
  cat <<EOF
{"event":"commit","count":$TOTAL_COUNT,"short_sha":"$COMMIT_SHORT","sha":"$COMMIT_SHA","push":"$PUSH_RESULT","truncated":$TRUNCATED,"files":$FILE_LIST_JSON}
EOF
else
  echo '{"event":"noop"}'
fi
