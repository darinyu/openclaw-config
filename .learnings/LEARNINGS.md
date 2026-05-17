
## 2026-05-17: Slack formatting — underscore italic vs bold

**Category:** correction  
**Severity:** recurring (caught multiple times)  
**Status:** fixed in TOOLS.md  

**Issue:** In Slack messages, I was writing `_underscore italic_` for emphasis, which Slack renders as *italic*. Darin wants **bold** only, no italic.

**Root cause:** Standard Markdown training makes `_italic_` feel natural. I wasn't conscious of the pattern.

**Fix applied:**
1. Updated TOOLS.md Pre-Send Check 2 to emphasize writing `**bold**` from the start (standard Markdown, pipeline converts to Slack `*bold*`)
2. Added training-fix language: "reach for `**bold**`, never for underscore"
3. Removed conflicting instruction that said "use `*bold*` for Slack" (which contradicts the AGENTS.md rule of `**bold**` everywhere)

**Prevention:** The filter script (`scripts/slack_format.sh`) catches slips, but the goal is to never reach for underscore in the first place. Writing message to file → filter → send is the safety net, not the primary fix.
