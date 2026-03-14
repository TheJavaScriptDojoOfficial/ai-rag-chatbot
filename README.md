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

### Frontend (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend (FastAPI)

```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate   # On Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL: [http://localhost:8000](http://localhost:8000). Health check: [http://localhost:8000/health](http://localhost:8000/health).

## Current Phase

- **Foundation only.** RAG logic, chat UI, LangChain, Chroma, Ollama, and similar integrations will be added in later phases.
- Frontend and backend are minimal and ready to extend.

## Requirements

- Node.js 18+ (for Next.js)
- Python 3.10+ (for FastAPI)
