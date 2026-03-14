"""
Request/response schemas for RAG chat. Citation-ready sources.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RAGChatRequest(BaseModel):
    """POST /rag/chat body."""

    message: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(None, ge=1, le=50)
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    include_sources: bool = Field(True, description="Include source chunks in response")
    include_debug: bool = Field(False, description="Include retrieval/generation debug info")


class RAGSource(BaseModel):
    """One source chunk for citation."""

    chunk_id: str
    source_id: str
    file_name: str
    file_path: str = ""
    chunk_index: int
    score: float
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGDebugInfo(BaseModel):
    """Debug info for RAG run."""

    top_k_used: int
    min_score_used: float
    context_char_count: int
    retrieved_count: int
    selected_count: int
    model: str
    prompt_name: str


class RAGChatResponse(BaseModel):
    """Response for POST /rag/chat."""

    mode: str = Field("rag", description="Always 'rag' for this endpoint")
    model: str
    answer: str
    sources: List[RAGSource] = Field(default_factory=list)
    debug: Optional[RAGDebugInfo] = Field(None)


class RetrievalCandidate(BaseModel):
    """Internal/API: one retrieved chunk candidate."""

    chunk_id: str
    score: float
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
