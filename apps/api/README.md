# API (FastAPI Backend)

FastAPI backend for the Company RAG Chatbot. RAG and model integration will be added in later phases.

## Structure

```
apps/api/
  app/
    main.py           # FastAPI app, CORS, router
    api/
      routes/
        health.py     # GET /health
    core/
      config.py      # Env-based config (e.g. CORS origins)
  requirements.txt
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

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

- API base: [http://localhost:8000](http://localhost:8000)
- OpenAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Test the health endpoint

```bash
curl http://localhost:8000/health
```

Expected JSON:

```json
{
  "status": "ok",
  "service": "api",
  "message": "FastAPI backend is running"
}
```

## Configuration

- **CORS**: Allowed origins default to `http://localhost:3000`. Override with env var:
  ```bash
  export CORS_ORIGINS="http://localhost:3000,https://myapp.com"
  ```

## Requirements

- Python 3.10+
