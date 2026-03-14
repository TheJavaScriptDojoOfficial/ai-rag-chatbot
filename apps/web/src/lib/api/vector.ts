/**
 * Vector API: health, index, clear index, search.
 */

import { apiRequest } from "./client";

export interface VectorHealthResponse {
  status: string;
  provider?: string;
  collection_name?: string;
  persist_directory?: string;
  embed_model?: string;
  error?: string;
}

export interface IndexRequestOptions {
  path?: string | null;
  recursive?: boolean;
  reset_collection?: boolean;
  include_chunks?: boolean;
}

export interface IndexDocumentResult {
  source_id: string;
  file_name: string;
  chunk_count: number;
  indexed_chunk_count: number;
  metadata: Record<string, unknown>;
}

export interface IndexResponse {
  status: string;
  collection_name: string;
  total_files: number;
  processed_files: number;
  skipped_files: number;
  indexed_chunks: number;
  documents: IndexDocumentResult[];
  errors: string[];
}

export interface ClearIndexResponse {
  status: string;
  message: string;
  collection_name: string;
}

export async function getVectorHealth(): Promise<VectorHealthResponse> {
  return apiRequest<VectorHealthResponse>("/vector/health", { method: "GET" });
}

export async function postVectorIndex(
  options: IndexRequestOptions = {}
): Promise<IndexResponse> {
  return apiRequest<IndexResponse>("/vector/index", {
    method: "POST",
    body: JSON.stringify({
      path: options.path ?? undefined,
      recursive: options.recursive ?? true,
      reset_collection: options.reset_collection ?? false,
      include_chunks: options.include_chunks ?? false,
    }),
  });
}

export async function deleteVectorIndex(): Promise<ClearIndexResponse> {
  return apiRequest<ClearIndexResponse>("/vector/index", {
    method: "DELETE",
  });
}
