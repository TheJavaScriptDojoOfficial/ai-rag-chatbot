"""
Feedback business logic: validate and store; optional dedup.
"""
import json
from typing import Optional

from app.schemas.feedback import FeedbackSubmitRequest
from app.services.feedback.feedback_repository import (
    has_feedback_for_message,
    insert_feedback,
)


def submit_feedback(payload: FeedbackSubmitRequest, *, allow_duplicate: bool = True) -> Optional[str]:
    """
    Store feedback. If allow_duplicate is False, skip if message_id already has feedback.
    Returns feedback_id or None if skipped (e.g. duplicate).
    """
    if not allow_duplicate and has_feedback_for_message(payload.message_id):
        return None

    sources_json = None
    if payload.sources is not None:
        try:
            sources_json = json.dumps(payload.sources)
        except (TypeError, ValueError):
            pass

    debug_json = None
    if payload.debug is not None:
        try:
            debug_json = json.dumps(payload.debug)
        except (TypeError, ValueError):
            pass

    fid = insert_feedback(
        session_id=payload.session_id,
        message_id=payload.message_id,
        feedback_type=payload.feedback_type,
        comment=payload.comment,
        answer_text=payload.answer_text,
        question_text=payload.question_text,
        sources_json=sources_json,
        debug_json=debug_json,
    )
    return fid
