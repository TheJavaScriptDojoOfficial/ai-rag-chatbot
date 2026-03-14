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
    ollama_num_ctx: int = 4096

    # Document ingestion (Phase 3)
    docs_base_path: str = "./docs"
    ingest_max_file_size_mb: int = 10
    chunk_size_chars: int = 1500
    chunk_overlap_chars: int = 200
    allowed_doc_extensions: str = ".pdf,.md,.txt"

    # Vector DB and embeddings (Phase 4)
    vector_db_provider: str = "chroma"
    chroma_persist_directory: str = "./data/chroma"
    chroma_collection_name: str = "company_knowledge_base"
    ollama_embed_model: str = "nomic-embed-text"
    vector_search_top_k: int = 5

    # RAG orchestration (Phase 5)
    rag_top_k: int = 5
    rag_max_context_chars: int = 6000
    rag_min_score: float = 0.15
    rag_temperature: float = 0.2
    rag_system_prompt_name: str = "default_company_assistant"

    # Session and feedback storage (Phase 8)
    app_data_directory: str = "./data/app"
    sqlite_db_path: str = "./data/app/chatbot.sqlite3"
    max_session_messages_for_context: int = 8
    session_title_max_chars: int = 80

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [e.strip().lower() for e in self.allowed_doc_extensions.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
