# Docs (ingestion source)

Place documents here for the **ingestion preview** (Phase 3).

- **Supported formats:** `.pdf`, `.md`, `.txt`
- The API and CLI scan this folder (or the path set by `DOCS_BASE_PATH`), extract text, normalize it, and chunk it for preview.
- No vectors or persistence in this phase — this folder is only used as the source for the preview pipeline.

Add your own `.pdf`, `.md`, or `.txt` files to test the ingestion flow. Do not commit proprietary or sensitive content.
