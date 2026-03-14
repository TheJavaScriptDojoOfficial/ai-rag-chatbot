"""
Session business logic: create, title generation, append messages, fetch for context.
"""
import re
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.services.sessions.session_repository import (
    create_session as repo_create_session,
    delete_session as repo_delete_session,
    get_recent_messages_for_context,
    get_session,
    insert_message,
    list_messages_by_session,
    list_sessions,
    get_next_sequence_number,
    update_session_title as repo_update_session_title,
    update_session_updated_at_and_count,
)


DEFAULT_TITLE = "New chat"


def _sanitize_title(raw: str, max_chars: int) -> str:
    """Trim and clean title; enforce max length."""
    s = re.sub(r"\s+", " ", raw).strip()
    if len(s) > max_chars:
        s = s[: max_chars - 3].rstrip() + "..."
    return s or DEFAULT_TITLE


def create_new_session(title: Optional[str] = None) -> Dict[str, Any]:
    """Create a new session. If title provided, sanitize it; else use default."""
    settings = get_settings()
    if title is not None and title.strip():
        final_title = _sanitize_title(title, settings.session_title_max_chars)
    else:
        final_title = DEFAULT_TITLE
    return repo_create_session(final_title)


def generate_title_from_first_question(question: str) -> str:
    """Derive a short title from the first user message."""
    settings = get_settings()
    return _sanitize_title(question, settings.session_title_max_chars)


def update_session_title_from_first_message(session_id: str, first_user_content: str) -> bool:
    """Set session title from first user message (e.g. after first turn)."""
    title = generate_title_from_first_question(first_user_content)
    return repo_update_session_title(session_id, title)


def list_sessions_ordered() -> List[Dict[str, Any]]:
    """List all sessions by updated_at desc."""
    return list_sessions()


def get_session_with_messages(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session summary and all messages in sequence order."""
    session = get_session(session_id)
    if not session:
        return None
    messages = list_messages_by_session(session_id)
    return {"session": session, "messages": messages}


def append_user_message(session_id: str, content: str) -> Optional[Dict[str, Any]]:
    """Append a user message; return the created message record or None if session missing."""
    if not get_session(session_id):
        return None
    seq = get_next_sequence_number(session_id)
    return insert_message(session_id, "user", content, sequence_number=seq)


def append_assistant_message(
    session_id: str,
    content: str,
    *,
    sources_json: Optional[str] = None,
    debug_json: Optional[str] = None,
    error: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Append an assistant message; return the created message record or None if session missing."""
    if not get_session(session_id):
        return None
    seq = get_next_sequence_number(session_id)
    return insert_message(
        session_id,
        "assistant",
        content,
        sources_json=sources_json,
        debug_json=debug_json,
        error=error,
        sequence_number=seq,
    )


def get_recent_conversation_turns(session_id: str) -> List[Dict[str, Any]]:
    """Get recent user/assistant turns for RAG prompt context (limited by config)."""
    settings = get_settings()
    limit = settings.max_session_messages_for_context
    return get_recent_messages_for_context(session_id, limit)


def rename_session(session_id: str, title: str) -> bool:
    """Rename session; title is sanitized."""
    settings = get_settings()
    final = _sanitize_title(title, settings.session_title_max_chars)
    return repo_update_session_title(session_id, final)


def remove_session(session_id: str) -> bool:
    """Delete session and related messages."""
    return repo_delete_session(session_id)
