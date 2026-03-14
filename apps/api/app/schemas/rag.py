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
    session_id: Optional[str] = Field(None, description="If set, store messages and optionally use recent history")
    use_session_memory: bool = Field(True, description="When session_id is set, include recent conversation in prompt")


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
    session_id: Optional[str] = None
    memory_messages_used: Optional[int] = None


class RAGChatResponse(BaseModel):
    """Response for POST /rag/chat."""

    mode: str = Field("rag", description="Always 'rag' for this endpoint")
    model: str
    answer: str
    sources: List[RAGSource] = Field(default_factory=list)
    debug: Optional[RAGDebugInfo] = Field(None)
    message_id: Optional[str] = Field(None, description="Stored assistant message id when session_id was set")


class RetrievalCandidate(BaseModel):
    """Internal/API: one retrieved chunk candidate."""

    chunk_id: str
    score: float
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
