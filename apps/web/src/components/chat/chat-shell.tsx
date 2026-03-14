"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { UtilityPanel } from "./utility-panel";
import { postRAGChat, streamRagChat } from "@/lib/api/rag";
import { getSession } from "@/lib/api/sessions";
import {
  getHealth,
  getRAGHealth,
  getAIHealth,
  getVectorHealth,
  getIngestHealth,
} from "@/lib/api/health";
import type { ChatMessage } from "@/lib/types/chat";
import type {
  AppHealthSummary,
  RAGHealthResponse,
  VectorHealthResponse,
} from "@/lib/types/health";
import type { IngestHealthResponse } from "@/lib/api/ingest";
import type { ApiError } from "@/lib/api/client";
import type { ChatMessageRecord } from "@/lib/types/sessions";

const EMPTY_SUMMARY: AppHealthSummary = {
  api: "unreachable",
  rag: "unreachable",
  ai: "unreachable",
  vector: "unreachable",
  lastChecked: null,
};

function deriveSummary(
  api: "ok" | "fail",
  rag: "ok" | "degraded" | "fail",
  ai: "ok" | "degraded" | "fail",
  vector: "ok" | "degraded" | "fail"
): AppHealthSummary {
  return {
    api: api === "ok" ? "healthy" : "unreachable",
    rag: rag === "ok" ? "ready" : rag === "degraded" ? "degraded" : "unreachable",
    ai: ai === "ok" ? "healthy" : ai === "degraded" ? "degraded" : "unreachable",
    vector:
      vector === "ok" ? "healthy" : vector === "degraded" ? "degraded" : "unreachable",
    lastChecked: Date.now(),
  };
}

function getErrorMessage(err: unknown): string {
  if (err && typeof err === "object" && "message" in err) {
    const msg = (err as ApiError).message;
    if (typeof msg === "string") return msg;
  }
  if (err && typeof err === "object" && "detail" in err) {
    const d = (err as { detail?: string | Record<string, unknown> }).detail;
    if (typeof d === "string") return d;
    if (d && typeof d === "object" && typeof d.message === "string") return d.message;
  }
  if (err instanceof Error) return err.message;
  return "Something went wrong. Please try again.";
}

function recordToChatMessage(m: ChatMessageRecord): ChatMessage {
  const createdAt = typeof m.created_at === "string" ? new Date(m.created_at).getTime() : Date.now();
  return {
    id: m.id,
    role: m.role as "user" | "assistant" | "system",
    content: m.content ?? "",
    sources: Array.isArray(m.sources) ? (m.sources as ChatMessage["sources"]) : undefined,
    debug: m.debug ?? undefined,
    createdAt,
    error: m.error ?? undefined,
    messageId: m.id,
  };
}

interface ChatShellProps {
  activeSessionId: string | null;
}

