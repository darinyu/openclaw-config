# RETRO.md — Things to Review / Keep Track Of

## 2026-05-20: OpenAI Revenue Deep Research — Failed to Reply in Thread

**What happened:** Darin asked in `#random` to do "openai revenue deep research." I received the message, reacted with eyes, read the deep-research skill, prepared a clarifying question — but never sent it to Slack. Two follow-up messages in the thread went unanswered. It took a third @-mention to get a response.

**Root cause:** Session `eba67a9f` (05:05 UTC) replied with text-only output in the private session instead of calling `message(action=send)` to post to Slack. This is a known failure mode documented in TOOLS.md but the model output text instead of a tool call.

**Contributing factors:**
- The clarifying question felt like "thinking out loud" rather than a message that needed sending
- The model didn't recognize that a text reply in a Slack-triggered session is invisible
- The `wasMentioned: true` signal was present but didn't trigger `message(action=send)` behavior

**Fix needed:** Harder guardrail — maybe add a pre-check: "If this session was triggered by a Slack message and my final output is text, call message(action=send) before stopping."
