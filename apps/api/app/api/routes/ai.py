"""
AI routes: Ollama runtime health and plain chat. No RAG, no retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_settings
from app.schemas.ai import (
    AIModelHealthResponse,
    PlainPromptRequest,
    PlainPromptResponse,
)
from app.services.ollama_client import OllamaClient, OllamaError

router = APIRouter(prefix="/ai", tags=["ai"])


def get_ollama_client() -> OllamaClient:
    s = get_settings()
    return OllamaClient(
        base_url=s.ollama_base_url,
        model=s.ollama_chat_model,
        timeout_seconds=float(s.ollama_timeout_seconds),
    )


@router.get("/health", response_model=AIModelHealthResponse)
def ai_health(client: OllamaClient = Depends(get_ollama_client)):
    """
    Verify backend can reach Ollama. Returns degraded status if unreachable
    without crashing the server.
    """
    settings = get_settings()
    reachable = client.is_reachable()
    return AIModelHealthResponse(
        status="ok" if reachable else "degraded",
        ollama_reachable=reachable,
        base_url=settings.ollama_base_url,
        model=settings.ollama_chat_model,
    )


@router.post("/chat", response_model=PlainPromptResponse)
def ai_chat(
    body: PlainPromptRequest,
    client: OllamaClient = Depends(get_ollama_client),
):
    """
    Send a plain user message to Ollama. No RAG or retrieval; end-to-end
    integration check only.
    """
    try:
        result = client.chat(body.message)
        return PlainPromptResponse(model=result["model"], response=result["response"])
    except OllamaError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "ollama_error",
                "message": e.message,
                "details": e.details,
            },
        )