export function ChatShell({ activeSessionId }: ChatShellProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const [debugMode, setDebugMode] = useState(false);
  const [lastDebug, setLastDebug] = useState<ChatMessage["debug"]>(null);
  const [healthSummary, setHealthSummary] = useState<AppHealthSummary>(EMPTY_SUMMARY);
  const [healthLoading, setHealthLoading] = useState(false);
  const [ragHealth, setRagHealth] = useState<RAGHealthResponse | null>(null);
  const [vectorHealth, setVectorHealth] = useState<VectorHealthResponse | null>(null);
  const [ingestHealth, setIngestHealth] = useState<IngestHealthResponse | null>(null);

  const loadSessionMessages = useCallback(async (sessionId: string) => {
    try {
      const data = await getSession(sessionId);
      const list = (data.messages ?? []).map(recordToChatMessage);
      setMessages(list);
    } catch {
      setMessages([]);
    }
  }, []);

  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId, loadSessionMessages]);

  const fetchHealth = useCallback(async () => {
    setHealthLoading(true);
    let api: "ok" | "fail" = "fail";
    let rag: "ok" | "degraded" | "fail" = "fail";
    let ai: "ok" | "degraded" | "fail" = "fail";
    let vector: "ok" | "degraded" | "fail" = "fail";

    try {
      await getHealth();
      api = "ok";
    } catch {
      api = "fail";
    }

    try {
      const r = await getRAGHealth();
      setRagHealth(r);
      rag = r.status === "ok" ? "ok" : "degraded";
    } catch {
      setRagHealth(null);
      rag = "fail";
    }

    try {
      const a = await getAIHealth();
      ai = a.ollama_reachable ? "ok" : "degraded";
    } catch {
      ai = "fail";
    }

    try {
      const v = await getVectorHealth();
      setVectorHealth(v);
      vector = v.status === "ok" ? "ok" : "degraded";
    } catch {
      setVectorHealth(null);
      vector = "fail";
    }

    try {
      const ing = await getIngestHealth();
      setIngestHealth(ing);
    } catch {
      setIngestHealth(null);
    }

    setHealthSummary(deriveSummary(api, rag, ai, vector));
    setHealthLoading(false);
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  const sendMessage = useCallback(
    async (text: string) => {
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: text,
        createdAt: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);

      const assistantId = `assistant-${Date.now()}`;
      const placeholder: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: Date.now(),
      };
      setMessages((prev) => [...prev, placeholder]);
      setLoading(true);
      setStreaming(true);
      abortRef.current = new AbortController();
      const signal = abortRef.current.signal;
      const streamErrorRef = { current: null as string | null };
      const streamHadContentRef = { current: false };

      const ragRequest = {
        message: text,
        include_sources: true,
        include_debug: debugMode,
        session_id: activeSessionId ?? undefined,
        use_session_memory: true,
      };

      const tryStreaming = async () => {
        await streamRagChat(
          ragRequest,
          {
            onToken: (chunk) => {
              streamHadContentRef.current = true;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: (m.content || "") + chunk }
                    : m
                )
              );
            },
            onComplete: (payload) => {
              streamHadContentRef.current = true;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: payload.answer || m.content,
                        sources: payload.sources ?? [],
                        debug: payload.debug ?? undefined,
                        messageId: payload.message_id ?? undefined,
                      }
                    : m
                )
              );
              if (payload.debug) setLastDebug(payload.debug);
            },
            onError: (msg) => {
              streamErrorRef.current = msg;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, error: msg } : m
                )
              );
            },
          },
          signal
        );
      };

      try {
        await tryStreaming();
      } catch (err) {
        if (signal.aborted) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, error: undefined } : m
            )
          );
        } else {
          streamErrorRef.current = getErrorMessage(err);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, error: streamErrorRef.current ?? undefined }
                : m
            )
          );
        }
      } finally {
        setLoading(false);
        setStreaming(false);
        abortRef.current = null;
      }

      if (signal.aborted) return;

      if (streamErrorRef.current && !streamHadContentRef.current) {
        try {
          const res = await postRAGChat(ragRequest);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    content: res.answer,
                    sources: res.sources ?? [],
                    debug: res.debug ?? undefined,
                    error: undefined,
                    messageId: res.message_id ?? undefined,
                  }
                : m
            )
          );
          if (res.debug) setLastDebug(res.debug);
        } catch (fallbackErr) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, error: getErrorMessage(fallbackErr) }
                : m
            )
          );
        }
      }
    },
    [debugMode, activeSessionId]
  );

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, []);

  const empty = messages.length === 0;

  const chatColumn = (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex-1 overflow-y-auto">
        {empty ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <p className="text-slate-600">
              {activeSessionId
                ? "Ask a question about your indexed company docs."
                : "Select a chat or start a new one to begin."}
            </p>
            {activeSessionId && (
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {[
                  "How does leave approval work?",
                  "What is the reimbursement process?",
                  "Summarize the onboarding policy.",
                ].map((example) => (
                  <button
                    key={example}
                    type="button"
                    onClick={() => sendMessage(example)}
                    disabled={loading}
                    className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                  >
                    {example}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <MessageList
            messages={messages}
            showDebug={debugMode}
            loading={loading}
            activeSessionId={activeSessionId}
          />
        )}
      </div>
      <div className="shrink-0 border-t border-slate-200 bg-white p-4">
        <ChatInput
          onSend={sendMessage}
          disabled={loading || !activeSessionId}
          streaming={streaming}
          onStop={stopStreaming}
          placeholder={activeSessionId ? undefined : "Select or start a chat to send a message"}
        />
      </div>
    </div>
  );

  return (
    <div className="min-h-0 flex-1 flex flex-col lg:flex-row gap-6">
      <section
        className="flex-1 min-h-0 flex flex-col rounded-xl border border-slate-200 bg-slate-50/50 shadow-sm"
        aria-label="Chat"
      >
        {chatColumn}
      </section>
      <aside
        className="lg:w-80 shrink-0 flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm min-h-0"
        aria-label="Status, debug, and indexing"
      >
        <UtilityPanel
          summary={healthSummary}
          onRefresh={fetchHealth}
          refreshing={healthLoading}
          debugMode={debugMode}
          onDebugModeChange={setDebugMode}
          lastDebug={lastDebug ?? undefined}
          ragHealth={ragHealth}
          vectorHealth={vectorHealth}
          ingestHealth={ingestHealth}
        />
      </aside>
    </div>
  );
}
