from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Service health. Does not depend on Ollama being online."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": "api",
        "message": "FastAPI backend is running",
        "ai_configured": True,
        "ollama_base_url": settings.ollama_base_url,
        "ollama_model": settings.ollama_chat_model,
        "vector_configured": True,
        "vector_provider": settings.vector_db_provider,
        "rag_configured": True,
        "sessions_configured": True,
        "feedback_configured": True,
    }
