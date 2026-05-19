
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

## 2026-05-19: Xiaohongshu MCP Setup & Workflow Skill

### Correction: xiaohongshu.com redirects outside China
- **Category:** best_practice
- **Pattern-Key:** xhs-base-url-config
- **Context:** The `xpzouying/xiaohongshu-mcp` Go server hardcodes `www.xiaohongshu.com` in all 7 navigation/URL files. Outside mainland China, this domain redirects to `www.rednote.com`, breaking login QR and all navigation.
- **Fix:** Patched the Go server to read `XHS_BASE_URL` env var (defaults to `https://www.xiaohongshu.com`). Set it to `https://www.rednote.com` in our deployment.
- **Implication:** Anyone outside China running this MCP server must set `XHS_BASE_URL=https://www.rednote.com`.

### Best Practice: XHS MCP Workflow
- **Category:** best_practice
- **Pattern-Key:** xhs-mcp-workflow
- **Always check login before XHS requests** — use `python3 xhs_mcp_client.py --server xiaohongshu-mcp ensure-login --strip-qr-image`
- **Always check MCP health before operations** — `mcporter list xiaohongshu-mcp`
- **Rank results by likedCount + collectedCount** — this is the authoritative popularity metric
- **Parallelize detail fetches** — spawn concurrent mcporter calls for multiple notes
- **Push structured reports to GitHub** — `darinyu/deep-research-reports/blob/main/xhs/<keyword>/<YYYY-MM-DD>/<HHMMSS>/report.md`
- **Use :heart: for likes, :star: for saves** in Slack output
- **Keep summaries in original language (prefer Chinese)**

### Learning: MCP Tools via mcporter
- **Category:** insight
- **Use `mcporter call <server>.<tool>`** with underscores for params (e.g. `--feed_id` not `--id`, `--xsec_token` not `--xsecToken`)
- **Search returns `feeds[].id`** as `noteId` and `feeds[].xsecToken` — both needed for `get_feed_detail`
- **`get_feed_detail`** args: `--feed_id`, `--xsec_token`, `--load_all_comments true`, `--limit <n>`
