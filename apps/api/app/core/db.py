"""
SQLite initialization for chat sessions and feedback. Ensures data dir and tables exist.
"""
import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New chat',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    sources_json TEXT,
    debug_json TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS answer_feedback (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    comment TEXT,
    answer_text TEXT,
    question_text TEXT,
    sources_json TEXT,
    debug_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);
CREATE INDEX IF NOT EXISTS idx_answer_feedback_session_id ON answer_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_answer_feedback_created_at ON answer_feedback(created_at);
"""


def ensure_data_directory() -> Path:
    """Create app data directory if it does not exist."""
    settings = get_settings()
    path = Path(settings.app_data_directory).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_db_initialized() -> str:
    """
    Ensure APP_DATA_DIRECTORY exists, DB file path is valid, and tables are created.
    Returns the resolved SQLite DB path. Safe to call at startup.
    """
    settings = get_settings()
    ensure_data_directory()
    db_path = Path(settings.sqlite_db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()

    logger.info("SQLite DB initialized at %s", db_path)
    return str(db_path)


def get_db_connection() -> sqlite3.Connection:
    """Return a connection to the configured SQLite DB. Caller must close it."""
    ensure_db_initialized()
    settings = get_settings()
    return sqlite3.connect(str(Path(settings.sqlite_db_path).resolve()))


def get_db_path() -> str:
    """Return resolved DB path after ensuring initialization."""
    return ensure_db_initialized()
