"use client";

import { useState } from "react";
import { SourceCard } from "./source-card";
import type { RAGSource } from "@/lib/types/rag";
import { cn } from "@/lib/utils/cn";

const COLLAPSED_COUNT = 3;

interface SourceListProps {
  sources: RAGSource[];
}

export function SourceList({ sources }: SourceListProps) {
  const [expanded, setExpanded] = useState(false);
  const showCollapse = sources.length > COLLAPSED_COUNT;
  const visible = showCollapse && !expanded ? sources.slice(0, COLLAPSED_COUNT) : sources;

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
        Sources ({sources.length})
      </p>
      <div className="space-y-2">
        {visible.map((source, i) => (
          <SourceCard key={source.chunk_id ?? i} source={source} index={i} />
        ))}
      </div>
      {showCollapse && (
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className={cn(
            "text-xs font-medium text-slate-500 hover:text-slate-700",
            "underline"
          )}
        >
          {expanded ? `Show less` : `Show ${sources.length - COLLAPSED_COUNT} more`}
        </button>
      )}
    </div>
  );
}
