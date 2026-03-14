"""
SQLite repository for chat_sessions and chat_messages. No business logic.
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.db import get_db_connection


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_session(title: str = "New chat") -> Dict[str, Any]:
    sid = str(uuid.uuid4())
    now = _now_iso()
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO chat_sessions (id, title, created_at, updated_at, message_count) VALUES (?, ?, ?, ?, 0)",
            (sid, title, now, now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, created_at, updated_at, message_count FROM chat_sessions WHERE id = ?",
            (sid,),
        ).fetchone()
        return {
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "message_count": row[4],
        }
    finally:
        conn.close()


def list_sessions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at, message_count FROM chat_sessions ORDER BY updated_at DESC"
        ).fetchall()
        return [
            {
                "id": r[0],
                "title": r[1],
                "created_at": r[2],
                "updated_at": r[3],
                "message_count": r[4],
            }
            for r in rows
        ]
    finally:
        conn.close()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT id, title, created_at, updated_at, message_count FROM chat_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "message_count": row[4],
        }
    finally:
        conn.close()


def update_session_title(session_id: str, title: str) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
            (title, _now_iso(), session_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def update_session_updated_at_and_count(session_id: str, message_count: int) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "UPDATE chat_sessions SET updated_at = ?, message_count = ? WHERE id = ?",
            (_now_iso(), message_count, session_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_session(session_id: str) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def insert_message(
    session_id: str,
    role: str,
    content: str,
    *,
    sources_json: Optional[str] = None,
    debug_json: Optional[str] = None,
    error: Optional[str] = None,
    sequence_number: int = 0,
) -> Dict[str, Any]:
    mid = str(uuid.uuid4())
    now = _now_iso()
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO chat_messages
               (id, session_id, role, content, sources_json, debug_json, error, created_at, sequence_number)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (mid, session_id, role, content, sources_json, debug_json, error, now, sequence_number),
        )
        count_row = conn.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (session_id,)
        ).fetchone()
        new_count = count_row[0] if count_row else 0
        conn.execute(
            "UPDATE chat_sessions SET updated_at = ?, message_count = ? WHERE id = ?",
            (now, new_count, session_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, session_id, role, content, sources_json, debug_json, error, created_at, sequence_number FROM chat_messages WHERE id = ?",
            (mid,),
        ).fetchone()
        sources = []
        if row[4]:
            try:
                sources = json.loads(row[4])
            except (json.JSONDecodeError, TypeError):
                pass
        debug = None
        if row[5]:
            try:
                debug = json.loads(row[5])
            except (json.JSONDecodeError, TypeError):
                pass
        return {
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "sources": sources,
            "debug": debug,
            "error": row[6],
            "created_at": row[7],
            "sequence_number": row[8],
        }
    finally:
        conn.close()


def list_messages_by_session(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, session_id, role, content, sources_json, debug_json, error, created_at, sequence_number
               FROM chat_messages WHERE session_id = ? ORDER BY sequence_number ASC""",
            (session_id,),
        ).fetchall()
        out = []
        for r in rows:
            sources = []
            if r[4]:
                try:
                    sources = json.loads(r[4])
                except (json.JSONDecodeError, TypeError):
                    pass
            debug = None
            if r[5]:
                try:
                    debug = json.loads(r[5])
                except (json.JSONDecodeError, TypeError):
                    pass
            out.append({
                "id": r[0],
                "session_id": r[1],
                "role": r[2],
                "content": r[3],
                "sources": sources,
                "debug": debug,
                "error": r[6],
                "created_at": r[7],
                "sequence_number": r[8],
            })
        return out
    finally:
        conn.close()


def get_recent_messages_for_context(session_id: str, limit: int) -> List[Dict[str, Any]]:
    """Return the most recent messages (by sequence) for prompt context, in chronological order."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, session_id, role, content, sources_json, debug_json, error, created_at, sequence_number
               FROM chat_messages WHERE session_id = ? AND role IN ('user', 'assistant')
               ORDER BY sequence_number DESC LIMIT ?""",
            (session_id, limit),
        ).fetchall()
        out = []
        for r in reversed(rows):
            sources = []
            if r[4]:
                try:
                    sources = json.loads(r[4])
                except (json.JSONDecodeError, TypeError):
                    pass
            debug = None
            if r[5]:
                try:
                    debug = json.loads(r[5])
                except (json.JSONDecodeError, TypeError):
                    pass
            out.append({
                "id": r[0],
                "session_id": r[1],
                "role": r[2],
                "content": r[3],
                "sources": sources,
                "debug": debug,
                "error": r[6],
                "created_at": r[7],
                "sequence_number": r[8],
            })
        return out
    finally:
        conn.close()


def get_next_sequence_number(session_id: str) -> int:
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(MAX(sequence_number), -1) + 1 FROM chat_messages WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row[0] if row is not None else 0
    finally:
        conn.close()


def delete_all_sessions() -> int:
    """Delete all sessions (and messages via CASCADE). For local dev reset only."""
    conn = get_db_connection()
    try:
        cur = conn.execute("DELETE FROM chat_sessions")
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
