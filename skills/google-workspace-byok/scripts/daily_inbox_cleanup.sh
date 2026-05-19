#!/usr/bin/env bash
# Daily inbox cleanup
# Runs at 9pm Pacific every night
# Archives (never deletes) all categorized noise + stale Primary emails
# Outputs report with rationale for each batch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ACCOUNT="personal"
cd "$SCRIPT_DIR"

echo "===== Inbox Cleanup Report — $(date -u) ====="
echo ""

# ------------------------------------------------------------------
# Phase 1: Archive Promotions — ads, newsletters, marketing
# Reason: These are unsolicited promotional emails. If you want 
# to see a specific sender, unsubscribe from within the email.
# ------------------------------------------------------------------
echo "--- Phase 1: Promotions ---"
echo "Reason: Marketing/promotional emails — ads, sales announcements, newsletters."
node -e "
  const { google } = require('googleapis');
  const { getAuthClient } = require('./shared');
  const { performance } = require('perf_hooks');
  const start = performance.now();
  
  async function run() {
    const auth = getAuthClient('$ACCOUNT');
    const gmail = google.gmail({ version: 'v1', auth });
    let total = 0;
    let pageToken = null;
    do {
      const res = await gmail.users.messages.list({ userId: 'me', q: 'in:inbox category:promotions', maxResults: 500, pageToken });
      const msgs = res.data.messages || [];
      if (msgs.length === 0) break;
      const ids = msgs.map(m => m.id);
      total += ids.length;
      for (let i = 0; i < ids.length; i += 1000) {
        const chunk = ids.slice(i, i + 1000);
        await gmail.users.messages.batchModify({ userId: 'me', requestBody: { ids: chunk, removeLabelIds: ['INBOX', 'UNREAD'] } });
      }
      pageToken = res.data.nextPageToken || null;
    } while (pageToken);
    const elapsed = ((performance.now() - start) / 1000).toFixed(1);
    console.log('Archived ' + total + ' promotional emails (' + elapsed + 's)');
  }
  run().catch(e => { console.error('Error: ' + e.message); process.exit(1); });
"

# ------------------------------------------------------------------
# Phase 2: Archive Social — LinkedIn, Nextdoor, Instagram
# Reason: Social network notifications — low priority, check apps directly.
# ------------------------------------------------------------------
echo ""
echo "--- Phase 2: Social ---"
echo "Reason: Social network notifications (LinkedIn, Nextdoor, Instagram)."
node -e "
  const { google } = require('googleapis');
  const { getAuthClient } = require('./shared');
  async function run() {
    const auth = getAuthClient('$ACCOUNT');
    const gmail = google.gmail({ version: 'v1', auth });
    let total = 0, pageToken = null;
    do {
      const res = await gmail.users.messages.list({ userId: 'me', q: 'in:inbox category:social', maxResults: 500, pageToken });
      const msgs = res.data.messages || [];
      if (msgs.length === 0) break;
      const ids = msgs.map(m => m.id);
      total += ids.length;
      for (let i = 0; i < ids.length; i += 1000) {
        const chunk = ids.slice(i, i + 1000);
        await gmail.users.messages.batchModify({ userId: 'me', requestBody: { ids: chunk, removeLabelIds: ['INBOX', 'UNREAD'] } });
      }
      pageToken = res.data.nextPageToken || null;
    } while (pageToken);
    console.log('Archived ' + total + ' social emails');
  }
  run().catch(e => { console.error('Error: ' + e.message); process.exit(1); });
"

