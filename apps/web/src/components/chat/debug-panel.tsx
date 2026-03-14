"use client";

import type { RAGDebugInfo } from "@/lib/types/rag";

interface DebugPanelProps {
  debug: RAGDebugInfo | null | undefined;
  onRetryPreview?: () => void;
  previewLoading?: boolean;
}

export function DebugPanel({
  debug,
  onRetryPreview,
  previewLoading = false,
}: DebugPanelProps) {
  if (!debug) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4 text-sm text-slate-500">
        <p className="font-medium text-slate-600">Debug</p>
        <p className="mt-1">Enable &quot;Debug mode&quot; and send a message to see retrieval details.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-4 text-sm">
      <p className="font-medium text-slate-700">Last run</p>
      <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-xs text-slate-600">
        <dt>top_k_used</dt>
        <dd>{debug.top_k_used}</dd>
        <dt>min_score_used</dt>
        <dd>{debug.min_score_used}</dd>
        <dt>context_char_count</dt>
        <dd>{debug.context_char_count}</dd>
        <dt>retrieved_count</dt>
        <dd>{debug.retrieved_count}</dd>
        <dt>selected_count</dt>
        <dd>{debug.selected_count}</dd>
        <dt>model</dt>
        <dd className="truncate" title={debug.model}>
          {debug.model}
        </dd>
        <dt>prompt_name</dt>
        <dd className="truncate" title={debug.prompt_name}>
          {debug.prompt_name}
        </dd>
      </dl>
      {onRetryPreview && (
        <button
          type="button"
          onClick={onRetryPreview}
          disabled={previewLoading}
          className="mt-3 text-xs font-medium text-slate-600 hover:text-slate-800 underline disabled:opacity-50"
        >
          {previewLoading ? "Loading…" : "Refresh preview"}
        </button>
      )}
    </div>
  );
}
