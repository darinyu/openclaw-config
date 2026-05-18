/**
 * Inbox cleanup tool for Darin.
 * Phase 1: Identify all promotional/unwanted emails and extract unsubscribe links.
 * Phase 2: Archive them.
 */

const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');
const { getAuthClient } = require('/data/.openclaw/workspace/skills/google-workspace-byok/scripts/shared');

const account = 'personal';
const auth = getAuthClient(account);
const gmail = google.gmail({ version: 'v1', auth });

function decodeBase64Url(str) {
  if (!str) return '';
  const base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  return Buffer.from(base64, 'base64').toString('utf8');
}

function getHeader(headers, name) {
  const h = headers.find(h => h.name.toLowerCase() === name.toLowerCase());
  return h ? h.value : null;
}

/**
 * Extract body text from message payload for unsubscribe link hunting.
 */
function extractBody(payload) {
  if (payload.body && payload.body.data) {
    return decodeBase64Url(payload.body.data);
  }
  if (payload.parts) {
    for (const part of payload.parts) {
      const nested = extractBody(part);
      if (nested) return nested;
    }
  }
  return '';
}

/**
 * Find unsubscribe links in an email body/headers.
 */
function findUnsubscribeLinks(body, headers) {
  const links = [];

  // 1. Check List-Unsubscribe header
  const listUnsub = getHeader(headers, 'List-Unsubscribe');
  if (listUnsub) {
    // RFC 2369: can be <url>, <mailto:addr>
    const urlMatches = listUnsub.match(/<([^>]+)>/g);
    if (urlMatches) {
      for (const m of urlMatches) {
        const clean = m.replace(/^<|>$/g, '');
        if (clean.startsWith('http')) links.push(clean);
      }
    }
  }

  // 2. Look for unsubscribe links in body
  const bodyLower = body.toLowerCase();
  const unsubPatterns = [
    /href="([^"]*unsub[^"]*)"/gi,
    /href='([^']*unsub[^']*)'/gi,
    /https?:\/\/[^\s"']*unsub[^\s"']*/gi,
    /https?:\/\/[^\s"']*opt[_-]?out[^\s"']*/gi,
    /https?:\/\/[^\s"']*email[_-]?pref[^\s"']*/gi,
  ];

  for (const pattern of unsubPatterns) {
    let match;
    while ((match = pattern.exec(body)) !== null) {
      const url = match[1] || match[0];
      if (!links.includes(url)) links.push(url);
    }
  }

  return links;
}

async function run() {
  // Get unread messages from categories that are likely promotional noise
  // Promotional category emails
  const promoQuery = 'in:inbox category:promotions is:unread';
  console.log(`Fetching promo emails...`);

  const listRes = await gmail.users.messages.list({
    userId: 'me',
    q: promoQuery,
    maxResults: 200,
  });

  const messageList = listRes.data.messages || [];
  console.log(`Found ${messageList.length} unread promo emails`);

  // Also get social newsletters
  const socialQuery = 'in:inbox category:social is:unread';
  const socialRes = await gmail.users.messages.list({
    userId: 'me',
    q: socialQuery,
    maxResults: 100,
  });
  const socialMessages = socialRes.data.messages || [];
  console.log(`Found ${socialMessages.length} unread social emails`);

  // Get all unread non-promo/non-social (Updates mostly)
  const updatesQuery = 'in:inbox category:updates is:unread';
  const updatesRes = await gmail.users.messages.list({
    userId: 'me',
    q: updatesQuery,
    maxResults: 200,
  });
  const updatesMessages = updatesRes.data.messages || [];
  console.log(`Found ${updatesMessages.length} unread updates emails`);

  // Process promo emails for unsubscribe info
  const unsubData = [];
  const senders = new Set();

  for (const m of messageList) {
    const msg = await gmail.users.messages.get({
      userId: 'me',
      id: m.id,
      format: 'full',
    });
    const headers = msg.data.payload.headers;
    const from = getHeader(headers, 'From');
    const subject = getHeader(headers, 'Subject');
    const body = extractBody(msg.data.payload);
    const unsubLinks = findUnsubscribeLinks(body, headers);

    const senderName = from ? from.replace(/<[^>]+>/, '').trim() : 'unknown';
    senders.add(senderName);

    unsubData.push({
      id: m.id,
      from,
      subject,
      unsubLinks,
    });

    if (unsubLinks.length > 0) {
      console.log(`\n${senderName}:`);
      console.log(`  Subject: ${subject}`);
      console.log(`  Unsubscribe: ${unsubLinks[0]}`);
    }
  }

  console.log(`\n\n=== SENDERS FOUND (${senders.size}) ===`);
  for (const s of [...senders].sort()) {
    console.log(`  - ${s}`);
  }

  console.log(`\n\n=== UNSUBSCRIBE LINKS ===`);
  for (const item of unsubData) {
    if (item.unsubLinks.length > 0) {
      console.log(`From: ${item.from}`);
      console.log(`  Link: ${item.unsubLinks[0]}`);
      console.log(``);
    } else {
      console.log(`From: ${item.from} (NO UNSUBSCRIBE LINK FOUND)`);
    }
  }

  // Return summary for the calling process
  console.log(`\n\n---JSON_SUMMARY---`);
  console.log(JSON.stringify({
    promoTotal: messageList.length,
    socialTotal: socialMessages.length,
    updatesTotal: updatesMessages.length,
    uniqueSenders: [...senders].sort(),
    unsubData: unsubData.filter(d => d.unsubLinks.length > 0).map(d => ({
      from: d.from,
      subject: d.subject,
      link: d.unsubLinks[0],
      id: d.id,
    })),
  }));
}

run().catch(err => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
