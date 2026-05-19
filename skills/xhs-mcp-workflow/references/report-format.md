# XHS Search Report Data Format

Report files are stored at `darinyu/deep-research-reports/main/xhs/<keyword>/<YYYY-MM-DD>/<HHMMSS>/report.md`

## Report Structure

```markdown
# XHS Search: <keyword>

**Date:** YYYY-MM-DDTHH:MM:SSZ
**Account:** <XHS account used>
**Total results found:** N
**Top results analyzed:** M

## Rankings (by likes + collects)

### #1 | <title> — 👍N / ⭐N / 💬N
- **Author:** <nickname>
- **Link:** https://www.xiaohongshu.com/explore/<feed_id>
- **Description:** <excerpt of text content>

**Top comments:**
- <comment 1>
- <comment 2>

### #2 | <title> — ...
```

## Key Fields

| Field | Source | Notes |
|---|---|---|
| feed_id | search result `.id` | Used for permalink |
| xsec_token | search result `.xsecToken` | Required for detail fetch |
| title | detail `.title` | If empty, use `.displayTitle` |
| desc | detail `.desc` | Full text content |
| likedCount | detail `.interactInfo.likedCount` | String, may contain commas |
| collectedCount | detail `.interactInfo.collectedCount` | String, may contain commas |
| commentCount | detail `.interactInfo.commentCount` | String |
| nickname | detail `.user.nickname` | Author display name |

## Slack Output Conventions

- *bold* for title/emphasis
- :heart: for likes
- :star: for collects/saves
- :speech_balloon: for comment count
- Rank descending by (likedCount + collectedCount)
- Link with `<https://www.xiaohongshu.com/explore/<id>|title>`
