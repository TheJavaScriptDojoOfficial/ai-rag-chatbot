"""
RAG orchestration: retrieval -> prompt -> Ollama -> answer + sources + debug.
Supports both one-shot and streaming responses. Optional session memory for context.
"""
import json
from typing import Any, Dict, Generator, List, Optional

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
from app.services.sessions.session_repository import get_session
from app.services.sessions.session_service import (
    append_assistant_message,
    append_user_message,
    get_recent_conversation_turns,
    update_session_title_from_first_message,
)

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


def _get_memory_context(session_id: Optional[str], use_memory: bool) -> List[Dict[str, Any]]:
    """Fetch recent conversation turns for prompt context if session_id and use_memory are set."""
    if not session_id or not use_memory:
        return []
    if not get_session(session_id):
        return []
    return get_recent_conversation_turns(session_id)


def run_rag_chat(req: RAGChatRequest) -> RAGChatResponse:
    """
    Run RAG: retrieve -> (if no chunks: return safe fallback) -> build prompt -> Ollama -> response.
    If session_id and use_session_memory, include recent conversation in prompt.
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

    memory_messages: List[Dict[str, Any]] = []
    if req.session_id and req.use_session_memory:
        memory_messages = _get_memory_context(req.session_id, req.use_session_memory)

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
                session_id=req.session_id,
                memory_messages_used=len(memory_messages) if memory_messages else None,
            )
        message_id_none: Optional[str] = None
        if req.session_id:
            session = get_session(req.session_id)
            if session:
                was_first = (session.get("message_count") or 0) == 0
                append_user_message(req.session_id, req.message)
                rec = append_assistant_message(req.session_id, INSUFFICIENT_EVIDENCE_ANSWER)
                if rec:
                    message_id_none = rec.get("id")
                if was_first:
                    update_session_title_from_first_message(req.session_id, req.message)
        return RAGChatResponse(
            mode="rag",
            model=settings.ollama_chat_model,
            answer=INSUFFICIENT_EVIDENCE_ANSWER,
            sources=sources,
            debug=debug,
            message_id=message_id_none,
        )

    messages = build_rag_messages(
        question=req.message,
        chunks=retrieval_result.chunks,
        prompt_name=settings.rag_system_prompt_name,
        conversation_history=memory_messages if memory_messages else None,
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
            session_id=req.session_id,
            memory_messages_used=len(memory_messages) if memory_messages else None,
        )

    message_id: Optional[str] = None
    if req.session_id:
        session = get_session(req.session_id)
        if session:
            was_first = (session.get("message_count") or 0) == 0
            append_user_message(req.session_id, req.message)
            sources_json = json.dumps([s.model_dump() for s in sources]) if sources else None
            debug_json = json.dumps(debug.model_dump()) if debug else None
            rec = append_assistant_message(
                req.session_id,
                answer,
                sources_json=sources_json,
                debug_json=debug_json,
            )
            if rec:
                message_id = rec.get("id")
            if was_first:
                update_session_title_from_first_message(req.session_id, req.message)

    return RAGChatResponse(
        mode="rag",
        model=model_used,
        answer=answer,
        sources=sources,
        debug=debug,
        message_id=message_id,
    )


def run_rag_chat_stream(req: RAGChatRequest) -> Generator[Dict[str, Any], None, None]:
    """
    Run RAG with streaming: yield retrieval event, token events, then complete event.
    On no context or error, yield error or complete with fallback answer.
    When session_id is set, persists user + assistant messages and adds message_id to complete.
    Event shapes: {"event": "retrieval"|"token"|"complete"|"error", "data": {...}}.
    """
    settings = get_settings()
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_chat_model,
        timeout_seconds=float(settings.ollama_timeout_seconds),
    )

    session_was_first = False
    if req.session_id:
        session = get_session(req.session_id)
        if not session:
            yield {"event": "error", "data": {"message": "Session not found"}}
            return
        session_was_first = (session.get("message_count") or 0) == 0
        append_user_message(req.session_id, req.message)

    memory_messages = _get_memory_context(req.session_id, req.use_session_memory)

    try:
        retrieval_result = retrieve(
            query=req.message,
            top_k=req.top_k,
            min_score=req.min_score,
            max_context_chars=None,
        )
    except Exception as e:
        yield {"event": "error", "data": {"message": f"Retrieval failed: {e}"}}
        return

    yield {
        "event": "retrieval",
        "data": {
            "retrieved_count": retrieval_result.retrieved_count,
            "selected_count": retrieval_result.selected_count,
        },
    }

    if not retrieval_result.chunks:
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
                session_id=req.session_id,
                memory_messages_used=len(memory_messages) if memory_messages else None,
            )
        complete_data = {
            "model": settings.ollama_chat_model,
            "answer": INSUFFICIENT_EVIDENCE_ANSWER,
            "sources": [],
            "debug": debug.model_dump() if debug else None,
        }
        if req.session_id:
            rec = append_assistant_message(
                req.session_id,
                INSUFFICIENT_EVIDENCE_ANSWER,
                error=None,
            )
            if rec:
                complete_data["message_id"] = rec.get("id")
            if session_was_first:
                update_session_title_from_first_message(req.session_id, req.message)
        yield {"event": "complete", "data": complete_data}
        return

    messages = build_rag_messages(
        question=req.message,
        chunks=retrieval_result.chunks,
        prompt_name=settings.rag_system_prompt_name,
        conversation_history=memory_messages if memory_messages else None,
    )

    accumulated: List[str] = []
    try:
        for chunk in client.chat_with_options_stream(
            messages=messages,
            temperature=settings.rag_temperature,
        ):
            accumulated.append(chunk)
            yield {"event": "token", "data": {"text": chunk}}
    except Exception as e:
        yield {"event": "error", "data": {"message": str(e)}}
        return

    answer = "".join(accumulated).strip() or INSUFFICIENT_EVIDENCE_ANSWER
    model_used = settings.ollama_chat_model
    sources = (
        [_search_match_to_rag_source(m) for m in retrieval_result.chunks]
        if req.include_sources
        else []
    )
    debug_data = None
    if req.include_debug:
        debug_data = RAGDebugInfo(
            top_k_used=retrieval_result.top_k_used,
            min_score_used=retrieval_result.min_score_used,
            context_char_count=retrieval_result.context_char_count,
            retrieved_count=retrieval_result.retrieved_count,
            selected_count=retrieval_result.selected_count,
            model=model_used,
            prompt_name=settings.rag_system_prompt_name,
            session_id=req.session_id,
            memory_messages_used=len(memory_messages) if memory_messages else None,
        ).model_dump()

    complete_data = {
        "model": model_used,
        "answer": answer,
        "sources": [s.model_dump() for s in sources],
        "debug": debug_data,
    }
    if req.session_id:
        sources_json = json.dumps([s.model_dump() for s in sources]) if sources else None
        rec = append_assistant_message(
            req.session_id,
            answer,
            sources_json=sources_json,
            debug_json=json.dumps(debug_data) if debug_data else None,
        )
        if rec:
            complete_data["message_id"] = rec.get("id")
        if session_was_first:
            update_session_title_from_first_message(req.session_id, req.message)
    yield {"event": "complete", "data": complete_data}


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
