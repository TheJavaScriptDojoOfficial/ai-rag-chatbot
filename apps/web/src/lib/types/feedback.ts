/**
 * Frontend types for answer feedback (aligned with backend).
 */

export type FeedbackType = "up" | "down";

export interface FeedbackSubmitRequest {
  session_id: string;
  message_id: string;
  feedback_type: FeedbackType;
  comment?: string;
  question_text?: string;
  answer_text?: string;
  sources?: unknown[];
  debug?: Record<string, unknown>;
}

export interface FeedbackSubmitResponse {
  status: string;
  feedback_id: string;
}
