# Company RAG Chatbot

A local AI RAG (Retrieval-Augmented Generation) chatbot with a Next.js frontend and FastAPI backend. This repository is the foundation for adding RAG, chat, and model integration in later phases.

## Monorepo Structure

```
/
├── apps/
│   ├── web/          # Next.js frontend (TypeScript, Tailwind); app code in src/app/
│   └── api/          # FastAPI backend (Python)
├── packages/
│   └── shared/       # Shared types/constants (for future use)
├── docs/             # Project documentation
├── scripts/          # Helper scripts (for future use)
├── .gitignore
└── README.md
```

## How to Run

### Backend (FastAPI) — run first

```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate   # On Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL: [http://localhost:8000](http://localhost:8000). Health: [http://localhost:8000/health](http://localhost:8000/health).

### Frontend (Next.js)

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` in `apps/web/.env.local` (see `apps/web/.env.example`). Then:

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The frontend talks to the FastAPI backend directly. Index documents first (via backend ingest/vector APIs) for good RAG answers.

## Current Phase

- **Phase 7 — Streaming and indexing UI:** Streaming RAG answers via `POST /rag/chat/stream` (SSE), Stop button, fallback to non-streaming `POST /rag/chat`. Frontend: tabbed right panel (Status, Debug, Indexing) with Run Indexing, Clear Index, Preview Docs, and improved status/readiness details.
- **Phase 6:** Chat UI, RAG integration, source citations, health/status, debug mode.
- Backend: RAG (streaming + non-streaming), vector DB, ingest, and AI routes are in place.

## Requirements

- Node.js 18+ (for Next.js)
- Python 3.10+ (for FastAPI)
