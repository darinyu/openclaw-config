/**
 * Axiom Trace — Full agent-turn tracing to Axiom
 *
 * Captures:
 *  - Inbound message (with thread_id from Slack)
 *  - Prompt being sent to the model
 *  - Tool calls + results
 *  - Model calls (metadata only — no raw response)
 *  - Final agent reply
 *
 * ID scheme:
 *   thread_id = Slack thread_ts — shared across all turns in a thread
 *   turn_id   = Generated per agent response cycle
 *   step_id   = Sequential step within a turn (1, 2, 3...)
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

// ── Config ──────────────────────────────────────────────────────

const AXIOM_URL = (dataset: string) =>
  `https://api.axiom.co/v1/datasets/${dataset}/ingest`;

const AXIOM_API_KEY = () => process.env.AXIOM_API_KEY;

// ── In-memory turn tracking ─────────────────────────────────────

// sessionKey → { turn_id, thread_id, step_count }
const turnState = new Map<string, {
  turn_id: string;
  thread_id: string;
  step: number;
}>();

// ── Helpers ─────────────────────────────────────────────────────

function stamp(): string {
  return new Date().toISOString();
}

function shortUuid(): string {
  return Math.random().toString(16).slice(2, 10);
}

function genTurnId(): string {
  const now = new Date();
  const ts = now.toISOString().replace(/[:.]/g, "").slice(0, 18);
  return `turn_${ts}_${shortUuid()}`;
}

function isSlackChannel(channelId: string): boolean {
  return !!(channelId && /^[CDG]/.test(channelId));
}

async function axiomSend(events: Record<string, unknown>[], dataset: string) {
  const key = AXIOM_API_KEY();
  if (!key || events.length === 0) return;

  try {
    const resp = await fetch(AXIOM_URL(dataset), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        "User-Agent": "axiom-trace/1.0",
      },
      body: JSON.stringify(events),
    });
    const result: any = await resp.json();
    if (result.failed > 0) {
      console.error(`[axiom-trace] ${result.failed} events failed`);
    }
  } catch (err) {
    console.error(`[axiom-trace] send error: ${(err as Error).message}`);
  }
}

// ── Plugin Hooks ────────────────────────────────────────────────

export default definePluginEntry({
  id: "axiom-trace",
  name: "Axiom Trace Logger",
  description: "Full agent-turn tracing to Axiom",

  register(api) {
    // Get dataset from plugin config
    const getDataset = () => api.config?.dataset || "openclaw";

    // 1. Inbound message — start a new turn
    api.on("message_received", async (event) => {
      const ctx = event.context ?? {};
      const metadata = ctx.metadata ?? {};
      const channelId = ctx.channelId ?? "";

      if (!isSlackChannel(channelId)) return;

      const messageId = metadata.messageId ?? "";
      if (!messageId) return;

      const threadId = metadata.threadId ?? metadata.thread_ts ?? messageId ?? "";
      const turnId = genTurnId();

      turnState.set(event.sessionKey ?? "", {
        turn_id: turnId,
        thread_id: threadId,
        step: 0,
      });

      await axiomSend([{
        timestamp: stamp(),
        thread_id: threadId,
        turn_id: turnId,
        message_id: messageId,
        session_key: event.sessionKey ?? "",
        channel_id: channelId,
        step: 0,
        step_type: "inbound",
        content: (ctx.content ?? "").slice(0, 5000),
        sender: metadata.senderId ?? ctx.from ?? "unknown",
      }], getDataset());
    });

    // 2. Before prompt build — log what's going to the model
    api.on("before_prompt_build", async (event) => {
      const sessionKey = event.ctx?.sessionKey ?? "";
      const state = turnState.get(sessionKey);
      if (!state) return;

      state.step += 1;
      const step = state.step;

      await axiomSend([{
        timestamp: stamp(),
        thread_id: state.thread_id,
        turn_id: state.turn_id,
        session_key: sessionKey,
        step,
        step_type: "prompt_build",
        // system context summary — don't send full raw prompt to Axiom
        context_length: event.prompt?.length ?? 0,
        attachments_count: event.attachments?.length ?? 0,
      }], getDataset());
    });

    // 3. Model call started — log model, provider, timing
    api.on("model_call_started", async (event) => {
      const sessionKey = event.ctx?.sessionKey ?? "";
      const state = turnState.get(sessionKey);
      if (!state) return;

      state.step += 1;

      await axiomSend([{
        timestamp: stamp(),
        thread_id: state.thread_id,
        turn_id: state.turn_id,
        session_key: sessionKey,
        step: state.step,
        step_type: "model_call_started",
        provider: event.provider ?? "",
        model: event.model ?? "",
      }], getDataset());
    });

    // 4. Model call ended — log outcome + duration
    api.on("model_call_ended", async (event) => {
      const sessionKey = event.ctx?.sessionKey ?? "";
      const state = turnState.get(sessionKey);
      if (!state) return;

      state.step += 1;

      await axiomSend([{
        timestamp: stamp(),
        thread_id: state.thread_id,
        turn_id: state.turn_id,
        session_key: sessionKey,
        step: state.step,
        step_type: "model_call_ended",
        provider: event.provider ?? "",
        model: event.model ?? "",
        duration_ms: event.durationMs ?? 0,
        outcome: event.outcome ?? "",
      }], getDataset());
    });

    // 5. Before tool call — log what tool + params
    api.on("before_tool_call", async (event) => {
      const sessionKey = event.ctx?.sessionKey ?? "";
      const state = turnState.get(sessionKey);
      if (!state) return;

      state.step += 1;

      await axiomSend([{
        timestamp: stamp(),
        thread_id: state.thread_id,
        turn_id: state.turn_id,
        session_key: sessionKey,
        step: state.step,
        step_type: "tool_call",
        tool_name: event.toolName ?? "",
        params_summary: JSON.stringify(event.params ?? {}).slice(0, 1000),
      }], getDataset());
    });

    // 6. After tool call — log result
    api.on("after_tool_call", async (event) => {
      const sessionKey = event.ctx?.sessionKey ?? "";
      const state = turnState.get(sessionKey);
      if (!state) return;

      state.step += 1;

      await axiomSend([{
        timestamp: stamp(),
        thread_id: state.thread_id,
        turn_id: state.turn_id,
        session_key: sessionKey,
        step: state.step,
        step_type: "tool_result",
        tool_name: event.toolName ?? "",
        duration_ms: event.durationMs ?? 0,
        success: !event.error,
        error: event.error ?? "",
        result_summary: JSON.stringify(event.result ?? {}).slice(0, 1000),
      }], getDataset());
    });

    // 7. Agent end — log final outcome
    api.on("agent_end", async (event) => {
      const sessionKey = event.ctx?.sessionKey ?? "";
      const state = turnState.get(sessionKey);
      if (!state) return;

      await axiomSend([{
        timestamp: stamp(),
        thread_id: state.thread_id,
        turn_id: state.turn_id,
        session_key: sessionKey,
        step: state.step + 1,
        step_type: "agent_end",
        success: event.success ?? true,
        duration_ms: event.durationMs ?? 0,
      }], getDataset());

      // Clean up turn state
      turnState.delete(sessionKey);
    });
  },
});
