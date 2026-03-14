"""
Retrieval for RAG: search, filter by score, dedupe, trim to max context chars.
Reuses index_service.run_search; no duplicate embedding/Chroma logic.
"""
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from app.core.config import get_settings
from app.schemas.vector import SearchMatch
from app.services.indexing.index_service import run_search


@dataclass
class RetrievalResult:
    """Selected chunks + debug info."""

    chunks: List[SearchMatch]
    retrieved_count: int
    selected_count: int
    context_char_count: int
    top_k_used: int
    min_score_used: float


def retrieve(
    query: str,
    top_k: Optional[int] = None,
    min_score: Optional[float] = None,
    max_context_chars: Optional[int] = None,
) -> RetrievalResult:
    """
    Run semantic search, filter by min_score, dedupe by (source_id, chunk_index),
    trim to max_context_chars. Returns selected chunks and debug counts.
    """
    settings = get_settings()
    k = top_k if top_k is not None else settings.rag_top_k
    threshold = min_score if min_score is not None else settings.rag_min_score
    max_chars = max_context_chars if max_context_chars is not None else settings.rag_max_context_chars

    search_resp = run_search(query=query, top_k=k, include_text=True)
    if search_resp.status == "error" or not search_resp.matches:
        return RetrievalResult(
            chunks=[],
            retrieved_count=0,
            selected_count=0,
            context_char_count=0,
            top_k_used=k,
            min_score_used=threshold,
        )

    # Filter by score; dedupe by (source_id, chunk_index)
    seen: Set[Tuple[str, int]] = set()
    selected: List[SearchMatch] = []
    for m in search_resp.matches:
        if m.score < threshold:
            continue
        key = (m.source_id, m.chunk_index)
        if key in seen:
            continue
        seen.add(key)
        selected.append(m)

    # Trim to max_context_chars (order preserved)
    total_chars = 0
    trimmed: List[SearchMatch] = []
    for m in selected:
        chunk_len = len(m.text)
        if total_chars + chunk_len > max_chars and trimmed:
            break
        trimmed.append(m)
        total_chars += chunk_len

    return RetrievalResult(
        chunks=trimmed,
        retrieved_count=len(search_resp.matches),
        selected_count=len(trimmed),
        context_char_count=total_chars,
        top_k_used=k,
        min_score_used=threshold,
    )
