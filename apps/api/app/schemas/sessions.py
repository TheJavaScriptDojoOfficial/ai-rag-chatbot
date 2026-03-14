"""
Request/response schemas for chat sessions and messages.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SessionSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


class ChatMessageRecord(BaseModel):
    id: str
    session_id: str
    role: str
    content: str = ""
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    debug: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    sequence_number: int


class CreateSessionRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=500)


class CreateSessionResponse(BaseModel):
    session: SessionSummary


class SessionListResponse(BaseModel):
    sessions: List[SessionSummary]


class SessionDetailResponse(BaseModel):
    session: SessionSummary
    messages: List[ChatMessageRecord]


class RenameSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
