/**
 * Ingest API: health, preview (no persistence).
 */

import { apiRequest } from "./client";

export interface IngestHealthResponse {
  status: string;
  docs_base_path?: string;
  path_exists?: boolean;
  resolved_path?: string;
  allowed_extensions?: string[];
}

export interface IngestPreviewOptions {
  path?: string | null;
  recursive?: boolean;
  include_chunks?: boolean;
}

export interface IngestPreviewResponse {
  status: string;
  total_files: number;
  processed_files: number;
  skipped_files: number;
  documents: Array<{
    source_id: string;
    file_name: string;
    file_path: string;
    extension: string;
    char_count: number;
    chunk_count: number;
    metadata: Record<string, unknown>;
    chunks?: unknown[];
  }>;
  errors: string[];
}

export async function getIngestHealth(): Promise<IngestHealthResponse> {
  return apiRequest<IngestHealthResponse>("/ingest/health", { method: "GET" });
}

export async function postIngestPreview(
  options: IngestPreviewOptions = {}
): Promise<IngestPreviewResponse> {
  return apiRequest<IngestPreviewResponse>("/ingest/preview", {
    method: "POST",
    body: JSON.stringify({
      path: options.path ?? undefined,
      recursive: options.recursive ?? true,
      include_chunks: options.include_chunks ?? true,
    }),
  });
}
