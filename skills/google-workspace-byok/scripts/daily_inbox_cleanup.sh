#!/usr/bin/env bash
# Daily inbox cleanup - archives Promotions, Social, and Updates categories
# Never deletes - only removes INBOX and UNREAD labels
# Also learns from manual archives in the "Retro" tracking list

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ACCOUNT="personal"
LEARN_FILE="$SCRIPT_DIR/inbox_learned_senders.txt"

# Ensure learn file exists
touch "$LEARN_FILE"

echo "[$(date)] Starting daily inbox cleanup..."

# Archive all categorized unread emails
archive_category() {
  local label="$1"
  local query="in:inbox is:unread category:${label,,}"
  
  echo "  Processing ${label}..."
  node -e "
    const { google } = require('googleapis');
    const { getAuthClient } = require('./shared');
    
    async function run() {
      const auth = getAuthClient('$ACCOUNT');
      const gmail = google.gmail({ version: 'v1', auth });
      
      let pageToken = null;
      let total = 0;
      let batch = [];
      
      do {
        const res = await gmail.users.messages.list({
          userId: 'me', q: '$query', maxResults: 500, pageToken
        });
        const msgs = res.data.messages || [];
        if (msgs.length === 0) break;
        batch = batch.concat(msgs.map(m => m.id));
        total += msgs.length;
        pageToken = res.data.nextPageToken || null;
        
        if (batch.length >= 1000) {
          const chunk = batch.splice(0, 1000);
          await gmail.users.messages.batchModify({
            userId: 'me',
            requestBody: { ids: chunk, removeLabelIds: ['INBOX', 'UNREAD'] }
          });
          console.log('    Archived ' + total + ' ' + label + ' emails');
        }
      } while (pageToken);
      
      if (batch.length > 0) {
        await gmail.users.messages.batchModify({
          userId: 'me',
          requestBody: { ids: batch, removeLabelIds: ['INBOX', 'UNREAD'] }
        });
      }
      console.log('    Total ' + label + ': ' + total);
    }
    run().catch(e => { console.error(e.message); process.exit(1); });
  "
}

archive_category "Promotions"
archive_category "Social"
archive_category "Updates"

# Also archive learned senders (manually tracked)
echo "  Checking learned senders..."
if [ -s "$LEARN_FILE" ]; then
  while IFS= read -r sender; do
    [ -z "$sender" ] && continue
    node -e "
      const { google } = require('googleapis');
      const { getAuthClient } = require('./shared');
      const sender = '$sender';
      
      async function run() {
        const auth = getAuthClient('$ACCOUNT');
        const gmail = google.gmail({ version: 'v1', auth });
        
        const res = await gmail.users.messages.list({
          userId: 'me', q: 'from:' + sender + ' in:inbox', maxResults: 100
        });
        const ids = (res.data.messages || []).map(m => m.id);
        if (ids.length > 0) {
          for (let i = 0; i < ids.length; i += 1000) {
            const chunk = ids.slice(i, i + 1000);
            await gmail.users.messages.batchModify({
              userId: 'me',
              requestBody: { ids: chunk, removeLabelIds: ['INBOX', 'UNREAD'] }
            });
          }
        }
      }
      run().catch(e => {});
    "
  done < "$LEARN_FILE"
fi

echo "[$(date)] Cleanup complete!"
