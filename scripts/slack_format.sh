#!/bin/bash
# Slack Format Filter — global italic-to-bold enforcement.
# Wrapper around slack_formatter.py for backward compatibility.
#
# Converts ALL italic to bold:
#   *single asterisk italic*  -> **bold**
#   _underscore italic_       -> **bold**
#
# Preserves code spans, code blocks, and existing **bold**.
#
# Usage:
#   echo "message" | ./slack_format.sh
#   ./slack_format.sh < input.txt
#   cat message.txt | ./slack_format.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/slack_formatter.py" "$@"
