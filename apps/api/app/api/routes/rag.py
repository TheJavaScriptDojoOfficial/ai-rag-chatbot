"""
RAG routes: health, retrieval-augmented chat (JSON and streaming).
"""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.schemas.rag import RAGChatRequest, RAGChatResponse
from app.services.rag.rag_service import run_rag_chat, run_rag_chat_stream, run_rag_preview

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/health")
def rag_health():
    """
    Verify RAG config and dependency readiness. Collection may be empty.
    """
    settings = get_settings()
    return {
        "status": "ok",
        "rag_top_k": settings.rag_top_k,
        "rag_min_score": settings.rag_min_score,
        "rag_max_context_chars": settings.rag_max_context_chars,
        "model": settings.ollama_chat_model,
        "embed_model": settings.ollama_embed_model,
        "collection_name": settings.chroma_collection_name,
    }


@router.post("/chat", response_model=RAGChatResponse)
def rag_chat(body: RAGChatRequest):
    """
    Retrieval-augmented answer: retrieve chunks -> build grounded prompt -> generate answer.
    Returns answer, sources, and optional debug. Non-streaming; use /rag/chat/stream for streaming.
    """
    return run_rag_chat(body)


def _sse_stream(body: RAGChatRequest):
    """Yield SSE-formatted bytes from RAG stream events."""
    for event_dict in run_rag_chat_stream(body):
        event = event_dict.get("event", "")
        data = event_dict.get("data", {})
        data_str = json.dumps(data) if data is not None else "{}"
        yield f"event: {event}\ndata: {data_str}\n\n"


@router.post("/chat/stream")
def rag_chat_stream(body: RAGChatRequest):
    """
    Streaming RAG: SSE events retrieval -> token chunks -> complete (answer, sources, debug).
    Use for progressive answer display. POST /rag/chat remains the non-streaming fallback.
    """
    return StreamingResponse(
        _sse_stream(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat/preview")
def rag_chat_preview(
    body: RAGChatRequest,
):
    """
    Run retrieval and return selected sources + stats; skip LLM generation.
    Useful for debugging RAG context.
    """
    return run_rag_preview(
        query=body.message,
        top_k=body.top_k,
        min_score=body.min_score,
    )
