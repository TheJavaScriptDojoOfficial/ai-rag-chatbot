# Web (Next.js Frontend)

Next.js frontend for the Company RAG Chatbot. App Router, TypeScript, Tailwind CSS. Connects to the FastAPI backend for RAG chat, source visibility, and health/status.

## Configuration

Create a `.env.local` (or copy from `.env.example`) and set:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

This is the base URL of the FastAPI backend. The frontend talks to it directly (no BFF). The backend must be running and must allow the frontend origin in CORS (e.g. `http://localhost:3000`).

## Run

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

**Backend must be running** (e.g. from `apps/api`: `uvicorn app.main:app --reload`). Documents should be indexed first (via backend ingest/vector APIs) for good RAG answers.

## Structure

- `src/app/` — App Router (layout, page, globals)
- `src/components/chat/` — Session sidebar, chat shell, message list, bubbles (with feedback), sources, debug panel, utility panel (Status, Debug, Indexing), indexing panel
- `src/lib/api/` — API client, RAG (streaming), health, vector, ingest, sessions, feedback
- `src/lib/types/` — RAG, health, chat, sessions, feedback types
- `src/lib/utils/` — `cn`, format helpers

## Features

- **Session sidebar** — Left panel lists chat sessions. "New chat" creates a session; click a session to switch. Sessions are persisted on the backend (SQLite). On load, the most recent session is selected if any exist. You can rename (edit icon) or delete (trash icon) a session.
- **Chat UI** — Type a question, send with Enter (Shift+Enter for newline). Messages and assistant answers appear in the thread. When a session is selected, messages are stored and recent conversation is used as context for RAG (session memory).
- **Streaming answers** — RAG responses stream token-by-token from **POST /rag/chat/stream** for a ChatGPT-like experience. If streaming fails, the app falls back to non-streaming **POST /rag/chat**.
- **Stop button** — While a response is streaming, a “Stop” button appears; clicking it aborts the request and keeps any partial answer already received.
- **Sources panel** — Each assistant reply shows cited chunks (file name, chunk index, score, snippet). Long lists are collapsible.
- **Debug toggle** — Enable “Debug mode” and send a message to see retrieval details (top_k, min_score, context size, model, prompt name) in the right panel and under the answer.
- **Health panel** — Right side shows backend status: API, RAG, AI runtime, Vector DB. Use “Refresh” to re-check. The Status tab also shows readiness details (model, embed model, collection, docs path). Failures do not break the page.
- **Indexing panel** — In the right-side utility panel, open the “Indexing” tab to run document indexing, clear the vector index, or preview docs. This is a **local dev/admin utility** (no auth or role-based access). Use “Run Indexing” to index from the configured docs path; optionally check “Reset collection before indexing”. Use “Clear Index” to wipe the vector collection (confirmation required). “Refresh status” re-checks health after indexing or clearing.
- **Feedback buttons** — For each assistant message that has a backend id (sent in a session), thumbs up / thumbs down buttons appear. Submitting feedback sends it to **POST /feedback** for later analysis. A short "Thanks" or "Recorded" confirmation is shown after submit.

## Requirements

- Node.js 18+
