#!/usr/bin/env bash
# Archive all promotional, social, and transactional noise from Gmail inbox
# Then list unsubscribe links for browser processing
set -e

SCRIPT_DIR="/data/.openclaw/workspace/skills/google-workspace-byok/scripts"
ACCOUNT="personal"

# Step 1: Archive all promotional emails (remove INBOX label)
echo "=== Archiving CATEGORY_PROMOTIONS emails ==="
node -e "
const { google } = require('googleapis');
const { getAuthClient } = require('./shared');

async function run() {
  const auth = getAuthClient('${ACCOUNT}');
  const gmail = google.gmail({ version: 'v1', auth });

  const queries = [
    { label: 'Promotions', q: 'in:inbox category:promotions is:unread' },
    { label: 'Social', q: 'in:inbox category:social is:unread' },
  ];

  for (const { label, q } of queries) {
    console.log('Fetching ' + label + '...');
    let pageToken = null;
    let total = 0;
    let batch = [];

    do {
      const res = await gmail.users.messages.list({
        userId: 'me',
        q: q,
        maxResults: 500,
        pageToken: pageToken,
      });

      const msgs = res.data.messages || [];
      if (msgs.length === 0) break;

      batch = batch.concat(msgs.map(m => m.id));
      total += msgs.length;
      pageToken = res.data.nextPageToken || null;

      // Process in batches of 100
      while (batch.length >= 100) {
        const chunk = batch.splice(0, 100);
        await gmail.users.messages.batchModify({
          userId: 'me',
          requestBody: {
            ids: chunk,
            removeLabelIds: ['INBOX', 'UNREAD'],
          },
        });
        console.log('  Archived ' + chunk.length + ' ' + label + ' emails...');
      }
    } while (pageToken);

    // Remaining
    if (batch.length > 0) {
      await gmail.users.messages.batchModify({
        userId: 'me',
        requestBody: {
          ids: batch,
          removeLabelIds: ['INBOX', 'UNREAD'],
        },
      });
      console.log('  Archived final ' + batch.length + ' ' + label + ' emails');
    }

    console.log('Total ' + label + ' archived: ' + total);
  }
}
run().catch(e => { console.error(e); process.exit(1); });
" 2>&1
