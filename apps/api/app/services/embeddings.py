"""
Embeddings generation via Ollama. Abstracted for potential swap of provider later.
"""
import logging
from typing import List, Optional

import httpx

from app.core.config import get_settings
from app.services.ollama_client import OllamaError

logger = logging.getLogger(__name__)


class EmbeddingsError(Exception):
    """Raised when embedding request fails."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


def get_embedding_client():
    """Return (base_url, model, timeout) from settings for embedding calls."""
    s = get_settings()
    return s.ollama_base_url.rstrip("/"), s.ollama_embed_model, float(s.ollama_timeout_seconds)


def embed_texts(texts: List[str]) -> tuple[List[List[float]], str]:
    """
    Generate embeddings for a list of texts via Ollama POST /api/embed.
    Returns (list of embedding vectors, model_name). Raises EmbeddingsError on failure.
    """
    if not texts:
        return [], get_settings().ollama_embed_model

    base_url, model, timeout = get_embedding_client()
    payload = {"model": model, "input": texts if len(texts) > 1 else texts[0]}

    try:
        with httpx.Client(base_url=base_url, timeout=timeout) as client:
            r = client.post("/api/embed", json=payload)
            r.raise_for_status()
    except httpx.TimeoutException:
        raise EmbeddingsError("Ollama embeddings request timed out", details=f"timeout={timeout}s")
    except httpx.ConnectError as e:
        raise EmbeddingsError("Could not connect to Ollama for embeddings", details=str(e))
    except httpx.HTTPStatusError as e:
        raise EmbeddingsError(
            f"Ollama embeddings error: {e.response.status_code}",
            details=e.response.text[:500] if e.response.text else None,
        )

    data = r.json()
    if not isinstance(data, dict):
        raise EmbeddingsError("Invalid Ollama embeddings response: not a JSON object", details=str(data))

    raw = data.get("embeddings")
    if raw is None:
        raise EmbeddingsError("Invalid Ollama embeddings response: missing 'embeddings'", details=str(data))

    if not isinstance(raw, list):
        raise EmbeddingsError("Invalid Ollama embeddings response: 'embeddings' not a list", details=str(data)[:500])

    if len(raw) == 0:
        return [], data.get("model") or model

    # Single input can return one vector as flat list of numbers
    if len(raw) == 1 and isinstance(raw[0], (int, float)):
        vectors = [raw]
    elif all(isinstance(x, (int, float)) for x in raw):
        vectors = [raw]
    elif all(isinstance(x, list) for x in raw):
        vectors = raw
    else:
        raise EmbeddingsError("Invalid Ollama embeddings response: unexpected embeddings shape", details=str(data)[:500])

    model_used = data.get("model") or model
    return vectors, model_used
