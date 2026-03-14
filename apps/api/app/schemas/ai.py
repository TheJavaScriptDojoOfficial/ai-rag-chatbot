"""
Request/response schemas for AI routes.
"""
from pydantic import BaseModel, Field


class AIModelHealthResponse(BaseModel):
    """GET /ai/health — Ollama runtime status."""

    status: str = Field(..., description="ok or error/degraded")
    ollama_reachable: bool = Field(..., description="Whether Ollama responded")
    base_url: str = Field(..., description="Ollama base URL used")
    model: str = Field(..., description="Configured chat model name")


class PlainPromptRequest(BaseModel):
    """POST /ai/chat — single user message."""

    message: str = Field(..., min_length=1, description="User message to send to the model")


class PlainPromptResponse(BaseModel):
    """POST /ai/chat — model reply."""

    model: str = Field(..., description="Model that generated the response")
    response: str = Field(..., description="Model output text")
