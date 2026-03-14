/**
 * Frontend types aligned with backend RAG schemas.
 */

export interface RAGSource {
  chunk_id: string;
  source_id: string;
  file_name: string;
  file_path: string;
  chunk_index: number;
  score: number;
  text: string;
  metadata: Record<string, unknown>;
}

export interface RAGDebugInfo {
  top_k_used: number;
  min_score_used: number;
  context_char_count: number;
  retrieved_count: number;
  selected_count: number;
  model: string;
  prompt_name: string;
}

export interface RAGChatRequest {
  message: string;
  top_k?: number;
  min_score?: number;
  include_sources?: boolean;
  include_debug?: boolean;
}

export interface RAGChatResponse {
  mode: string;
  model: string;
  answer: string;
  sources: RAGSource[];
  debug?: RAGDebugInfo | null;
}