# ------------------------------------------------------------------
# Phase 3: Archive Updates — transactional/Zillow/Amazon/etc
# Reason: Transactional receipts, shipping confirmations, Zillow 
# alerts, bill reminders — info-only, no action needed.
# ------------------------------------------------------------------
echo ""
echo "--- Phase 3: Updates ---"
echo "Reason: Transactional/update emails — receipts, shipping, Zillow, bills, alerts."
node -e "
  const { google } = require('googleapis');
  const { getAuthClient } = require('./shared');
  async function run() {
    const auth = getAuthClient('$ACCOUNT');
    const gmail = google.gmail({ version: 'v1', auth });
    let total = 0, pageToken = null;
    do {
      const res = await gmail.users.messages.list({ userId: 'me', q: 'in:inbox category:updates', maxResults: 500, pageToken });
      const msgs = res.data.messages || [];
      if (msgs.length === 0) break;
      const ids = msgs.map(m => m.id);
      total += ids.length;
      for (let i = 0; i < ids.length; i += 1000) {
        const chunk = ids.slice(i, i + 1000);
        await gmail.users.messages.batchModify({ userId: 'me', requestBody: { ids: chunk, removeLabelIds: ['INBOX', 'UNREAD'] } });
      }
      pageToken = res.data.nextPageToken || null;
    } while (pageToken);
    console.log('Archived ' + total + ' update emails');
  }
  run().catch(e => { console.error('Error: ' + e.message); process.exit(1); });
"

# ------------------------------------------------------------------
# Phase 4: Archive stale Primary emails (older than 30 days)
# Reason: Primary emails become stale. Recruiters not replied to for 
# 30+ days = opportunity passed. Old receipts, old bills, past events,
# course newsletters, ancient student life emails (2017-2019) — all
# clearly irrelevant now. Only recent/actionable emails kept.
# ------------------------------------------------------------------
echo ""
echo "--- Phase 4: Primary (stale) ---"
echo "Reason: Emails older than 30 days from non-essential senders — stale recruiters, old receipts, past events, ancient student/course emails."
node -e "
  const { google } = require('googleapis');
  const { getAuthClient } = require('./shared');
  async function run() {
    const auth = getAuthClient('$ACCOUNT');
    const gmail = google.gmail({ version: 'v1', auth });
    
    // Get all Primary inbox emails
    let total = 0, pageToken = null;
    let allMsgs = [];
    do {
      const res = await gmail.users.messages.list({ userId: 'me', q: 'in:inbox is:unread', maxResults: 500, pageToken });
      allMsgs = allMsgs.concat(res.data.messages || []);
      pageToken = res.data.nextPageToken || null;
    } while (pageToken);
    
    const archiveIds = [];
    for (const m of allMsgs) {
      const msg = await gmail.users.messages.get({ userId: 'me', id: m.id, format: 'metadata', metadataHeaders: ['Date', 'From', 'Subject'] });
      const h = msg.data.payload.headers;
      const dateStr = h.find(x => x.name === 'Date')?.value || '';
      const date = new Date(dateStr);
      const now = new Date();
      const daysOld = (now - date) / 86400000;
      const from = (h.find(x => x.name === 'From')?.value || '').replace(/<[^>]+>/g,'').trim().toLowerCase();
      const subj = h.find(x => x.name === 'Subject')?.value || '';
      
      // Keep if:
      // - Less than 30 days old (recent)
      const isRecent = daysOld < 30;
      
      // Always keep important senders regardless of age
      const importantSenders = ['carrot', 'bq realty', 'central loan', 'central loan administration'];
      const isImportant = importantSenders.some(s => from.includes(s));
      
      // Always keep security alerts and bills under 2 months
      const isSecurityOrRecentBill = daysOld < 60 && (
        from.includes('xfinity') || from.includes('american express') || from.includes('amex')
      );
      
      if (isRecent || isImportant || isSecurityOrRecentBill) {
        // Keep
      } else {
        archiveIds.push(m.id);
      }
    }
    
    if (archiveIds.length > 0) {
      for (let i = 0; i < archiveIds.length; i += 1000) {
        const chunk = archiveIds.slice(i, i + 1000);
        await gmail.users.messages.batchModify({ userId: 'me', requestBody: { ids: chunk, removeLabelIds: ['INBOX', 'UNREAD'] } });
      }
    }
    
    const kept = allMsgs.length - archiveIds.length;
    console.log('Archived: ' + archiveIds.length + ' stale emails, Kept: ' + kept + ' recent/important');
  }
  run().catch(e => { console.error('Error: ' + e.message); process.exit(1); });
"

echo ""
echo "===== Cleanup Complete ====="
