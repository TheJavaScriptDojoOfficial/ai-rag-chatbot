"""
Vector DB routes: health, index, search. No RAG answer generation.
"""
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from app.core.config import get_settings
from app.schemas.vector import (
    IndexRequest,
    IndexResponse,
    SearchRequest,
    SearchResponse,
)
from app.services.indexing.index_service import run_index, run_search
from app.services.vector_store.chroma_store import get_chroma_store

router = APIRouter(prefix="/vector", tags=["vector"])


@router.get("/health")
def vector_health():
    """
    Verify vector config, Chroma path, collection access, embed model config.
    Does not require collection to be non-empty.
    """
    settings = get_settings()
    try:
        store = get_chroma_store()
        _ = store.count()
    except Exception as e:
        return {
            "status": "degraded",
            "provider": settings.vector_db_provider,
            "collection_name": settings.chroma_collection_name,
            "persist_directory": settings.chroma_persist_directory,
            "embed_model": settings.ollama_embed_model,
            "error": str(e),
        }
    return {
        "status": "ok",
        "provider": settings.vector_db_provider,
        "collection_name": settings.chroma_collection_name,
        "persist_directory": settings.chroma_persist_directory,
        "embed_model": settings.ollama_embed_model,
    }


@router.post("/index", response_model=IndexResponse)
def vector_index(body: Optional[IndexRequest] = Body(None)):
    """
    Run document indexing: ingestion -> embeddings -> vector store.
    Optional body: path, recursive, reset_collection, include_chunks.
    """
    if body is None:
        body = IndexRequest(path=None, recursive=True, reset_collection=False, include_chunks=False)
    path_override = body.path if body.path and body.path.strip() else None
    result = run_index(
        path_override=path_override,
        recursive=body.recursive,
        reset_collection=body.reset_collection,
        include_chunk_details=body.include_chunks,
    )
    return result


@router.post("/search", response_model=SearchResponse)
def vector_search(body: SearchRequest):
    """Semantic search preview. Returns matching chunks; no answer generation."""
    result = run_search(
        query=body.query,
        top_k=body.top_k,
        include_text=body.include_text,
    )
    if result.status == "error":
        raise HTTPException(status_code=503, detail="Embedding or search failed")
    return result


@router.delete("/index")
def vector_index_delete():
    """
    Clear the vector collection. For local testing only.
    """
    settings = get_settings()
    try:
        store = get_chroma_store()
        store.reset()
        return {
            "status": "ok",
            "message": "Collection cleared",
            "collection_name": settings.chroma_collection_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "reset_failed", "message": str(e)})
