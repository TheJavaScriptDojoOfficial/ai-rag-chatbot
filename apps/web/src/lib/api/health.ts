/**
 * Health API: backend, RAG, AI, vector status.
 */

import { apiRequest } from "./client";
import type {
  AppHealthResponse,
  RAGHealthResponse,
  AIHealthResponse,
  VectorHealthResponse,
} from "@/lib/types/health";

export async function getHealth(): Promise<AppHealthResponse> {
  return apiRequest<AppHealthResponse>("/health", { method: "GET" });
}

export async function getRAGHealth(): Promise<RAGHealthResponse> {
  return apiRequest<RAGHealthResponse>("/rag/health", { method: "GET" });
}

export async function getAIHealth(): Promise<AIHealthResponse> {
  return apiRequest<AIHealthResponse>("/ai/health", { method: "GET" });
}

export async function getVectorHealth(): Promise<VectorHealthResponse> {
  return apiRequest<VectorHealthResponse>("/vector/health", { method: "GET" });
}
