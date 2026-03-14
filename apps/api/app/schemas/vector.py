"""
Request/response schemas for vector indexing and semantic search.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    """POST /vector/index body."""

    path: Optional[str] = Field(None, description="Override docs base path")
    recursive: bool = Field(True, description="Scan subdirectories")
    reset_collection: bool = Field(False, description="Clear collection before indexing")
    include_chunks: bool = Field(False, description="Include chunk details in response")


class IndexedChunkResult(BaseModel):
    """One indexed chunk in index response."""

    chunk_id: str
    chunk_index: int
    file_name: str
    source_id: str
    char_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IndexDocumentResult(BaseModel):
    """One indexed document in index response."""

    source_id: str
    file_name: str
    chunk_count: int
    indexed_chunk_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IndexResponse(BaseModel):
    """Response for POST /vector/index."""

    status: str
    collection_name: str
    total_files: int = Field(..., ge=0)
    processed_files: int = Field(..., ge=0)
    skipped_files: int = Field(..., ge=0)
    indexed_chunks: int = Field(..., ge=0)
    documents: List[IndexDocumentResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """POST /vector/search body."""

    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(None, ge=1, le=100, description="Override default top_k")
    path_filter: Optional[str] = Field(None, description="Future: filter by path")
    include_text: bool = Field(True, description="Include chunk text in matches")


class SearchMatch(BaseModel):
    """One search result chunk."""

    chunk_id: str
    source_id: str
    file_name: str
    chunk_index: int
    score: float = Field(..., description="Similarity score (higher = more similar)")
    text: str = Field("", description="Chunk text when include_text=true")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response for POST /vector/search."""

    status: str
    query: str
    collection_name: str
    match_count: int = Field(..., ge=0)
    matches: List[SearchMatch] = Field(default_factory=list)
