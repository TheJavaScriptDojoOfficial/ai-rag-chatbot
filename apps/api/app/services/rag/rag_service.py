"""
RAG orchestration: retrieval -> prompt -> Ollama -> answer + sources + debug.
"""
from typing import List, Optional

from app.core.config import get_settings
from app.schemas.rag import (
    RAGChatRequest,
    RAGChatResponse,
    RAGDebugInfo,
    RAGSource,
)
from app.schemas.vector import SearchMatch
from app.services.ollama_client import OllamaClient, OllamaError
from app.services.rag.prompt_builder import build_rag_messages
from app.services.retrieval.retrieval_service import retrieve, RetrievalResult

INSUFFICIENT_EVIDENCE_ANSWER = (
    "I could not find enough support in the indexed documents to answer that confidently."
)


def _search_match_to_rag_source(m: SearchMatch) -> RAGSource:
    """Map SearchMatch to citation-ready RAGSource. Metadata stays JSON-serializable."""
    meta = getattr(m, "metadata", None) or {}
    # Ensure metadata is dict with simple types for JSON
    safe_meta = {}
    for k, v in meta.items():
        if v is None or isinstance(v, (str, int, float, bool)):
            safe_meta[k] = v
        else:
            safe_meta[k] = str(v)
    return RAGSource(
        chunk_id=getattr(m, "chunk_id", ""),
        source_id=getattr(m, "source_id", ""),
        file_name=getattr(m, "file_name", ""),
        file_path=meta.get("file_path", ""),
        chunk_index=getattr(m, "chunk_index", 0),
        score=getattr(m, "score", 0.0),
        text=getattr(m, "text", ""),
        metadata=safe_meta,
    )


def run_rag_chat(req: RAGChatRequest) -> RAGChatResponse:
    """
    Run RAG: retrieve -> (if no chunks: return safe fallback) -> build prompt -> Ollama -> response.
    """
    settings = get_settings()
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_chat_model,
        timeout_seconds=float(settings.ollama_timeout_seconds),
    )

    retrieval_result = retrieve(
        query=req.message,
        top_k=req.top_k,
        min_score=req.min_score,
        max_context_chars=None,
    )

    # No usable context -> do not call LLM; return safe refusal
    if not retrieval_result.chunks:
        sources: List[RAGSource] = []
        if req.include_sources:
            sources = []
        debug = None
        if req.include_debug:
            debug = RAGDebugInfo(
                top_k_used=retrieval_result.top_k_used,
                min_score_used=retrieval_result.min_score_used,
                context_char_count=0,
                retrieved_count=retrieval_result.retrieved_count,
                selected_count=0,
                model=settings.ollama_chat_model,
                prompt_name=settings.rag_system_prompt_name,
            )
        return RAGChatResponse(
            mode="rag",
            model=settings.ollama_chat_model,
            answer=INSUFFICIENT_EVIDENCE_ANSWER,
            sources=sources,
            debug=debug,
        )

    messages = build_rag_messages(
        question=req.message,
        chunks=retrieval_result.chunks,
        prompt_name=settings.rag_system_prompt_name,
    )

    try:
        result = client.chat_with_options(
            messages=messages,
            temperature=settings.rag_temperature,
        )
        answer = result.get("response", "").strip() or INSUFFICIENT_EVIDENCE_ANSWER
        model_used = result.get("model", settings.ollama_chat_model)
    except OllamaError as e:
        answer = f"Sorry, the answer service is temporarily unavailable: {e.message}."
        model_used = settings.ollama_chat_model

    sources = [_search_match_to_rag_source(m) for m in retrieval_result.chunks] if req.include_sources else []
    debug = None
    if req.include_debug:
        debug = RAGDebugInfo(
            top_k_used=retrieval_result.top_k_used,
            min_score_used=retrieval_result.min_score_used,
            context_char_count=retrieval_result.context_char_count,
            retrieved_count=retrieval_result.retrieved_count,
            selected_count=retrieval_result.selected_count,
            model=model_used,
            prompt_name=settings.rag_system_prompt_name,
        )

    return RAGChatResponse(
        mode="rag",
        model=model_used,
        answer=answer,
        sources=sources,
        debug=debug,
    )


def run_rag_preview(query: str, top_k: Optional[int] = None, min_score: Optional[float] = None) -> dict:
    """
    Run retrieval + prompt assembly only; no LLM call. For debugging.
    Returns selected sources and prompt stats.
    """
    retrieval_result = retrieve(query=query, top_k=top_k, min_score=min_score, max_context_chars=None)
    settings = get_settings()
    sources = [_search_match_to_rag_source(m) for m in retrieval_result.chunks]
    return {
        "query": query,
        "top_k_used": retrieval_result.top_k_used,
        "min_score_used": retrieval_result.min_score_used,
        "retrieved_count": retrieval_result.retrieved_count,
        "selected_count": retrieval_result.selected_count,
        "context_char_count": retrieval_result.context_char_count,
        "sources": sources,
        "prompt_name": settings.rag_system_prompt_name,
    }
