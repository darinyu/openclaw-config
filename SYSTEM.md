# SYSTEM.md — Comprehensive Automation Reference

*Generated 2026-05-29. Keep in sync with cloud.openclaw.ai configuration.*

---

## 1. CRON JOBS — 11 Scheduled Tasks

All configured via cloud.openclaw.ai. Each job = isolated ephemeral session, model = DeepSeek, schedule = cron expression + America/Los_Angeles TZ. Output goes through OpenClaw's message routing back to Slack.

### 1. Daily Weather Brief
- **Schedule:** 7:00 AM PT daily
- **Target:** #weather (C0B420KCYAV)
- **Action:** Fetch wttr.in weather for Sunnyvale, SF, Wuhan, Linyi
- **Format:** Mobile-readable, emoji-coded

### 2. Personal Morning Brief
- **Schedule:** 7:30 AM PT daily
- **Target:** DM to Darin
- **Action:** Calendar check (personal + family + work), baby prep reminders, anniversary countdown. Uses Google Calendar API

### 3. Tech + Finance Daily Digest
- **Schedule:** 8/11/14/17 PT, weekdays only
- **Target:** #learning (C07LV6XMHNJ)
- **Action:** Scrape HN top 15 (10 AI + 5 general), tech news top 10, finance digest. Annotate tech vocab for Paofu (B2+ English)

### 4. Stock Pre-Market Deep Analysis
- **Schedule:** 6:00 AM PT, Mon-Fri
- **Target:** stock channel (C0B48T730DT)
- **Action:** Deep analysis on 23 tickers (AAPL MSFT GOOGL META AMZN NVDA AMD TSM AVGO CRM DDOG SNOW NET CRWV NBIS MRVL APP SNDK QQQ SMH XLK SOXX), strategy signal check, options opps. Uses TradingView MCP

### 5. Vocabulary Evening Quiz
- **Schedule:** 8:30 PM PT daily
- **Target:** #learning (C07LV6XMHNJ), @Paofu
- **Action:** Auto-quiz from accumulated vocab words. Interactive with Paofu

### 6. Inbox Nightly Cleanup
- **Schedule:** 9:00 PM PT daily
- **Target:** #cron-status (C0B4EK31NCU)
- **Action:** Gmail archiving — Promotions, Social, Updates folders. Archive only, no deletes

### 7. Daily Journal Summary
- **Schedule:** 11:59 PM PT daily
- **Target:** #cron-status (C0B4EK31NCU)
- **Action:** Save polished journal entry to memory/journal/ from daily memory file

### 8. MCP Health Check
- **Schedule:** Hourly 8AM-11PM PT
- **Target:** #cron-status (C0B4EK31NCU)
- **Action:** Ping xiaohongshu-mcp + tradingview-mcp health. Auto-restart if down. Uses healthcheck skill

### 9. Correction Retrospective
- **Schedule:** 4:00 AM PT daily
- **Target:** #cron-status (C0B4EK31NCU)
- **Action:** Scan last 24h sessions for Darin corrections, verify fixes were applied, apply any missed ones

### 10. Git Auto-Sync
- **Schedule:** Every 6 hours
- **Target:** #cron-status (C0B4EK31NCU)
- **Action:** git add/commit/push workspace changes to GitHub, report changed files list

### 11. Memory Dreaming Promotion
- **Schedule:** 3:00 AM UTC daily
- **Target:** None (internal, system-managed)
- **Action:** OpenClaw built-in — promotes short-term memories from memory/ files to MEMORY.md. No output channel

### Channel Map
- C0B48T730DT = stock channel
- C0B420KCYAV = #weather
- C07LV6XMHNJ = #learning
- C0B4EK31NCU = #cron-status (fallback)

---

## 2. MEMORY SYSTEM

### File Structure
- `~/.openclaw/workspace/MEMORY.md` — Long-term curated memory (durable, hand-picked)
- `~/.openclaw/workspace/memory/YYYY-MM-DD.md` — Daily raw activity logs
- `~/.openclaw/workspace/memory/journal/YYYY-MM-DD.md` — Polished journal entries (from cron #7)

### Lifecycle
1. **Session Start:** Read MEMORY.md + today's + yesterday's daily files for context
2. **During Session:** Write notes to memory/YYYY-MM-DD.md (decisions, context, lessons)
3. **Memory Dreaming (3AM UTC):** Built-in OpenClaw plugin (memory-core) scans short-term memory files, finds high-scoring entries, auto-promotes them to MEMORY.md with metadata tags
4. **Daily Journal (11:59PM PT):** Cron #7 — extract key events from daily memory file, polish, save to memory/journal/
5. **Memory Cleanup:** Every few heartbeats review recent daily files, distill key learnings, update MEMORY.md, rotate outdated info

### Storage
- Local filesystem only (no external DB)
- ~30+ daily memory files dating back to May 2026
- MEMORY.md has promoted entries sorted by score

### Key Content in MEMORY.md
- Identity (Darin, Paofu, baby girl due Sep 5 2026)
- Paofu English annotation rules
- Slack routing protocols (critical learned lessons)
- Tool configurations
- Cron job specs
- Model preferences (DeepSeek > Gemini > ChatGPT)

### What's NOT in Memory
- Credentials (tokens, API keys — stored in env/OpenClaw secrets)
- Raw conversation logs (session-only, ephemeral)
- Large files (purpose-built separate storage)

---

## 3. SKILLS INVENTORY

Skills are tool definitions living in `skills/` dir. Each has a SKILL.md defining how the tool works.

### Trading & Finance
- stock-market-pro — Full stock analysis pipeline
- stock-strategy-monitor — Pre-market signal checks (cron #4)
- trading-agent — Multi-agent LLM stock analysis
- tradingview-mcp — TradingView MCP tools
- market-environment-analysis — Macro environment checks

### Search & Research
- tavily-search — Web search via Tavily
- deep-research-pro — Structured deep research (pushes to GitHub)
- summarize-pro — Summarization tool
- browser-automation — Web browsing via Playwright

### Xiaohongshu (小红书)
- xhs-login, xhs-profile, xhs-search, xhs-explore, xhs-interact
- xhs-food-research, xhs-trip-planner, xhs-content-plan, xhs-mcp-workflow
- xiaohongshu-mcp-openclaw — MCP integration
- xiaohongshu-search-summarizer — Search + summarize

### Communication & Productivity
- google-workspace-byok — Gmail + Calendar API
- google-calendar — Calendar read/write
- slack — Slack bot integration
- himalaya — Email client
- post-to-xhs — XHS posting
- flight-search, flight-research — Flight booking
- hotel-research — Hotel booking

### Agent Infrastructure
- skill-creator — Create new skills
- self-improvement — Self-modification skill
- healthcheck — Health check (cron #8)
- weather — Weather fetcher (cron #1)
- humanizer — Writing style tuning
- canvas — UI canvas
- diagram-maker, meme-maker — Media generation
- tts, music_generate, video_generate — Media tools
- taskflow, taskflow-inbox-triage — Task management
- clawhub — Skill marketplace

### Debug Tools
- node-connect, node-inspect-debugger, python-debugpy
- openai-whisper-api — Audio transcription

---

## 4. CONFIGURATION NOTES

- Skills managed in `openclaw.json` under skills.entries
- Each skill can be enabled/disabled
- Some have API keys stored (e.g., image-lab has GEMINI_API_KEY)
- Skills auto-install from ClawHub when referenced
- New skills created with skill-creator skill using SKILL.md template
