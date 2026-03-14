"""
Orchestrates document scan, load, normalize, chunk; returns preview data.
No persistence or Ollama. Independent of FastAPI.
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.config import get_settings
from app.schemas.ingest import (
    DocumentChunkPreview,
    IngestedDocumentPreview,
    IngestPreviewResponse,
)
from app.services.ingestion.chunker import Chunk, chunk_text
from app.services.ingestion.loader import load_document, LoadedDocument
from app.services.ingestion.normalizer import normalize_text
from app.utils.files import scan_docs_folder, ScannedFile


class IndexableDoc:
    """One document's chunks ready for embedding and vector store. Used by index_service."""

    __slots__ = ("source_id", "file_name", "file_path", "extension", "loader_type", "page_count", "chunks")

    def __init__(
        self,
        source_id: str,
        file_name: str,
        file_path: str,
        extension: str,
        loader_type: str,
        page_count: Optional[int],
        chunks: List[Chunk],
    ):
        self.source_id = source_id
        self.file_name = file_name
        self.file_path = file_path
        self.extension = extension
        self.loader_type = loader_type
        self.page_count = page_count
        self.chunks = chunks


def run_ingest_preview(
    path_override: Optional[str] = None,
    recursive: bool = True,
    include_chunks: bool = True,
) -> IngestPreviewResponse:
    """
    Scan, load, normalize, chunk documents and return preview.
    One bad file does not stop the run; errors are collected.
    """
    settings = get_settings()
    base_path = path_override or settings.docs_base_path
    # Resolve relative to cwd when path is relative
    if not os.path.isabs(base_path):
        base_path = str(Path.cwd() / base_path)
    else:
        base_path = str(Path(base_path).resolve())

    scanned = scan_docs_folder(
        base_path=base_path,
        allowed_extensions=settings.allowed_extensions_list,
        max_file_size_mb=float(settings.ingest_max_file_size_mb),
        recursive=recursive,
    )
    total_files = len(scanned)
    processed = 0
    skipped = 0
    errors: List[str] = []
    documents: List[IngestedDocumentPreview] = []

    for f in scanned:
        doc = _process_one_file(
            f,
            settings.chunk_size_chars,
            settings.chunk_overlap_chars,
            include_chunks,
            errors,
        )
        if doc is None:
            skipped += 1
            continue
        processed += 1
        documents.append(doc)

    status = "ok" if (errors == [] and skipped == 0) else "partial"
    return IngestPreviewResponse(
        status=status,
        total_files=total_files,
        processed_files=processed,
        skipped_files=skipped,
        documents=documents,
        errors=errors,
    )


def _process_one_file(
    scanned: ScannedFile,
    chunk_size: int,
    chunk_overlap: int,
    include_chunks: bool,
    errors: List[str],
) -> Optional[IngestedDocumentPreview]:
    """Load, normalize, chunk one file. Returns None on failure."""
    loaded: Optional[LoadedDocument] = load_document(scanned.file_path, scanned.extension)
    if loaded is None:
        errors.append(f"Could not load: {scanned.file_path}")
        return None

    normalized = normalize_text(loaded.text)
    if not normalized.strip():
        errors.append(f"Empty text after normalize: {scanned.file_path}")
        return None

    chunks = chunk_text(
        normalized,
        source_id=loaded.source_id,
        file_name=loaded.file_name,
        chunk_size=chunk_size,
        overlap=chunk_overlap,
    )
    if not chunks:
        errors.append(f"No chunks produced: {scanned.file_path}")
        return None

    meta = {"loader_type": loaded.loader_type}
    if loaded.page_count is not None:
        meta["page_count"] = loaded.page_count

    chunk_previews = []
    if include_chunks:
        for c in chunks:
            chunk_previews.append(
                DocumentChunkPreview(
                    chunk_id=c.chunk_id,
                    chunk_index=c.chunk_index,
                    text=c.text,
                    char_count=len(c.text),
                    metadata={
                        "start_char": c.start_char,
                        "end_char": c.end_char,
                        "source_id": c.source_id,
                        "file_name": c.file_name,
                    },
                )
            )

    return IngestedDocumentPreview(
        source_id=loaded.source_id,
        file_name=loaded.file_name,
        file_path=loaded.file_path,
        extension=loaded.extension,
        char_count=len(normalized),
        chunk_count=len(chunks),
        metadata=meta,
        chunks=chunk_previews,
    )


def run_ingest_for_indexing(
    path_override: Optional[str] = None,
    recursive: bool = True,
) -> Tuple[List[IndexableDoc], List[str], int, int, int]:
    """
    Same pipeline as preview but returns indexable docs (chunks + metadata) for vector indexing.
    Returns (indexable_docs, errors, total_files, processed_files, skipped_files).
    """
    settings = get_settings()
    base_path = path_override or settings.docs_base_path
    if not os.path.isabs(base_path):
        base_path = str(Path.cwd() / base_path)
    else:
        base_path = str(Path(base_path).resolve())

    scanned = scan_docs_folder(
        base_path=base_path,
        allowed_extensions=settings.allowed_extensions_list,
        max_file_size_mb=float(settings.ingest_max_file_size_mb),
        recursive=recursive,
    )
    total_files = len(scanned)
    processed = 0
    skipped = 0
    errors: List[str] = []
    indexable_docs: List[IndexableDoc] = []

    for f in scanned:
        doc = _process_one_file_for_indexing(
            f,
            settings.chunk_size_chars,
            settings.chunk_overlap_chars,
            errors,
        )
        if doc is None:
            skipped += 1
            continue
        processed += 1
        indexable_docs.append(doc)

    return indexable_docs, errors, total_files, processed, skipped


def _process_one_file_for_indexing(
    scanned: ScannedFile,
    chunk_size: int,
    chunk_overlap: int,
    errors: List[str],
) -> Optional[IndexableDoc]:
    """Load, normalize, chunk; return IndexableDoc or None."""
    loaded: Optional[LoadedDocument] = load_document(scanned.file_path, scanned.extension)
    if loaded is None:
        errors.append(f"Could not load: {scanned.file_path}")
        return None

    normalized = normalize_text(loaded.text)
    if not normalized.strip():
        errors.append(f"Empty text after normalize: {scanned.file_path}")
        return None

    chunks = chunk_text(
        normalized,
        source_id=loaded.source_id,
        file_name=loaded.file_name,
        chunk_size=chunk_size,
        overlap=chunk_overlap,
    )
    if not chunks:
        errors.append(f"No chunks produced: {scanned.file_path}")
        return None

    return IndexableDoc(
        source_id=loaded.source_id,
        file_name=loaded.file_name,
        file_path=loaded.file_path,
        extension=loaded.extension,
        loader_type=loaded.loader_type,
        page_count=loaded.page_count,
        chunks=chunks,
    )
