# API (FastAPI Backend)

FastAPI backend for the Company RAG Chatbot. Phase 2: Ollama; Phase 3: ingestion; Phase 4: vector DB; Phase 5: RAG chat orchestration.

## Structure

```
apps/api/
  app/
    main.py              # FastAPI app, CORS, exception handler, routers
    cli_ingest.py        # CLI: python -m app.cli_ingest
    cli_index.py         # CLI: python -m app.cli_index
    cli_rag.py           # CLI: python -m app.cli_rag
    api/
      routes/
        health.py        # GET /health
        ai.py            # GET /ai/health, POST /ai/chat (plain LLM debug)
        ingest.py        # GET /ingest/health, POST /ingest/preview
        vector.py        # GET /vector/health, POST /vector/index, POST /vector/search, DELETE /vector/index
        rag.py           # GET /rag/health, POST /rag/chat, POST /rag/chat/preview
    core/
      config.py          # Env-based config (pydantic-settings)
    schemas/
      ai.py, ingest.py, vector.py, rag.py
    services/
      ollama_client.py   # chat + chat_with_options (system + temperature)
      embeddings.py      # Ollama /api/embed
      vector_store/      # Chroma
      indexing/         # index + search
      retrieval/        # retrieve(): search + filter + dedupe + trim
      rag/              # prompt_builder, rag_service
      ingestion/
    utils/
      files.py
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

## Phase 4 — Vector DB integration

Embeddings (Ollama), persistent vector store (Chroma), indexing and semantic search. **No RAG answer generation yet.**

### Env vars (see .env.example)

- `VECTOR_DB_PROVIDER` — default `chroma`
- `CHROMA_PERSIST_DIRECTORY` — default `./data/chroma` (created if missing; already gitignored)
- `CHROMA_COLLECTION_NAME` — default `company_knowledge_base`
- `OLLAMA_EMBED_MODEL` — default `nomic-embed-text`
- `VECTOR_SEARCH_TOP_K` — default `5`

### Ollama and embedding model

1. Start Ollama (same as Phase 2):
   ```bash
   ollama serve
   ```
2. Pull the embedding model (must match `OLLAMA_EMBED_MODEL`):
   ```bash
   ollama pull nomic-embed-text
   ```

### Indexing

Indexing runs the ingestion pipeline (scan → load → normalize → chunk), generates embeddings via Ollama, and writes to Chroma. Re-indexing a document replaces its chunks (no duplicates).

**API:**

```bash
# Index from default docs path
curl -X POST http://localhost:8000/vector/index \
  -H "Content-Type: application/json" \
  -d '{"path": "./docs", "recursive": true, "reset_collection": false}'

# Clear collection then index (local testing)
curl -X POST http://localhost:8000/vector/index \
  -H "Content-Type: application/json" \
  -d '{"reset_collection": true}'
```

**CLI (from apps/api, venv active):**

```bash
python -m app.cli_index
python -m app.cli_index --reset-collection
python -m app.cli_index --search "leave policy"
```

### Vector health and search

**GET /vector/health** — Config and Chroma access (collection may be empty):

```bash
curl http://localhost:8000/vector/health
```

**POST /vector/search** — Semantic search preview (no answer generation):

```bash
curl -X POST http://localhost:8000/vector/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How does leave approval work?", "top_k": 5, "include_text": true}'
```

**DELETE /vector/index** — Clear the collection (local testing):

```bash
curl -X DELETE http://localhost:8000/vector/index
```

### Persistence

Chroma data is stored under `CHROMA_PERSIST_DIRECTORY` (default `./data/chroma`). The repo `.gitignore` already excludes `data/`. No DB server required.

---

## Phase 5 — Retrieval + RAG chat orchestration

Retrieval-augmented answers: retrieve relevant chunks, build a grounded prompt, generate an answer with sources. **No conversation persistence in this phase.**

### What changed

- **POST /ai/chat** — Unchanged. Plain direct LLM call (no retrieval). Use for debugging or simple chat.
- **POST /rag/chat** — New. Retrieval-augmented: runs semantic search, filters by score, builds a grounded system + context + question prompt, calls Ollama, returns answer + sources + optional debug.

### Env vars (see .env.example)

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_TOP_K` | 5 | Max chunks to retrieve |
| `RAG_MAX_CONTEXT_CHARS` | 6000 | Max total context length (trim after dedupe) |
| `RAG_MIN_SCORE` | 0.15 | Minimum similarity score to keep a chunk |
| `RAG_TEMPERATURE` | 0.2 | LLM temperature for RAG answers |
| `RAG_SYSTEM_PROMPT_NAME` | default_company_assistant | Prompt template name |

### Index first

RAG uses the same vector collection as Phase 4. Index documents before using RAG:

```bash
curl -X POST http://localhost:8000/vector/index \
  -H "Content-Type: application/json" \
  -d '{"recursive": true}'
```

Or from CLI: `python -m app.cli_index` (from `apps/api` with venv active).

### RAG health and chat

**GET /rag/health** — Config and dependency readiness (collection may be empty):

```bash
curl http://localhost:8000/rag/health
```

**POST /rag/chat** — Retrieval-augmented answer:

```bash
curl -X POST http://localhost:8000/rag/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How does leave approval work?", "include_sources": true, "include_debug": true}'
```

**POST /rag/chat/preview** — Retrieval only (no LLM): selected sources and stats:

```bash
curl -X POST http://localhost:8000/rag/chat/preview \
  -H "Content-Type: application/json" \
  -d '{"message": "How does leave approval work?"}'
```

### CLI RAG test

From `apps/api` with venv active:

```bash
python -m app.cli_rag --question "How does leave approval work?"
python -m app.cli_rag --question "What is the policy?" --debug
```

### Behavior

- If no chunks pass the score filter, the API returns a safe message: *"I could not find enough support in the indexed documents to answer that confidently."* No LLM call in that case.
- Sources are citation-ready: `file_name`, `chunk_index`, `score`, `text`, `metadata`.
- No multi-turn or chat history persistence yet.

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
| `VECTOR_DB_PROVIDER` | chroma | Vector store provider |
| `CHROMA_PERSIST_DIRECTORY` | ./data/chroma | Chroma persistence path |
| `CHROMA_COLLECTION_NAME` | company_knowledge_base | Collection name |
| `OLLAMA_EMBED_MODEL` | nomic-embed-text | Embedding model |
| `VECTOR_SEARCH_TOP_K` | 5 | Default search result count |
| `RAG_TOP_K` | 5 | RAG retrieval top_k |
| `RAG_MAX_CONTEXT_CHARS` | 6000 | Max context length (chars) |
| `RAG_MIN_SCORE` | 0.15 | Min similarity score |
| `RAG_TEMPERATURE` | 0.2 | LLM temperature for RAG |
| `RAG_SYSTEM_PROMPT_NAME` | default_company_assistant | Prompt template |

---

## Requirements

- Python 3.10+
- Ollama installed and running (chat + embeddings). Pull `qwen2.5:7b` and `nomic-embed-text`.
- For ingestion/indexing: place PDF/MD/TXT under `DOCS_BASE_PATH` (default `./docs`).
- Chroma stores vectors under `CHROMA_PERSIST_DIRECTORY` (default `./data/chroma`).
- For RAG: index docs first (POST /vector/index or `python -m app.cli_index`); then use POST /rag/chat or `python -m app.cli_rag`.
