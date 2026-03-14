"""
Orchestrates ingestion -> embeddings -> vector store. Reuses ingestion pipeline.
"""
import logging
from typing import List, Optional

from app.core.config import get_settings
from app.schemas.vector import (
    IndexDocumentResult,
    IndexResponse,
    SearchMatch,
    SearchResponse,
)
from app.services.embeddings import EmbeddingsError, embed_texts
from app.services.ingestion.ingest_service import IndexableDoc, run_ingest_for_indexing
from app.services.vector_store.chroma_store import ChromaStore, get_chroma_store

logger = logging.getLogger(__name__)

# Batch size for embedding calls to avoid huge payloads
EMBED_BATCH_SIZE = 32


def run_index(
    path_override: Optional[str] = None,
    recursive: bool = True,
    reset_collection: bool = False,
    include_chunk_details: bool = False,
) -> IndexResponse:
    """
    Run ingestion, generate embeddings, write to vector store.
    Optionally reset collection first. Re-indexing a doc deletes its old chunks then adds new.
    """
    settings = get_settings()
    store = get_chroma_store()

    if reset_collection:
        try:
            store.reset()
        except Exception as e:
            logger.exception("Failed to reset collection: %s", e)
            return IndexResponse(
                status="error",
                collection_name=settings.chroma_collection_name,
                total_files=0,
                processed_files=0,
                skipped_files=0,
                indexed_chunks=0,
                documents=[],
                errors=[f"Failed to reset collection: {e}"],
            )

    indexable_docs, errors, total_files, processed_files, skipped_files = run_ingest_for_indexing(
        path_override=path_override,
        recursive=recursive,
    )

    if not indexable_docs:
        return IndexResponse(
            status="partial" if errors else "ok",
            collection_name=settings.chroma_collection_name,
            total_files=total_files,
            processed_files=processed_files,
            skipped_files=skipped_files,
            indexed_chunks=0,
            documents=[],
            errors=errors,
        )

    total_indexed = 0
    doc_results: List[IndexDocumentResult] = []

    for doc in indexable_docs:
        # Remove existing chunks for this source (re-index)
        try:
            store.delete_by_source_id(doc.source_id)
        except Exception as e:
            logger.warning("Delete by source_id failed for %s: %s", doc.source_id, e)
            errors.append(f"Delete before re-index failed for {doc.file_name}: {e}")

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[dict] = []

        for c in doc.chunks:
            meta = {
                "source_id": doc.source_id,
                "file_name": doc.file_name,
                "file_path": doc.file_path,
                "extension": doc.extension,
                "chunk_index": c.chunk_index,
                "start_char": c.start_char,
                "end_char": c.end_char,
                "loader_type": doc.loader_type,
            }
            if doc.page_count is not None:
                meta["page_count"] = doc.page_count
            ids.append(c.chunk_id)
            documents.append(c.text)
            metadatas.append(meta)

        if not ids:
            continue

        # Embed in batches
        all_embeddings: List[List[float]] = []
        for i in range(0, len(documents), EMBED_BATCH_SIZE):
            batch = documents[i : i + EMBED_BATCH_SIZE]
            try:
                vectors, _ = embed_texts(batch)
                all_embeddings.extend(vectors)
            except EmbeddingsError as e:
                errors.append(f"Embedding failed for {doc.file_name}: {e.message}")
                break
        if len(all_embeddings) != len(ids):
            continue

        try:
            store.add_chunks(ids=ids, documents=documents, embeddings=all_embeddings, metadatas=metadatas)
        except Exception as e:
            logger.exception("Chroma add_chunks failed: %s", e)
            errors.append(f"Vector store add failed for {doc.file_name}: {e}")
            continue

        total_indexed += len(ids)
        doc_results.append(
            IndexDocumentResult(
                source_id=doc.source_id,
                file_name=doc.file_name,
                chunk_count=len(doc.chunks),
                indexed_chunk_count=len(ids),
                metadata={"loader_type": doc.loader_type, "page_count": doc.page_count},
            )
        )

    status = "ok" if not errors and skipped_files == 0 else "partial"
    return IndexResponse(
        status=status,
        collection_name=settings.chroma_collection_name,
        total_files=total_files,
        processed_files=processed_files,
        skipped_files=skipped_files,
        indexed_chunks=total_indexed,
        documents=doc_results,
        errors=errors,
    )


def run_search(
    query: str,
    top_k: Optional[int] = None,
    include_text: bool = True,
) -> SearchResponse:
    """Embed query, search Chroma, return matches. No answer generation."""
    settings = get_settings()
    store = get_chroma_store()
    k = top_k if top_k is not None else settings.vector_search_top_k

    try:
        query_vectors, _ = embed_texts([query])
    except EmbeddingsError as e:
        return SearchResponse(
            status="error",
            query=query,
            collection_name=settings.chroma_collection_name,
            match_count=0,
            matches=[],
        )

    if not query_vectors:
        return SearchResponse(
            status="ok",
            query=query,
            collection_name=settings.chroma_collection_name,
            match_count=0,
            matches=[],
        )

    raw = store.search(
        query_embedding=query_vectors[0],
        top_k=k,
        include_documents=include_text,
    )

    # Chroma returns L2 distance (lower = more similar). Convert to score in (0, 1], higher = better.
    matches: List[SearchMatch] = []
    for item in raw:
        dist = item.get("distance", 0.0)
        score = 1.0 / (1.0 + dist) if dist is not None else 1.0
        meta = item.get("metadata") or {}
        text = item.get("document", "") if include_text else ""
        matches.append(
            SearchMatch(
                chunk_id=item.get("id", ""),
                source_id=meta.get("source_id", ""),
                file_name=meta.get("file_name", ""),
                chunk_index=int(meta.get("chunk_index", 0)),
                score=round(score, 4),
                text=text,
                metadata=meta,
            )
        )

    return SearchResponse(
        status="ok",
        query=query,
        collection_name=settings.chroma_collection_name,
        match_count=len(matches),
        matches=matches,
    )
