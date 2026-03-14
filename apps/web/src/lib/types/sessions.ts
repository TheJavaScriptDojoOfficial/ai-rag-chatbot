/**
 * Frontend types for chat sessions and messages (aligned with backend).
 */

export interface SessionSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessageRecord {
  id: string;
  session_id: string;
  role: string;
  content: string;
  sources?: unknown[];
  debug?: Record<string, unknown> | null;
  error?: string | null;
  created_at: string;
  sequence_number: number;
}

export interface SessionDetailResponse {
  session: SessionSummary;
  messages: ChatMessageRecord[];
}
