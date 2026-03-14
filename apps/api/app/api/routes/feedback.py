"""
Feedback API: submit answer feedback (thumbs up/down). Optional GET for dev inspection.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.feedback import FeedbackSubmitRequest, FeedbackSubmitResponse
from app.services.feedback.feedback_service import submit_feedback
from app.services.feedback.feedback_repository import list_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackSubmitResponse)
def submit_feedback_route(body: FeedbackSubmitRequest):
    """Store answer feedback (up/down, optional comment and context)."""
    feedback_id = submit_feedback(body, allow_duplicate=True)
    if feedback_id is None:
        raise HTTPException(status_code=400, detail="Feedback not stored")
    return FeedbackSubmitResponse(status="ok", feedback_id=feedback_id)


@router.get("")
def list_feedback_route(limit: int = 100):
    """List recent feedback (local dev inspection only). Max limit 500."""
    if limit > 500:
        limit = 500
    items = list_feedback(limit=limit)
    return {"feedback": items, "count": len(items)}
