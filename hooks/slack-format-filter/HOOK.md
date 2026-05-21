---
name: slack-format-filter
description: "Auto-converts _italic_ and *italic* to **bold** in outbound Slack messages"
metadata: {"openclaw":{"emoji":"🎨","events":["agent:bootstrap"],"requires":{"bins":["node"]}}}
---

# Slack Format Filter Hook

Injects format instructions into the agent bootstrap so the agent knows
pre-send formatting is handled automatically via the pipeline formatter.

**NOTE:** Outbound message content rewriting requires a plugin hook
(`message_sending`), not an internal hook. This internal hook uses the
next-best approach: injecting format rules into the agent's context.

## What It Does

- Fires on `agent:bootstrap`
- Injects `SLACK_FORMAT_FILTER.md` as a virtual bootstrap file
- The file tells the agent that italic is already auto-converted to bold
- Works alongside `scripts/slack_formatter.py` for actual conversion

## Configuration

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "slack-format-filter": {
          "enabled": true
        }
      }
    }
  }
}
```
