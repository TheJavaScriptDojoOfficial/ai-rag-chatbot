"""
Environment-based configuration. Load from env with clean defaults for local dev.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Company RAG API"
    app_env: str = "development"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen2.5:7b"
    ollama_timeout_seconds: int = 120

    # Document ingestion (Phase 3)
    docs_base_path: str = "./docs"
    ingest_max_file_size_mb: int = 10
    chunk_size_chars: int = 1500
    chunk_overlap_chars: int = 200
    allowed_doc_extensions: str = ".pdf,.md,.txt"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [e.strip().lower() for e in self.allowed_doc_extensions.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
