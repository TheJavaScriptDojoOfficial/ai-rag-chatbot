"use client";

import { useState } from "react";
import { cn } from "@/lib/utils/cn";
import { formatScore } from "@/lib/utils/format";
import type { RAGSource } from "@/lib/types/rag";

interface SourceCardProps {
  source: RAGSource;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const [showMeta, setShowMeta] = useState(false);
  const hasMeta = source.metadata && Object.keys(source.metadata).length > 0;

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2 text-slate-600">
        <span className="font-medium text-slate-800 truncate max-w-[180px]" title={source.file_name}>
          {source.file_name}
        </span>
        <span className="text-xs">chunk {source.chunk_index}</span>
        <span className="text-xs">score {formatScore(source.score)}</span>
        {hasMeta && (
          <button
            type="button"
            onClick={() => setShowMeta(!showMeta)}
            className="text-xs text-slate-500 hover:text-slate-700 underline"
          >
            {showMeta ? "Hide metadata" : "Metadata"}
          </button>
        )}
      </div>
      <pre
        className={cn(
          "mt-2 whitespace-pre-wrap break-words font-sans text-slate-700 text-xs overflow-x-auto",
          "border-t border-slate-200 pt-2"
        )}
      >
        {source.text}
      </pre>
      {showMeta && hasMeta && (
        <pre className="mt-2 text-xs text-slate-500 overflow-x-auto">
          {JSON.stringify(source.metadata, null, 2)}
        </pre>
      )}
    </div>
  );
}
