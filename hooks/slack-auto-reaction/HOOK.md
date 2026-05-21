---
name: slack-auto-reaction
description: "Auto-reacts with 👀 on every inbound Slack message"
metadata: {"openclaw":{"emoji":"👀","events":["message:received"],"requires":{"env":["SLACK_BOT_TOKEN"]}}}
---

# Slack Auto-Reaction Hook

Auto-reacts with 👀 on every inbound Slack message to acknowledge receipt.

## What It Does

- Fires on `message:received` (inbound message from any channel)
- Detects if it's a Slack channel
- Calls Slack API `reactions.add` with `eyes` emoji
- Skips non-Slack channels

## Configuration

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "slack-auto-reaction": {
          "enabled": true,
          "env": {
            "SLACK_BOT_TOKEN": "xoxb-your-bot-token"
          }
        }
      }
    }
  }
}
```
