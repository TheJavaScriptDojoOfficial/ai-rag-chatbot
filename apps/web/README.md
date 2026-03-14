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
- `src/components/chat/` — Chat shell, message list, bubbles, sources, debug panel, status bar
- `src/lib/api/` — API client, RAG and health calls
- `src/lib/types/` — RAG, health, and chat message types
- `src/lib/utils/` — `cn`, format helpers

## Features

- **Chat UI** — Type a question, send with Enter (Shift+Enter for newline). Messages and assistant answers appear in the thread; no persistence (in-memory only).
- **Sources panel** — Each assistant reply shows cited chunks (file name, chunk index, score, snippet). Long lists are collapsible.
- **Debug toggle** — Enable “Debug mode” and send a message to see retrieval details (top_k, min_score, context size, model, prompt name) in the right panel and under the answer.
- **Health panel** — Right side shows backend status: API, RAG, AI runtime, Vector DB. Use “Refresh” to re-check. Failures do not break the page.

## Requirements

- Node.js 18+
