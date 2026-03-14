"use client";

import { useState } from "react";
import { StatusBar } from "./status-bar";
import { DebugPanel } from "./debug-panel";
import { IndexingPanel } from "./indexing-panel";
import type {
  AppHealthSummary,
  RAGHealthResponse,
  VectorHealthResponse,
} from "@/lib/types/health";
import type { IngestHealthResponse } from "@/lib/api/ingest";
import { cn } from "@/lib/utils/cn";

type TabId = "status" | "debug" | "indexing";

interface UtilityPanelProps {
  summary: AppHealthSummary;
  onRefresh: () => void;
  refreshing: boolean;
  debugMode: boolean;
  onDebugModeChange: (v: boolean) => void;
  lastDebug: React.ComponentProps<typeof DebugPanel>["debug"];
  ragHealth: RAGHealthResponse | null;
  vectorHealth: VectorHealthResponse | null;
  ingestHealth: IngestHealthResponse | null;
}

export function UtilityPanel({
  summary,
  onRefresh,
  refreshing,
  debugMode,
  onDebugModeChange,
  lastDebug,
  ragHealth,
  vectorHealth,
  ingestHealth,
}: UtilityPanelProps) {
  const [tab, setTab] = useState<TabId>("status");

  const tabs: { id: TabId; label: string }[] = [
    { id: "status", label: "Status" },
    { id: "debug", label: "Debug" },
    { id: "indexing", label: "Indexing" },
  ];

  return (
    <div className="flex h-full flex-col">
      <div className="flex border-b border-slate-200">
        {tabs.map(({ id, label }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={cn(
              "px-3 py-2 text-sm font-medium border-b-2 -mb-px",
              tab === id
                ? "border-slate-700 text-slate-800"
                : "border-transparent text-slate-500 hover:text-slate-700"
            )}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="flex-1 min-h-0 overflow-y-auto py-4 space-y-4">
        {tab === "status" && (
          <>
            <StatusBar
              summary={summary}
              onRefresh={onRefresh}
              refreshing={refreshing}
            />
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={debugMode}
                onChange={(e) => onDebugModeChange(e.target.checked)}
                className="rounded border-slate-300 text-slate-700 focus:ring-slate-400"
              />
              <span className="text-sm text-slate-700">Debug mode</span>
            </label>
            {(ragHealth || vectorHealth || ingestHealth) && (
              <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-3 text-sm">
                <p className="font-medium text-slate-700">Readiness details</p>
                <dl className="mt-2 space-y-1 text-xs text-slate-600">
                  {ragHealth && (
                    <>
                      <dt className="font-medium text-slate-500">RAG</dt>
                      <dd>
                        Model: {ragHealth.model ?? "—"} · Embed:{" "}
                        {ragHealth.embed_model ?? "—"} · Collection:{" "}
                        {ragHealth.collection_name ?? "—"}
                      </dd>
                    </>
                  )}
                  {vectorHealth && (
                    <>
                      <dt className="font-medium text-slate-500">Vector</dt>
                      <dd>
                        Collection: {vectorHealth.collection_name ?? "—"} · Embed:{" "}
                        {vectorHealth.embed_model ?? "—"}
                        {vectorHealth.persist_directory && (
                          <> · Path: {vectorHealth.persist_directory}</>
                        )}
                      </dd>
                    </>
                  )}
                  {ingestHealth && (
                    <>
                      <dt className="font-medium text-slate-500">Docs path</dt>
                      <dd>
                        {ingestHealth.resolved_path ?? ingestHealth.docs_base_path ?? "—"}{" "}
                        {ingestHealth.path_exists ? "✓" : "(missing)"}
                      </dd>
                    </>
                  )}
                </dl>
              </div>
            )}
          </>
        )}
        {tab === "debug" && (
          <DebugPanel debug={lastDebug ?? undefined} />
        )}
        {tab === "indexing" && (
          <IndexingPanel onRefreshStatus={onRefresh} />
        )}
      </div>
    </div>
  );
}
