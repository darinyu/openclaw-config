---
name: axiom-thread-logger
description: "Logs Slack thread → turn interactions to Axiom for traceability"
metadata: {"openclaw":{"emoji":"📊","events":["message:received","message:sent"],"requires":{"env":["AXIOM_API_KEY"]}}}
---

# Axiom Thread Logger Hook

Logs every Slack message (inbound + outbound) to Axiom with thread-level tracing.
每个 thread 共享一个 ID，每个 turn 有自己的 sub-ID，可以连起来看也可以单独看。

## ID Scheme

- `thread_id` = Slack thread_ts (parent message timestamp). All turns in a
  thread share this ID.
- `turn_id` = Per-agent-response-cycle UUID. Generated on inbound, matched on outbound.
- `message_id` = Slack message_ts (individual message)

## Data Sent to Axiom

| Field | Description |
|-------|-------------|
| timestamp | ISO 8601 UTC |
| thread_id | Slack thread ts (shared across a thread) |
| turn_id | Unique per agent response cycle |
| message_id | Slack message ts |
| channel_id | Slack channel ID |
| direction | "inbound" or "outbound" |
| content | Message text (first 2000 chars) |
| content_type | "user_message" or "agent_reply" |
| sender | Sender name/ID |
| agent_id | Which agent handled it |

## Querying in Axiom

```apl
['openclaw']
| where thread_id == '1779315805.734799'
| sort timestamp asc
```

```apl
['openclaw']
| where turn_id == 'turn_abc123'
```
