# API (FastAPI Backend)

FastAPI backend for the Company RAG Chatbot. Phase 2 adds local Ollama; Phase 3 adds document ingestion foundation (no vectors yet).

## Structure

```
apps/api/
  app/
    main.py              # FastAPI app, CORS, exception handler, routers
    cli_ingest.py        # CLI: python -m app.cli_ingest
    api/
      routes/
        health.py        # GET /health
        ai.py            # GET /ai/health, POST /ai/chat
        ingest.py        # GET /ingest/health, POST /ingest/preview
    core/
      config.py          # Env-based config (pydantic-settings)
    schemas/
      ai.py
      ingest.py          # Request/response for ingestion preview
    services/
      ollama_client.py
      ingestion/
        loader.py        # PDF, MD, TXT load
        normalizer.py    # Text normalization
        chunker.py       # Character chunking
        ingest_service.py
    utils/
      files.py           # Safe doc folder scan
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

## Phase 3 — Document ingestion foundation

Document loading, normalization, and chunking for future RAG. **No vector DB, no embeddings, no Ollama** in this phase.

### Supported file types

- **PDF** (`.pdf`) — text extraction via pypdf; no OCR
- **Markdown** (`.md`)
- **Plain text** (`.txt`)

### Config (see .env.example)

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS_BASE_PATH` | ./docs | Folder to scan for documents (relative to process cwd) |
| `INGEST_MAX_FILE_SIZE_MB` | 10 | Skip files larger than this |
| `CHUNK_SIZE_CHARS` | 1500 | Target chunk size in characters |
| `CHUNK_OVERLAP_CHARS` | 200 | Overlap between chunks |
| `ALLOWED_DOC_EXTENSIONS` | .pdf,.md,.txt | Comma-separated extensions |

### Placing files

Put `.pdf`, `.md`, or `.txt` files in the repo **docs/** folder (or the path set by `DOCS_BASE_PATH`). See [docs/README.md](../../docs/README.md). The API and CLI resolve `DOCS_BASE_PATH` relative to the current working directory. If your files are in the monorepo root **docs/** and you run the server from `apps/api`, set `DOCS_BASE_PATH=../../docs` in `.env`.

### Ingestion preview API

**GET /ingest/health** — Check ingestion config and whether docs path exists:

```bash
curl http://localhost:8000/ingest/health
```

**POST /ingest/preview** — Scan, load, normalize, chunk; return preview (no persistence):

```bash
curl -X POST http://localhost:8000/ingest/preview \
  -H "Content-Type: application/json" \
  -d '{"recursive": true, "include_chunks": true}'
```

Optional body: `path` (override base path), `recursive` (default true), `include_chunks` (default true). Omit body for defaults.

### Ingestion preview CLI

From `apps/api` with venv activated:

```bash
python -m app.cli_ingest
```

Options:

- `--path ./docs` — override docs path
- `--no-recursive` — do not scan subdirectories
- `--show-first-chunk` — print first chunk preview per document

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
| `DOCS_BASE_PATH` | ./docs | Document root for ingestion |
| `INGEST_MAX_FILE_SIZE_MB` | 10 | Max file size (MB) |
| `CHUNK_SIZE_CHARS` | 1500 | Chunk size (chars) |
| `CHUNK_OVERLAP_CHARS` | 200 | Chunk overlap (chars) |
| `ALLOWED_DOC_EXTENSIONS` | .pdf,.md,.txt | Allowed extensions |

---

## Requirements

- Python 3.10+
- Ollama installed and running locally (for `/ai/health` and `/ai/chat`)
- For ingestion: place PDF/MD/TXT under `DOCS_BASE_PATH` (default `./docs`)
