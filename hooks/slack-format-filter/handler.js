/**
 * Slack Format Filter Hook for OpenClaw
 *
 * Injects a format filter reminder into agent bootstrap context.
 * Tells the agent to use **bold** and never *italic* or _italic_.
 */

const FILTER_NAME = "SLACK_FORMAT_FILTER.md";
const FILTER_PATH = FILTER_NAME;

const FORMAT_RULES = `
## 🎨 Slack Format Filter (Auto-Applied)

The following formatting rules are ENFORCED automatically on every outbound Slack message:

### Rule: Bold Only — Zero Italic
- Use **double asterisks** for emphasis: \`**bold**\`
- Never use \`_underscore_\` or \`*single asterisk*\` for formatting
- The pipeline converts \`**bold**\` → Slack \`*bold*\` automatically

### ⚠️ Critical: No space after **
- \`**bold text**\` ✓ (correct — ** directly touches text)
- \`** text**\` ✗ (WRONG — space breaks markdown parsing, shows literal **)

### Pre-Send Ritual (MANDATORY)
Before ANY \`message(action=send)\` call to Slack:
1. Write message to \`/tmp/slack_msg.txt\`
2. Run: \`python3 /data/.openclaw/workspace/scripts/slack_formatter.py < /tmp/slack_msg.txt\`
3. Use the FILTERED output as the message param
4. Never skip this. Never reason your way out.
`.trim();

function isObject(value) {
  return !!value && typeof value === "object";
}

function isInjectedFile(value) {
  if (!isObject(value) || value.path !== FILTER_PATH) return false;
  return value.virtual === true || value.content === FORMAT_RULES;
}

const handler = async (event) => {
  if (!event || typeof event !== "object") return;
  if (event.type !== "agent" || event.action !== "bootstrap") return;
  if (!event.context || typeof event.context !== "object") return;

  const sessionKey = event.sessionKey || "";
  if (sessionKey.includes(":subagent:")) return;

  if (Array.isArray(event.context.bootstrapFiles)) {
    const occupied = event.context.bootstrapFiles.some(
      (f) => isObject(f) && f.path === FILTER_PATH && !isInjectedFile(f),
    );
    if (occupied) return;

    const cleaned = event.context.bootstrapFiles.filter(
      (f, i, arr) =>
        !isInjectedFile(f) ||
        arr.findIndex((c) => isInjectedFile(c)) === i,
    );

    const file = {
      name: FILTER_NAME,
      path: FILTER_PATH,
      content: FORMAT_RULES,
      missing: false,
      virtual: true,
    };

    const existingIdx = cleaned.findIndex((f) => isInjectedFile(f));
    if (existingIdx === -1) {
      cleaned.push(file);
    } else {
      cleaned[existingIdx] = file;
    }

    event.context.bootstrapFiles = cleaned;
  }
};

module.exports = handler;
module.exports.default = handler;
