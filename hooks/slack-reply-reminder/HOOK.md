---
name: slack-reply-reminder
description: "Injects a Slack reply reminder into agent bootstrap context"
metadata: {"openclaw":{"emoji":"📬","events":["agent:bootstrap"]}}
---

# Slack Reply Reminder Hook

Injects a prominent reminder about the Slack reply rule during agent bootstrap.

## What It Does

- Fires on `agent:bootstrap` (before workspace files are injected)
- Checks if the session is a Slack channel
- If so, injects a mandatory reply reminder file

## Configuration

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "slack-reply-reminder": {
          "enabled": true
        }
      }
    }
  }
}
```
