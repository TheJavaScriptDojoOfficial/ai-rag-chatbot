"""
Ingestion preview routes. No persistence; development preview only.
"""
from pathlib import Path

from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from app.core.config import get_settings
from app.schemas.ingest import IngestPreviewRequest, IngestPreviewResponse
from app.services.ingestion.ingest_service import run_ingest_preview

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.get("/health")
def ingest_health():
    """
    Verify ingestion config is loaded and docs path exists.
    """
    settings = get_settings()
    base = settings.docs_base_path
    if not base or not base.strip():
        raise HTTPException(
            status_code=500,
            detail={"error": "config_error", "message": "DOCS_BASE_PATH is not set"},
        )
    resolved = (Path.cwd() / base) if not Path(base).is_absolute() else Path(base)
    resolved = resolved.resolve()
    path_exists = resolved.is_dir()
    return {
        "status": "ok",
        "docs_base_path": base,
        "path_exists": path_exists,
        "resolved_path": str(resolved),
        "allowed_extensions": settings.allowed_extensions_list,
    }


@router.post("/preview", response_model=IngestPreviewResponse)
def ingest_preview(body: Optional[IngestPreviewRequest] = Body(None)):
    """
    Scan docs folder, parse files, normalize, chunk; return preview JSON.
    No persistence. Optional body: path, recursive, include_chunks.
    """
    if body is None:
        body = IngestPreviewRequest(path=None, recursive=True, include_chunks=True)
    path_override = body.path if body.path and body.path.strip() else None
    result = run_ingest_preview(
        path_override=path_override,
        recursive=body.recursive,
        include_chunks=body.include_chunks,
    )
    return result
