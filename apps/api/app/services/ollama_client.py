"""
Ollama client service. Handles availability check and plain chat completion.
Uses httpx; returns normalized Python data. Supports streaming via chat_with_options_stream.
"""
import json
import logging
from typing import Any, Dict, Iterator, List, Optional

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

    def chat_with_options(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> Dict[str, str]:
        """
        Send a list of messages (e.g. system + user) to Ollama chat API.
        Optional temperature. Returns {"model": "...", "response": "..."}.
        Raises OllamaError on failure.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if temperature is not None:
            payload["options"] = {"temperature": temperature}
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

    def chat_with_options_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> Iterator[str]:
        """
        Stream chat completion from Ollama. Yields incremental text chunks.
        Does not raise; yields nothing and returns on connection/parse errors.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if temperature is not None:
            payload["options"] = {"temperature": temperature}
        try:
            with self._client() as client:
                with client.stream("POST", "/api/chat", json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line or not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if not isinstance(data, dict):
                            continue
                        msg = data.get("message")
                        if isinstance(msg, dict):
                            content = msg.get("content")
                            if isinstance(content, str) and content:
                                yield content
        except httpx.TimeoutException:
            logger.warning("Ollama stream timeout: %s", self.base_url)
        except httpx.ConnectError as e:
            logger.warning("Ollama stream connection failed: %s", e)
        except httpx.HTTPStatusError as e:
            logger.warning("Ollama stream HTTP error: %s", e.response.status_code)
        except Exception as e:
            logger.warning("Ollama stream error: %s", e)
