import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api.routes import health, ai, ingest, vector, rag

logger = logging.getLogger(__name__)

app = FastAPI(title="Company RAG Chatbot API", version="0.1.0")


@app.exception_handler(Exception)
def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Avoid leaking stack traces in API responses; log internally."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred"},
    )


settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ai.router)
app.include_router(ingest.router)
app.include_router(vector.router)
app.include_router(rag.router)
