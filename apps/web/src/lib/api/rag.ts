/**
 * RAG API: chat (JSON and streaming), preview.
 */

import { apiRequest, getApiBaseUrl } from "./client";
import type {
  RAGChatRequest,
  RAGChatResponse,
  RAGDebugInfo,
  RAGSource,
} from "@/lib/types/rag";

export async function postRAGChat(
  body: RAGChatRequest
): Promise<RAGChatResponse> {
  return apiRequest<RAGChatResponse>("/rag/chat", {
    method: "POST",
    body: JSON.stringify({
      message: body.message,
      top_k: body.top_k ?? undefined,
      min_score: body.min_score ?? undefined,
      include_sources: body.include_sources ?? true,
      include_debug: body.include_debug ?? false,
      session_id: body.session_id ?? undefined,
      use_session_memory: body.use_session_memory ?? true,
    }),
  });
}

/** Payload of SSE complete event from POST /rag/chat/stream */
export interface RAGStreamCompletePayload {
  model: string;
  answer: string;
  sources: RAGSource[];
  debug?: RAGDebugInfo | null;
  message_id?: string | null;
}

/** Handlers for streamRagChat */
export interface RAGStreamHandlers {
  onRetrieval?: (data: { retrieved_count: number; selected_count: number }) => void;
  onToken?: (textChunk: string) => void;
  onComplete?: (payload: RAGStreamCompletePayload) => void;
  onError?: (message: string) => void;
}

/**
 * Consume POST /rag/chat/stream via fetch + ReadableStream; parse SSE and invoke handlers.
 * Supports AbortSignal for stop. On stream failure, call onError and optionally fall back to postRAGChat.
 */
export async function streamRagChat(
  request: RAGChatRequest,
  handlers: RAGStreamHandlers,
  signal?: AbortSignal
): Promise<void> {
  const base = getApiBaseUrl().replace(/\/$/, "");
  const url = `${base}/rag/chat/stream`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: request.message,
      top_k: request.top_k ?? undefined,
      min_score: request.min_score ?? undefined,
      include_sources: request.include_sources ?? true,
      include_debug: request.include_debug ?? false,
      session_id: request.session_id ?? undefined,
      use_session_memory: request.use_session_memory ?? true,
    }),
    signal,
  });

  if (!res.ok) {
    let msg: string;
    if (res.headers.get("content-type")?.includes("application/json")) {
      const body = (await res.json().catch(() => ({}))) as { message?: string };
      msg = typeof body?.message === "string" ? body.message : `Request failed: ${res.status}`;
    } else {
      msg = (await res.text()) || `Request failed: ${res.status}`;
    }
    handlers.onError?.(msg);
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    handlers.onError?.("No response body");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";
  let currentData = "";

  const flushEvent = () => {
    const event = currentEvent;
    const data = currentData.trim();
    currentEvent = "";
    currentData = "";
    if (!event || !data) return;
    try {
      const parsed = JSON.parse(data) as Record<string, unknown>;
      if (event === "retrieval") {
        handlers.onRetrieval?.({
          retrieved_count: (parsed.retrieved_count as number) ?? 0,
          selected_count: (parsed.selected_count as number) ?? 0,
        });
      } else if (event === "token") {
        const text = (parsed.text as string) ?? "";
        if (text) handlers.onToken?.(text);
      } else if (event === "complete") {
        handlers.onComplete?.({
          model: (parsed.model as string) ?? "",
          answer: (parsed.answer as string) ?? "",
          sources: (parsed.sources as RAGSource[]) ?? [],
          debug: (parsed.debug as RAGDebugInfo | null) ?? null,
          message_id: (parsed.message_id as string | null) ?? null,
        });
      } else if (event === "error") {
        handlers.onError?.((parsed.message as string) ?? "Unknown error");
      }
    } catch {
      // ignore parse errors for unknown event types
    }
  };

  const processLine = (line: string) => {
    if (line.startsWith("event:")) {
      flushEvent();
      currentEvent = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      currentData = line.slice(5).trim();
    }
  };

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) processLine(line);
    }
    flushEvent();
  } catch (e) {
    if (signal?.aborted) return;
    handlers.onError?.(e instanceof Error ? e.message : "Stream failed");
  }
}

export async function postRAGChatPreview(
  message: string,
  options?: { top_k?: number; min_score?: number }
): Promise<{
  query: string;
  top_k_used: number;
  min_score_used: number;
  retrieved_count: number;
  selected_count: number;
  context_char_count: number;
  sources: unknown[];
  prompt_name: string;
}> {
  return apiRequest("/rag/chat/preview", {
    method: "POST",
    body: JSON.stringify({
      message,
      top_k: options?.top_k,
      min_score: options?.min_score,
    }),
  });
}
