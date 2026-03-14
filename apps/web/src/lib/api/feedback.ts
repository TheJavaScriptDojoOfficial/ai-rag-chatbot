/**
 * Feedback API: submit answer feedback (thumbs up/down).
 */

import { apiRequest } from "./client";
import type { FeedbackSubmitRequest, FeedbackSubmitResponse } from "@/lib/types/feedback";

export async function submitFeedback(
  payload: FeedbackSubmitRequest
): Promise<FeedbackSubmitResponse> {
  return apiRequest<FeedbackSubmitResponse>("/feedback", {
    method: "POST",
    body: JSON.stringify({
      session_id: payload.session_id,
      message_id: payload.message_id,
      feedback_type: payload.feedback_type,
      comment: payload.comment ?? undefined,
      question_text: payload.question_text ?? undefined,
      answer_text: payload.answer_text ?? undefined,
      sources: payload.sources ?? undefined,
      debug: payload.debug ?? undefined,
    }),
  });
}
