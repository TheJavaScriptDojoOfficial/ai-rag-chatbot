"use client";

import { useRef, useEffect } from "react";
import { MessageBubble } from "./message-bubble";
import type { ChatMessage } from "@/lib/types/chat";

interface MessageListProps {
  messages: ChatMessage[];
  showDebug?: boolean;
  loading?: boolean;
}

export function MessageList({
  messages,
  showDebug = false,
  loading = false,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [
    messages.length,
    loading,
    messages[messages.length - 1]?.content?.length ?? 0,
  ]);

  return (
    <div className="flex flex-col gap-4 py-4">
      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          showDebug={showDebug}
        />
      ))}
      {loading && messages.length > 0 && messages[messages.length - 1]?.role !== "assistant" && (
        <div className="flex justify-start">
          <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
            <span className="animate-pulse">Thinking…</span>
          </div>
        </div>
      )}
      <div ref={bottomRef} aria-hidden />
    </div>
  );
}
