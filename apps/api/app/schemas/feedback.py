"""
Request/response schemas for answer feedback.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FeedbackSubmitRequest(BaseModel):
    session_id: str
    message_id: str
    feedback_type: str = Field(..., pattern="^(up|down)$")
    comment: Optional[str] = Field(None, max_length=2000)
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    debug: Optional[Dict[str, Any]] = None


class FeedbackSubmitResponse(BaseModel):
    status: str = "ok"
    feedback_id: str
