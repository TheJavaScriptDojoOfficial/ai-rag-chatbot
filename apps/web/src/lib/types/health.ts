/**
 * Frontend types for backend health endpoints.
 */

export interface AppHealthResponse {
  status: string;
  service?: string;
  message?: string;
  ai_configured?: boolean;
  ollama_base_url?: string;
  ollama_model?: string;
  vector_configured?: boolean;
  vector_provider?: string;
  rag_configured?: boolean;
}

export interface RAGHealthResponse {
  status: string;
  rag_top_k?: number;
  rag_min_score?: number;
  rag_max_context_chars?: number;
  model?: string;
  embed_model?: string;
  collection_name?: string;
}

export interface AIHealthResponse {
  status: string;
  ollama_reachable: boolean;
  base_url: string;
  model: string;
}

export interface VectorHealthResponse {
  status: string;
  provider?: string;
  collection_name?: string;
  persist_directory?: string;
  embed_model?: string;
  error?: string;
}

export interface AppHealthSummary {
  api: "healthy" | "unreachable" | "error";
  rag: "ready" | "degraded" | "unreachable" | "error";
  ai: "healthy" | "degraded" | "unreachable" | "error";
  vector: "healthy" | "degraded" | "unreachable" | "error";
  lastChecked: number | null;
}
