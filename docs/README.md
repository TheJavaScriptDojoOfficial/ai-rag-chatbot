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
