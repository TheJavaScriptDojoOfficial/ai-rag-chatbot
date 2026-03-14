"""
Request/response schemas for ingestion preview. No persistence in this phase.
"""
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class DocumentChunkPreview(BaseModel):
    """Single chunk preview."""

    chunk_id: str = Field(..., description="Stable chunk identifier")
    chunk_index: int = Field(..., ge=0)
    text: str = Field(..., description="Chunk text")
    char_count: int = Field(..., ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestedDocumentPreview(BaseModel):
    """One processed document with optional chunks."""

    source_id: str = Field(..., description="Stable document id")
    file_name: str = Field(...)
    file_path: str = Field(...)
    extension: str = Field(...)
    char_count: int = Field(..., ge=0)
    chunk_count: int = Field(..., ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    chunks: List[DocumentChunkPreview] = Field(default_factory=list)


class IngestPreviewResponse(BaseModel):
    """Response for POST /ingest/preview."""

    status: str = Field(..., description="ok or partial")
    total_files: int = Field(..., ge=0)
    processed_files: int = Field(..., ge=0)
    skipped_files: int = Field(..., ge=0)
    documents: List[IngestedDocumentPreview] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list, description="Non-fatal errors encountered")


class IngestPreviewRequest(BaseModel):
    """Optional body for POST /ingest/preview."""

    path: Optional[str] = Field(None, description="Override docs base path")
    recursive: bool = Field(True, description="Scan subdirectories")
    include_chunks: bool = Field(True, description="Include chunk previews in response")
