# Docs (ingestion source)

Place documents here for **ingestion** and **vector indexing** (Phases 3–4).

- **Supported formats:** `.pdf`, `.md`, `.txt`
- The API and CLI scan this folder (or the path set by `DOCS_BASE_PATH`), extract text, normalize it, chunk it, then optionally embed and store in the vector DB for RAG.

Add your own `.pdf`, `.md`, or `.txt` files. Do not commit proprietary or sensitive content.

## Indexing a single PDF (quick start)

1. **Copy your PDF into this folder**, e.g.:
   ```bash
   cp "/path/to/your/file.pdf" docs/
   ```
2. **Point the API at this folder**  
   If you run the backend from `apps/api`, set in `apps/api/.env`:
   ```bash
   DOCS_BASE_PATH=../../docs
   ```
   (If you use the default `./docs`, put PDFs in `apps/api/docs` instead.)
3. **Start Ollama and pull the embed model** (if not already):
   ```bash
   ollama serve
   ollama pull nomic-embed-text
   ```
4. **Run indexing** (from `apps/api` with venv active):
   ```bash
   python -m app.cli_index
   ```
   Or via API (backend running):
   ```bash
   curl -X POST http://localhost:8000/vector/index \
     -H "Content-Type: application/json" \
     -d '{"path": "../../docs", "recursive": true, "reset_collection": true}'
   ```
5. Use the chat UI or `POST /rag/chat` to ask questions; answers will be grounded in the indexed PDF.

## Manual steps after config changes

- **After changing chunk size or overlap** (`CHUNK_SIZE_CHARS`, `CHUNK_OVERLAP_CHARS` in `apps/api/.env`): you must **re-index** so existing vectors match the new chunking. From `apps/api`: `python -m app.cli_index --reset-collection` (or use the Indexing panel in the UI: Reset collection before indexing → Run Indexing).
- **After changing RAG or docs path** in `.env`: **restart the API** (e.g. restart `uvicorn`) so the new values are loaded.

## If some questions still miss content

For long PDFs (e.g. 30+ pages), the app is tuned with higher `RAG_TOP_K` and larger chunks. If a specific article or term is still not found:

1. In `apps/api/.env`, try `RAG_TOP_K=18` or `20`, and/or `RAG_MIN_SCORE=0.08`.
2. Restart the API, then ask again. No need to re-index for RAG_TOP_K / RAG_MIN_SCORE changes.

## If responses feel slow (6–7 seconds)

Most of the time is **Ollama** (embedding the query + generating the answer). Chroma search is fast and the Chroma client is reused. To improve perceived speed:

1. **Streaming** – The UI shows “Finding relevant sections…” as soon as retrieval finishes, then streams the answer. You see progress instead of a long blank wait.
2. **Faster model** (optional) – Use a smaller chat model for quicker first token, e.g. `qwen2.5:3b`. In `apps/api/.env` set `OLLAMA_CHAT_MODEL=qwen2.5:3b` and run `ollama pull qwen2.5:3b`, then restart the API. Quality may be slightly lower than 7b.
