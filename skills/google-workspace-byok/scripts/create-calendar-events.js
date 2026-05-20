/**
 * Quick script to create calendar events using google-workspace-byok auth.
 * Usage: node create-events.js --account <label> --calendar <calendarId>
 *
 * Reads events from STDIN as JSON array.
 */

const { google } = require('googleapis');
const { getAuthClient } = require('/data/.openclaw/workspace/skills/google-workspace-byok/scripts/shared');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const match = argv[i].match(/^--(.+)$/);
    if (match) {
      const key = match[1];
      const val = argv[i + 1];
      if (val && !val.startsWith('--')) {
        args[key] = val;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

const args = parseArgs(process.argv);
const account = args.account || 'personal';
const calendarId = args.calendar || 'primary';

async function run() {
  const auth = getAuthClient(account);
  const calendar = google.calendar({ version: 'v3', auth });

  // Read events JSON from stdin
  const chunks = [];
  process.stdin.on('data', (chunk) => chunks.push(chunk));
  process.stdin.on('end', async () => {
    const input = Buffer.concat(chunks).toString().trim();
    const events = JSON.parse(input);

    if (!Array.isArray(events) || events.length === 0) {
      console.error('Expected a JSON array of events');
      process.exit(1);
    }

    const results = [];
    for (const event of events) {
      try {
        const res = await calendar.events.insert({
          calendarId,
          requestBody: {
            summary: event.summary,
            description: event.description || '',
            location: event.location || '',
            start: {
              dateTime: event.start,
              timeZone: event.timeZone || 'America/Los_Angeles',
            },
            end: {
              dateTime: event.end,
              timeZone: event.timeZone || 'America/Los_Angeles',
            },
            reminders: event.reminders || { useDefault: true },
            attendees: event.attendees || [],
          },
        });
        results.push({
          status: 'created',
          id: res.data.id,
          summary: res.data.summary,
          start: res.data.start.dateTime || res.data.start.date,
          htmlLink: res.data.htmlLink,
        });
        console.log(`✓ Created: ${event.summary} (${event.start})`);
      } catch (err) {
        console.error(`✗ Failed: ${event.summary}: ${err.message}`);
        results.push({ status: 'error', summary: event.summary, error: err.message });
      }
    }

    console.log('\n---\n' + JSON.stringify(results, null, 2));
  });
}

run().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
