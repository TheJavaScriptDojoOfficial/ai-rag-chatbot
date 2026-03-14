"use client";

import { useState } from "react";
import { ChatShell } from "@/components/chat/chat-shell";
import { SessionSidebar } from "@/components/chat/session-sidebar";

export default function Home() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <header className="shrink-0 border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight">
          Company RAG Chatbot
        </h1>
        <p className="mt-0.5 text-sm text-slate-600">
          Ask questions from indexed company documents
        </p>
      </header>

      <main className="flex-1 min-h-0 p-6 flex gap-4">
        <SessionSidebar
          activeSessionId={activeSessionId}
          onSessionSelect={setActiveSessionId}
        />
        <div className="min-h-0 flex-1 flex flex-col">
          <ChatShell activeSessionId={activeSessionId} />
        </div>
      </main>
    </div>
  );
}
