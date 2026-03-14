"use client";

import { useState, useCallback, useEffect } from "react";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { StatusBar } from "./status-bar";
import { DebugPanel } from "./debug-panel";
import { postRAGChat } from "@/lib/api/rag";
import {
  getHealth,
  getRAGHealth,
  getAIHealth,
  getVectorHealth,
} from "@/lib/api/health";
import type { ChatMessage } from "@/lib/types/chat";
import type { AppHealthSummary } from "@/lib/types/health";
import type { ApiError } from "@/lib/api/client";

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

export function ChatShell() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [lastDebug, setLastDebug] = useState<ChatMessage["debug"]>(null);
  const [healthSummary, setHealthSummary] = useState<AppHealthSummary>(EMPTY_SUMMARY);
  const [healthLoading, setHealthLoading] = useState(false);

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
      rag = r.status === "ok" ? "ok" : "degraded";
    } catch {
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
      vector = v.status === "ok" ? "ok" : "degraded";
    } catch {
      vector = "fail";
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

      try {
        const res = await postRAGChat({
          message: text,
          include_sources: true,
          include_debug: debugMode,
        });

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content: res.answer,
                  sources: res.sources ?? [],
                  debug: res.debug ?? undefined,
                }
              : m
          )
        );
        if (res.debug) setLastDebug(res.debug);
      } catch (err) {
        const msg = getErrorMessage(err);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: "", error: msg } : m
          )
        );
      } finally {
        setLoading(false);
      }
    },
    [debugMode]
  );

  const empty = messages.length === 0;

  const chatColumn = (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex-1 overflow-y-auto">
        {empty ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <p className="text-slate-600">
              Ask a question about your indexed company docs.
            </p>
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
          </div>
        ) : (
          <MessageList
            messages={messages}
            showDebug={debugMode}
            loading={loading}
          />
        )}
      </div>
      <div className="shrink-0 border-t border-slate-200 bg-white p-4">
        <ChatInput onSend={sendMessage} disabled={loading} />
      </div>
    </div>
  );

  const statusColumn = (
    <div className="space-y-6">
      <StatusBar
        summary={healthSummary}
        onRefresh={fetchHealth}
        refreshing={healthLoading}
      />
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={debugMode}
          onChange={(e) => setDebugMode(e.target.checked)}
          className="rounded border-slate-300 text-slate-700 focus:ring-slate-400"
        />
        <span className="text-sm text-slate-700">Debug mode</span>
      </label>
      <DebugPanel debug={lastDebug ?? undefined} />
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
        className="lg:w-80 shrink-0 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        aria-label="Status and debug"
      >
        {statusColumn}
      </aside>
    </div>
  );
}
