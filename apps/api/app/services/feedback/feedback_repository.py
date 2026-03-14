"""
SQLite repository for answer_feedback. No business logic.
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.db import get_db_connection


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_feedback(
    session_id: str,
    message_id: str,
    feedback_type: str,
    *,
    comment: Optional[str] = None,
    answer_text: Optional[str] = None,
    question_text: Optional[str] = None,
    sources_json: Optional[str] = None,
    debug_json: Optional[str] = None,
) -> str:
    """Insert a feedback row; returns the new id."""
    fid = str(uuid.uuid4())
    now = _now_iso()
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO answer_feedback
               (id, session_id, message_id, feedback_type, comment, answer_text, question_text, sources_json, debug_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (fid, session_id, message_id, feedback_type, comment, answer_text, question_text, sources_json, debug_json, now),
        )
        conn.commit()
        return fid
    finally:
        conn.close()


def has_feedback_for_message(message_id: str) -> bool:
    """Return True if any feedback already exists for this message (for simple dedup)."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM answer_feedback WHERE message_id = ? LIMIT 1",
            (message_id,),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def list_feedback(limit: int = 100) -> List[Dict[str, Any]]:
    """List recent feedback for local dev inspection. Ordered by created_at desc."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, session_id, message_id, feedback_type, comment, answer_text, question_text, sources_json, debug_json, created_at
               FROM answer_feedback ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        out = []
        for r in rows:
            sources = None
            if r[7]:
                try:
                    sources = json.loads(r[7])
                except (json.JSONDecodeError, TypeError):
                    pass
            debug = None
            if r[8]:
                try:
                    debug = json.loads(r[8])
                except (json.JSONDecodeError, TypeError):
                    pass
            out.append({
                "id": r[0],
                "session_id": r[1],
                "message_id": r[2],
                "feedback_type": r[3],
                "comment": r[4],
                "answer_text": r[5],
                "question_text": r[6],
                "sources": sources,
                "debug": debug,
                "created_at": r[9],
            })
        return out
    finally:
        conn.close()
