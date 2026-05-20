#!/bin/bash
# slack_send.sh — Pre-send hook for Slack messages.
# Auto-filters italic to bold, then prints the filtered message.
#
# Usage:
#   echo "Your **bold** message here" | ./scripts/slack_send.sh
#   ./scripts/slack_send.sh < /tmp/msg.txt
#   cat file.txt | ./scripts/slack_send.sh
#
# Output: The filtered message ready for message(action=send).
# Any italic (*text* or _text_) is converted to **bold** automatically.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FILTERED=$(python3 "$SCRIPT_DIR/slack_formatter.py")

# Print the filtered output
echo "$FILTERED"
