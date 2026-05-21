/**
 * Axiom Thread Logger Hook for OpenClaw
 *
 * Logs every Slack message (inbound + outbound) to Axiom with thread-level tracing.
 *
 * ID Scheme:
 *   thread_id = Slack thread_ts — shared across all turns in a thread
 *   turn_id   = Per agent-response-cycle UUID
 *   message_id = Slack message_ts — individual message
 *
 * Query in Axiom:
 *   ['openclaw'] | where thread_id == '<thread_ts>' | sort timestamp asc
 *   ['openclaw'] | where turn_id == '<turn_id>'
 */

// ── Config ──────────────────────────────────────────────────────

const AXIOM_API_KEY = process.env.AXIOM_API_KEY || "";
const AXIOM_DATASET = "openclaw";
const AXIOM_URL = `https://api.axiom.co/v1/datasets/${AXIOM_DATASET}/ingest`;

// In-memory turn tracking: sessionKey → { turn_id, thread_id, message_id }
const turnMap = new Map();

// ── Helpers ─────────────────────────────────────────────────────

function stamp() {
  return new Date().toISOString();
}

function shortUuid() {
  // 8-char hex
  return Math.random().toString(16).slice(2, 10);
}

function genTurnId() {
  const now = new Date();
  const ts = now.toISOString().replace(/[:.]/g, "").slice(0, 18);
  return `turn_${ts}_${shortUuid()}`;
}

function isSlackChannel(channelId) {
  if (!channelId || typeof channelId !== "string") return false;
  return (
    channelId.startsWith("C") ||
    channelId.startsWith("D") ||
    channelId.startsWith("G")
  );
}

/**
 * Send events to Axiom. Silent failure — never blocks the hook pipeline.
 */
async function axiomSend(events) {
  if (!AXIOM_API_KEY || !events || events.length === 0) return;

  try {
    const resp = await fetch(AXIOM_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${AXIOM_API_KEY}`,
        "Content-Type": "application/json",
        "User-Agent": "axiom-thread-logger/1.0",
      },
      body: JSON.stringify(events),
    });
    const result = await resp.json();
    if (result.failed > 0) {
      console.error(`[axiom-logger] ${result.failed} events failed`);
    }
  } catch (err) {
    console.error(`[axiom-logger] Axiom send error: ${err.message}`);
  }
}

/**
 * Extract thread_id from context.
 * Priority: context.metadata.threadId → context.metadata.thread_ts → message's own ts
 */
function extractThreadId(context, messageId) {
  const meta = context?.metadata || {};
  return meta.threadId || meta.thread_ts || meta.threadTs || messageId || "";
}

// ── Hook Handlers ───────────────────────────────────────────────

/**
 * Handle inbound messages: log to Axiom with thread_id + turn_id
 */
async function onMessageReceived(event) {
  const ctx = event.context || {};
  const channelId = ctx.channelId || "";
  const metadata = ctx.metadata || {};

  // Only Slack messages
  if (!isSlackChannel(channelId)) return;

  // Get message ID — try multiple keys
  const messageId =
    metadata.messageId ||
    metadata.message_ts ||
    metadata.ts ||
    metadata.slackTs ||
    "";

  if (!messageId) {
    console.warn("[axiom-logger] No messageId found for inbound message");
    return;
  }

  const threadId = extractThreadId(ctx, messageId);
  const turnId = genTurnId();

  // Store turn mapping for outbound matching
  turnMap.set(event.sessionKey, {
    turn_id: turnId,
    thread_id: threadId,
    inbound_message_id: messageId,
  });

  // Limit map size
  if (turnMap.size > 1000) {
    const firstKey = turnMap.keys().next().value;
    turnMap.delete(firstKey);
  }

  const senderId = metadata.senderId || ctx.from || "unknown";
  const content = (ctx.content || "").slice(0, 2000);

  await axiomSend([
    {
      timestamp: stamp(),
      thread_id: threadId,
      turn_id: turnId,
      message_id: messageId,
      session_key: event.sessionKey || "",
      channel_id: channelId,
      direction: "inbound",
      content,
      content_type: "user_message",
      sender: senderId,
    },
  ]);
}

/**
 * Handle outbound messages: log to Axiom with matching turn_id
 */
async function onMessageSent(event) {
  const ctx = event.context || {};
  const channelId = ctx.channelId || "";

  if (!isSlackChannel(channelId)) return;

  // Look up the turn_id from the inbound mapping
  const turnInfo = turnMap.get(event.sessionKey) || {};
  const turnId = turnInfo.turn_id || genTurnId();
  const threadId =
    turnInfo.thread_id ||
    ctx.metadata?.threadId ||
    ctx.metadata?.thread_ts ||
    ctx.metadata?.threadTs ||
    channelId;

  const content = (ctx.content || "").slice(0, 2000);
  const success = ctx.success !== false;

  await axiomSend([
    {
      timestamp: stamp(),
      thread_id: threadId,
      turn_id: turnId,
      message_id: ctx.metadata?.messageId || "",
      session_key: event.sessionKey || "",
      channel_id: channelId,
      direction: "outbound",
      content,
      content_type: "agent_reply",
      sender: "agent",
      success,
    },
  ]);
}

const handler = async (event) => {
  if (!event || typeof event !== "object") return;

  try {
    if (event.type === "message:received") {
      await onMessageReceived(event);
    } else if (event.type === "message:sent") {
      await onMessageSent(event);
    }
  } catch (err) {
    console.error(`[axiom-logger] handler error: ${err.message}`);
  }
};

module.exports = handler;
module.exports.default = handler;
