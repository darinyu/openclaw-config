/**
 * Slack Reply Reminder Hook for OpenClaw
 * 
 * Injects a prominent reminder to always reply to Slack via message(action=send).
 * Fires on agent:bootstrap event before workspace files are injected.
 */

const REMINDER_NAME = 'SLACK_REPLY_REMINDER.md';
const REMINDER_PATH = REMINDER_NAME;

const REMINDER_CONTENT = `
## 🔴 CRITICAL: Slack Replies MUST use message(action=send)

When this session receives messages FROM SLACK (channel=slack in inbound context):
- Your normal final reply is PRIVATE and INVISIBLE on Slack.
- You MUST call message(action=send) to post visible output back to Slack.
- Failure to do this = Darin sees nothing = broken session.

### Quick Rules:
1. React FIRST (eyes for processing, thumbsup for ack)
2. Process the request
3. END with message(action=send) — never end with a private reply

### Thread Rules (NO EXCEPTIONS):
- reply_to_id exists? Use it as threadId. Reply in the same thread.
- Direct @-mention (no thread)? Reply in a thread under that message.
- General channel message? Post directly, no threadId.
- Filter message through scripts/slack_formatter.py before sending (no italic).
- Use Slack mrkdwn: bold = *asterisks*, links = <url|label>.

### Non-Slack sessions:
Ignore this reminder.
`.trim();

function isObject(value) {
  return !!value && typeof value === 'object';
}

function isInjectedReminderFile(value) {
  if (!isObject(value) || value.path !== REMINDER_PATH) {
    return false;
  }

  return (
    value.virtual === true ||
    value.content === REMINDER_CONTENT
  );
}

const handler = async (event) => {
  // Safety checks for event structure
  if (!event || typeof event !== 'object') {
    return;
  }

  // Only handle agent:bootstrap events
  if (event.type !== 'agent' || event.action !== 'bootstrap') {
    return;
  }

  // Safety check for context
  if (!event.context || typeof event.context !== 'object') {
    return;
  }

  // Skip sub-agent sessions to avoid bootstrap issues
  const sessionKey = event.sessionKey || '';
  if (sessionKey.includes(':subagent:')) {
    return;
  }

  // Inject the reminder as a virtual bootstrap file
  if (Array.isArray(event.context.bootstrapFiles)) {
    const occupiedByOtherFile = event.context.bootstrapFiles.some(
      (file) => isObject(file) && file.path === REMINDER_PATH && !isInjectedReminderFile(file),
    );
    if (occupiedByOtherFile) {
      return;
    }

    const cleanedBootstrapFiles = event.context.bootstrapFiles.filter(
      (file, index, files) =>
        !isInjectedReminderFile(file) ||
        files.findIndex((candidate) => isInjectedReminderFile(candidate)) === index,
    );

    const reminderFile = {
      name: REMINDER_NAME,
      path: REMINDER_PATH,
      content: REMINDER_CONTENT,
      missing: false,
      virtual: true,
    };

    const existingIndex = cleanedBootstrapFiles.findIndex((file) => isInjectedReminderFile(file));
    if (existingIndex === -1) {
      cleanedBootstrapFiles.push(reminderFile);
    } else {
      cleanedBootstrapFiles[existingIndex] = reminderFile;
    }

    event.context.bootstrapFiles = cleanedBootstrapFiles;
  }
};

module.exports = handler;
module.exports.default = handler;
