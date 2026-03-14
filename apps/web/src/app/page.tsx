import { ChatShell } from "@/components/chat/chat-shell";

export default function Home() {
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

      <main className="flex-1 min-h-0 p-6">
        <ChatShell />
      </main>
    </div>
  );
}
