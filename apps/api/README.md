# API (FastAPI Backend)

FastAPI backend for the Company RAG Chatbot. Phase 2 adds local Ollama connectivity; RAG and document ingestion come in later phases.

## Structure

```
apps/api/
  app/
    main.py              # FastAPI app, CORS, exception handler, routers
    api/
      routes/
        health.py        # GET /health
        ai.py            # GET /ai/health, POST /ai/chat
    core/
      config.py          # Env-based config (pydantic-settings)
    services/
      ollama_client.py   # Ollama HTTP client
    schemas/
      ai.py              # Request/response models for AI routes
  requirements.txt
  .env.example
  README.md
```

## Setup (Mac / Linux)

### 1. Create virtual environment

```bash
cd apps/api
python3 -m venv venv
```

### 2. Activate virtual environment

**Mac / Linux (zsh/bash):**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local Ollama)
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

- API base: [http://localhost:8000](http://localhost:8000)
- OpenAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Local AI runtime setup (Phase 2)

The backend talks to a local [Ollama](https://ollama.com) instance. No LangChain, Chroma, or vector DB in this phase.

### Install Ollama

1. Install Ollama on your machine:
   - **Mac:** [https://ollama.com/download](https://ollama.com/download) or `brew install ollama`
   - **Linux:** see [Ollama Linux install](https://github.com/ollama/ollama/blob/main/docs/linux.md)

2. Start Ollama (if not running as a service):
   ```bash
   ollama serve
   ```
   On Mac, the app often runs in the background after install.

3. Pull a chat model (must match `OLLAMA_CHAT_MODEL` in `.env`):
   ```bash
   ollama pull qwen2.5:7b
   ```

### Configure .env

In `apps/api/.env` (copy from `.env.example`):

- `OLLAMA_BASE_URL` — Ollama API URL (default `http://localhost:11434`)
- `OLLAMA_CHAT_MODEL` — Model name for chat (default `qwen2.5:7b`)
- `OLLAMA_TIMEOUT_SECONDS` — Request timeout (default `120`)

Other optional keys: `APP_NAME`, `APP_ENV`, `API_PORT`, `CORS_ORIGINS`.

### Test endpoints

**Service health (does not require Ollama):**

```bash
curl http://localhost:8000/health
```

**AI runtime health (checks Ollama reachability):**

```bash
curl http://localhost:8000/ai/health
```

Expected when Ollama is running:

```json
{
  "status": "ok",
  "ollama_reachable": true,
  "base_url": "http://localhost:11434",
  "model": "qwen2.5:7b"
}
```

When Ollama is down you get `"ollama_reachable": false` and `"status": "degraded"` (no server crash).

**Plain chat (end-to-end):**

```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is React? Answer in one short paragraph."}'
```

Example response:

```json
{
  "model": "qwen2.5:7b",
  "response": "React is a JavaScript library..."
}
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Company RAG API | Application name |
| `APP_ENV` | development | Environment label |
| `API_PORT` | 8000 | Port (used when running via script) |
| `CORS_ORIGINS` | http://localhost:3000 | Comma-separated allowed origins |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API base URL |
| `OLLAMA_CHAT_MODEL` | qwen2.5:7b | Chat model name |
| `OLLAMA_TIMEOUT_SECONDS` | 120 | Timeout for Ollama requests |

---

## Requirements

- Python 3.10+
- Ollama installed and running locally (for `/ai/health` and `/ai/chat`)
