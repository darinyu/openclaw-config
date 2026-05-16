#!/bin/bash
# git-sync.sh — Commit and push workspace changes to GitHub
# Never checks in credentials (handled by .gitignore + explicit safety checks)
#
# Runs as an OpenClaw cron job.
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
  # Something changed
  CHANGED_FILES=$(git status --porcelain | wc -l)

  echo "[git-sync] $CHANGED_FILES file(s) changed, committing..."

  git add -A

  # Generate commit message
  TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
  CHANGES=$(git diff --cached --stat --no-color | tail -1 || echo "0 files changed")

  git commit \
    -m "Auto-sync: workspace changes at $TIMESTAMP" \
    -m "$CHANGES"

  # Push
  echo "[git-sync] Pushing to origin..."
  git push origin master 2>&1 || echo "[git-sync] Push failed (network? auth?) — commit saved locally"

  echo "[git-sync] Done."
else
  echo "[git-sync] No changes to commit."
fi
