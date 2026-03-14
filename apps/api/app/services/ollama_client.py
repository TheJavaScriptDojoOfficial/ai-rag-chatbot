"""
Ollama client service. Handles availability check and plain chat completion.
Uses httpx; returns normalized Python data. Easy to extend for streaming/RAG later.
"""
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Raised when Ollama request fails in a way we can interpret."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout_seconds

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def is_reachable(self) -> bool:
        """Check if Ollama service is available (e.g. GET /api/tags)."""
        try:
            with self._client() as client:
                r = client.get("/api/tags")
                r.raise_for_status()
                return True
        except httpx.TimeoutException:
            logger.warning("Ollama timeout when checking reachability: %s", self.base_url)
            return False
        except httpx.ConnectError as e:
            logger.warning("Ollama connection failed: %s", e)
            return False
        except httpx.HTTPStatusError as e:
            logger.warning("Ollama returned error status: %s", e.response.status_code)
            return False
        except Exception as e:
            logger.warning("Ollama reachability check failed: %s", e)
            return False

    def chat(self, message: str) -> dict[str, str]:
        """
        Send a single user message to Ollama chat API. Returns normalized
        {"model": "...", "response": "..."}. Raises OllamaError on failure.
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }
        try:
            with self._client() as client:
                r = client.post("/api/chat", json=payload)
                r.raise_for_status()
        except httpx.TimeoutException:
            raise OllamaError(
                "Ollama request timed out",
                details=f"timeout_seconds={self.timeout}",
            )
        except httpx.ConnectError as e:
            raise OllamaError(
                "Could not connect to Ollama",
                details=str(e),
            )
        except httpx.HTTPStatusError as e:
            raise OllamaError(
                f"Ollama returned error: {e.response.status_code}",
                status_code=e.response.status_code,
                details=e.response.text[:500] if e.response.text else None,
            )

        data = r.json()
        if not isinstance(data, dict):
            raise OllamaError("Invalid Ollama response: not a JSON object", details=data)

        msg = data.get("message")
        if not isinstance(msg, dict):
            raise OllamaError("Invalid Ollama response: missing or invalid 'message'", details=data)

        content = msg.get("content")
        if content is None:
            content = ""
        if not isinstance(content, str):
            content = str(content)

        return {
            "model": data.get("model") or self.model,
            "response": content,
        }
