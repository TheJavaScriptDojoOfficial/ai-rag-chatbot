"use client";

import { useState, useCallback } from "react";
import {
  postVectorIndex,
  deleteVectorIndex,
  type IndexResponse,
} from "@/lib/api/vector";
import {
  postIngestPreview,
  type IngestPreviewResponse,
} from "@/lib/api/ingest";

interface IndexingPanelProps {
  onRefreshStatus: () => void;
}

export function IndexingPanel({ onRefreshStatus }: IndexingPanelProps) {
  const [resetBeforeIndex, setResetBeforeIndex] = useState(false);
  const [includeChunks, setIncludeChunks] = useState(false);
  const [indexLoading, setIndexLoading] = useState(false);
  const [clearLoading, setClearLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [indexResult, setIndexResult] = useState<IndexResponse | null>(null);
  const [previewResult, setPreviewResult] = useState<IngestPreviewResponse | null>(null);
  const [clearSuccess, setClearSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runIndexing = useCallback(async () => {
    setIndexLoading(true);
    setError(null);
    setIndexResult(null);
    try {
      const res = await postVectorIndex({
        recursive: true,
        reset_collection: resetBeforeIndex,
        include_chunks: includeChunks,
      });
      setIndexResult(res);
      onRefreshStatus();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Indexing failed");
    } finally {
      setIndexLoading(false);
    }
  }, [resetBeforeIndex, includeChunks, onRefreshStatus]);

  const clearIndex = useCallback(async () => {
    if (!confirm("Clear the entire vector index? This cannot be undone.")) return;
    setClearLoading(true);
    setError(null);
    setClearSuccess(null);
    try {
      const res = await deleteVectorIndex();
      setClearSuccess(res.message ?? "Index cleared");
      setIndexResult(null);
      onRefreshStatus();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Clear failed");
    } finally {
      setClearLoading(false);
    }
  }, [onRefreshStatus]);

  const runPreview = useCallback(async () => {
    setPreviewLoading(true);
    setError(null);
    setPreviewResult(null);
    try {
      const res = await postIngestPreview({
        recursive: true,
        include_chunks: includeChunks,
      });
      setPreviewResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Preview failed");
    } finally {
      setPreviewLoading(false);
    }
  }, [includeChunks]);

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-slate-700">Indexing</h3>
      <p className="text-xs text-slate-500">
        Run indexing from the configured docs path. Clear index removes all vectors.
      </p>

      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={resetBeforeIndex}
          onChange={(e) => setResetBeforeIndex(e.target.checked)}
          className="rounded border-slate-300 text-slate-700 focus:ring-slate-400"
        />
        <span className="text-sm text-slate-700">Reset collection before indexing</span>
      </label>
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={includeChunks}
          onChange={(e) => setIncludeChunks(e.target.checked)}
          className="rounded border-slate-300 text-slate-700 focus:ring-slate-400"
        />
        <span className="text-sm text-slate-700">Include chunk details</span>
      </label>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={runIndexing}
          disabled={indexLoading}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          {indexLoading ? "Indexing…" : "Run Indexing"}
        </button>
        <button
          type="button"
          onClick={clearIndex}
          disabled={clearLoading}
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100 disabled:opacity-50"
        >
          {clearLoading ? "Clearing…" : "Clear Index"}
        </button>
        <button
          type="button"
          onClick={onRefreshStatus}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Refresh status
        </button>
        <button
          type="button"
          onClick={runPreview}
          disabled={previewLoading}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
        >
          {previewLoading ? "Loading…" : "Preview Docs"}
        </button>
      </div>

      {error && (
        <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {clearSuccess && (
        <div className="rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          {clearSuccess}
        </div>
      )}

      {indexResult && (
        <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3 text-sm">
          <p className="font-medium text-slate-700">Last indexing result</p>
          <dl className="mt-2 grid grid-cols-2 gap-x-2 gap-y-1 text-xs text-slate-600">
            <dt>Status</dt>
            <dd>{indexResult.status}</dd>
            <dt>Collection</dt>
            <dd className="truncate" title={indexResult.collection_name}>
              {indexResult.collection_name}
            </dd>
            <dt>Total files</dt>
            <dd>{indexResult.total_files}</dd>
            <dt>Processed</dt>
            <dd>{indexResult.processed_files}</dd>
            <dt>Skipped</dt>
            <dd>{indexResult.skipped_files}</dd>
            <dt>Indexed chunks</dt>
            <dd>{indexResult.indexed_chunks}</dd>
            <dt>Documents</dt>
            <dd>{indexResult.documents?.length ?? 0}</dd>
          </dl>
          {indexResult.errors.length > 0 && (
            <p className="mt-2 text-xs text-red-600">
              Errors: {indexResult.errors.join("; ")}
            </p>
          )}
        </div>
      )}

      {previewResult && (
        <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3 text-sm">
          <p className="font-medium text-slate-700">Preview</p>
          <p className="mt-1 text-xs text-slate-600">
            Files: {previewResult.processed_files} processed, {previewResult.skipped_files} skipped.
            Documents: {previewResult.documents?.length ?? 0}.
          </p>
          {previewResult.documents?.length > 0 && (
            <ul className="mt-2 max-h-24 overflow-y-auto text-xs text-slate-600">
              {previewResult.documents.slice(0, 10).map((d) => (
                <li key={d.source_id} className="truncate">
                  {d.file_name} ({d.chunk_count} chunks)
                </li>
              ))}
              {previewResult.documents.length > 10 && (
                <li>… and {previewResult.documents.length - 10} more</li>
              )}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
