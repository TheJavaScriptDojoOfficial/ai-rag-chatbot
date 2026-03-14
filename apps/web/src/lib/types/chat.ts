/**
 * Local chat message model (in-memory only).
 */

import type { RAGDebugInfo, RAGSource } from "./rag";

export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources?: RAGSource[];
  debug?: RAGDebugInfo | null;
  createdAt: number;
  error?: string;
  /** Backend message id when persisted (for feedback). */
  messageId?: string | null;
}
