/**
 * Slack Auto-Reaction Hook for OpenClaw
 *
 * Auto-reacts with 👀 on every inbound Slack message to acknowledge receipt.
 * Fires on message:received event.
 */

const SLACK_TOKEN = process.env.SLACK_BOT_TOKEN || "";
const SLACK_API = "https://slack.com/api";

/**
 * Extract Slack channel + message_ts from the event context.
 */
function extractSlackIds(event) {
  // Try standard event fields first
  const channelId = event.context?.channelId || "";
  const metadata = event.context?.metadata || {};

  // Slack message ID is the ts — try common metadata keys
  const messageTs =
    metadata.messageId ||
    metadata.message_ts ||
    metadata.ts ||
    metadata.slackTs ||
    "";

  return { channelId, messageTs };
}

/**
 * Call Slack API reactions.add
 */
async function addReaction(channel, timestamp, reaction) {
  if (!channel || !timestamp) {
    return { ok: false, error: "missing channel or timestamp" };
  }

  const url = `${SLACK_API}/reactions.add`;
  const body = JSON.stringify({
    channel,
    timestamp,
    name: reaction,
  });

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${SLACK_TOKEN}`,
        "Content-Type": "application/json",
      },
      body,
    });
    const data = await resp.json();

    if (!data.ok && data.error !== "already_reacted") {
      console.error(`[slack-auto-reaction] API error: ${data.error}`);
    }

    return data;
  } catch (err) {
    console.error(`[slack-auto-reaction] fetch error: ${err.message}`);
    return { ok: false, error: err.message };
  }
}

const handler = async (event) => {
  // Only handle Slack message:received events
  if (event.type !== "message:received") {
    return;
  }

  // Skip if no bot token
  if (!SLACK_TOKEN) {
    return;
  }

  const { channelId, messageTs } = extractSlackIds(event);

  // Skip if not a Slack channel
  if (!channelId || !channelId.startsWith("C")) {
    return;
  }

  if (!messageTs) {
    console.warn("[slack-auto-reaction] No message timestamp found in event metadata");
    return;
  }

  // React with eyes
  await addReaction(channelId, messageTs, "eyes");
};

module.exports = handler;
module.exports.default = handler;
