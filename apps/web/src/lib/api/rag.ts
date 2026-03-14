/**
 * RAG API: chat and preview.
 */

import { apiRequest } from "./client";
import type { RAGChatRequest, RAGChatResponse } from "@/lib/types/rag";

export async function postRAGChat(
  body: RAGChatRequest
): Promise<RAGChatResponse> {
  return apiRequest<RAGChatResponse>("/rag/chat", {
    method: "POST",
    body: JSON.stringify({
      message: body.message,
      top_k: body.top_k ?? undefined,
      min_score: body.min_score ?? undefined,
      include_sources: body.include_sources ?? true,
      include_debug: body.include_debug ?? false,
    }),
  });
}

export async function postRAGChatPreview(
  message: string,
  options?: { top_k?: number; min_score?: number }
): Promise<{
  query: string;
  top_k_used: number;
  min_score_used: number;
  retrieved_count: number;
  selected_count: number;
  context_char_count: number;
  sources: unknown[];
  prompt_name: string;
}> {
  return apiRequest("/rag/chat/preview", {
    method: "POST",
    body: JSON.stringify({
      message,
      top_k: options?.top_k,
      min_score: options?.min_score,
    }),
  });
}
