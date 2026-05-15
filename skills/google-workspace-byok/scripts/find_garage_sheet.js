const { google } = require('googleapis');
const shared = require('./shared.js');

async function main() {
  const auth = shared.getAuthClient('personal');
  const drive = google.drive({ version: 'v3', auth });

  // Search for spreadsheets with garage-related names
  const queries = [
    "mimeType='application/vnd.google-apps.spreadsheet' and name contains 'garage'",
    "mimeType='application/vnd.google-apps.spreadsheet' and name contains 'contractor'",
    "mimeType='application/vnd.google-apps.spreadsheet' and name contains 'receipt'",
    "mimeType='application/vnd.google-apps.spreadsheet' and name contains 'project'",
  ];

  for (const q of queries) {
    console.log('\n--- Query: ' + q + ' ---');
    const res = await drive.files.list({
      q: q,
      fields: 'files(id, name, createdTime, modifiedTime)',
      orderBy: 'modifiedTime desc',
    });
    const files = res.data.files;
    if (files && files.length > 0) {
      for (const f of files) {
        console.log('  📄 ' + f.name);
        console.log('     https://docs.google.com/spreadsheets/d/' + f.id + '/edit');
        console.log('     Modified: ' + f.modifiedTime);
      }
    } else {
      console.log('  No results found.');
    }
  }

  // Also search all recent sheets (last 3 months) and check with broader terms
  const threeMonthsAgo = new Date();
  threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
  const timeFilter = threeMonthsAgo.toISOString();

  console.log('\n--- All spreadsheets modified in last 3 months ---');
  const allRes = await drive.files.list({
    q: "mimeType='application/vnd.google-apps.spreadsheet' and modifiedTime >= '" + timeFilter + "'",
    fields: 'files(id, name, createdTime, modifiedTime)',
    orderBy: 'modifiedTime desc',
  });
  const allFiles = allRes.data.files;
  if (allFiles && allFiles.length > 0) {
    for (const f of allFiles) {
      console.log('  📄 ' + f.name);
      console.log('     https://docs.google.com/spreadsheets/d/' + f.id + '/edit');
      console.log('     Modified: ' + f.modifiedTime);
    }
  } else {
    console.log('  No recent sheets found.');
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  if (err.response) console.error('   Details:', JSON.stringify(err.response.data, null, 2));
  process.exit(1);
});
