"""
Session API: list, create, get, rename, delete. Optional DELETE all for dev reset.
"""
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from app.schemas.sessions import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionDetailResponse,
    SessionListResponse,
    SessionSummary,
    ChatMessageRecord,
    RenameSessionRequest,
)
from app.services.sessions.session_service import (
    create_new_session,
    get_session_with_messages,
    list_sessions_ordered,
    rename_session,
    remove_session,
)
from app.services.sessions.session_repository import delete_all_sessions, get_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _to_summary(s: dict) -> SessionSummary:
    return SessionSummary(
        id=s["id"],
        title=s["title"],
        created_at=s["created_at"],
        updated_at=s["updated_at"],
        message_count=s.get("message_count", 0),
    )


def _to_message_record(m: dict) -> ChatMessageRecord:
    return ChatMessageRecord(
        id=m["id"],
        session_id=m["session_id"],
        role=m["role"],
        content=m.get("content", ""),
        sources=m.get("sources", []),
        debug=m.get("debug"),
        error=m.get("error"),
        created_at=m["created_at"],
        sequence_number=m.get("sequence_number", 0),
    )


@router.get("", response_model=SessionListResponse)
def list_sessions_route():
    """List chat sessions ordered by updated_at desc."""
    sessions = list_sessions_ordered()
    return SessionListResponse(sessions=[_to_summary(s) for s in sessions])


@router.post("", response_model=CreateSessionResponse)
def create_session_route(body: Optional[CreateSessionRequest] = Body(default=None)):
    """Create a new session. Optional title override."""
    title = body.title if body and body.title else None
    session = create_new_session(title=title)
    return CreateSessionResponse(session=_to_summary(session))


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session_route(session_id: str):
    """Return session summary and all messages ordered by sequence."""
    data = get_session_with_messages(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetailResponse(
        session=_to_summary(data["session"]),
        messages=[_to_message_record(m) for m in data["messages"]],
    )


@router.patch("/{session_id}")
def rename_session_route(session_id: str, body: RenameSessionRequest):
    """Rename session."""
    if not get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    ok = rename_session(session_id, body.title)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update session")
    return {"status": "ok", "session_id": session_id}


@router.delete("/{session_id}")
def delete_session_route(session_id: str):
    """Delete session and related messages."""
    if not get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    remove_session(session_id)
    return {"status": "ok", "session_id": session_id}


@router.delete("", status_code=200)
def delete_all_sessions_route():
    """Delete all sessions (local dev reset only). Use with care."""
    count = delete_all_sessions()
    return {"status": "ok", "deleted_count": count}
