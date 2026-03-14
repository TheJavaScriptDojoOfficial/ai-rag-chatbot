"""
ChromaDB persistent vector store. Add chunks with embeddings, search by query embedding.
"""
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _metadata_for_chroma(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure metadata values are Chroma-compatible (str, int, float)."""
    out: Dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


class ChromaStore:
    """Persistent Chroma collection for chunk storage and similarity search."""

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
    ):
        self.persist_directory = str(Path(persist_directory).resolve())
        self.collection_name = collection_name
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=self.persist_directory)
        # Collection without embedding function; we supply embeddings ourselves
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine", "description": "Company knowledge base chunks"},
        )

    def add_chunks(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Upsert chunks. All lists must have the same length."""
        if not ids:
            return
        if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
            raise ValueError("ids, documents, embeddings, metadatas must have same length")
        chroma_metas = [_metadata_for_chroma(m) for m in metadatas]
        self._collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=chroma_metas,
        )

    def delete_by_source_id(self, source_id: str) -> None:
        """Remove all chunks with the given source_id (for re-indexing one doc)."""
        existing = self._collection.get(where={"source_id": source_id}, include=[])
        ids = existing.get("ids") if existing else []
        if ids:
            self._collection.delete(ids=ids)

    def reset(self) -> None:
        """Delete and recreate the collection."""
        self._client.delete_collection(name=self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "description": "Company knowledge base chunks"},
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        include_documents: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Similarity search. Returns list of dicts with id, document (if requested),
        metadata, distance (Chroma uses L2; we expose as-is or convert to similarity).
        """
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, 100),
            include=["documents", "metadatas", "distances"],
        )
        ids = results["ids"][0] if results["ids"] else []
        docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

        out = []
        for i, chunk_id in enumerate(ids):
            item: Dict[str, Any] = {
                "id": chunk_id,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distances[i] if i < len(distances) else 0.0,
            }
            if include_documents and i < len(docs):
                item["document"] = docs[i] or ""
            out.append(item)
        return out

    def count(self) -> int:
        """Total number of chunks in the collection."""
        return self._collection.count()


@lru_cache(maxsize=1)
def get_chroma_store() -> ChromaStore:
    """Build ChromaStore from app config. Cached so we reuse the same client per process (faster search)."""
    s = get_settings()
    return ChromaStore(
        persist_directory=s.chroma_persist_directory,
        collection_name=s.chroma_collection_name,
    )
