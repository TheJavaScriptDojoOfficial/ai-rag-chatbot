"use client";

import type { AppHealthSummary } from "@/lib/types/health";
import { cn } from "@/lib/utils/cn";

interface StatusBarProps {
  summary: AppHealthSummary;
  onRefresh: () => void;
  refreshing?: boolean;
}

const statusLabel = (
  s: "healthy" | "ready" | "degraded" | "unreachable" | "error"
): string => {
  switch (s) {
    case "healthy":
    case "ready":
      return "OK";
    case "degraded":
      return "Degraded";
    case "unreachable":
      return "Unreachable";
    case "error":
      return "Error";
    default:
      return String(s);
  }
};

const statusColor = (
  s: "healthy" | "ready" | "degraded" | "unreachable" | "error"
): string => {
  switch (s) {
    case "healthy":
    case "ready":
      return "bg-emerald-100 text-emerald-800 border-emerald-200";
    case "degraded":
      return "bg-amber-100 text-amber-800 border-amber-200";
    case "unreachable":
    case "error":
      return "bg-red-100 text-red-800 border-red-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
};

export function StatusBar({
  summary,
  onRefresh,
  refreshing = false,
}: StatusBarProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-700">Backend status</h3>
        <button
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          className="text-xs font-medium text-slate-600 hover:text-slate-800 underline disabled:opacity-50"
        >
          {refreshing ? "Checking…" : "Refresh"}
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        <StatusBadge label="API" status={summary.api} />
        <StatusBadge label="RAG" status={summary.rag} />
        <StatusBadge label="AI" status={summary.ai} />
        <StatusBadge label="Vector" status={summary.vector} />
      </div>
      {summary.lastChecked !== null && (
        <p className="text-xs text-slate-500">
          Last checked: {new Date(summary.lastChecked).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}

function StatusBadge({
  label,
  status,
}: {
  label: string;
  status: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium",
        statusColor(
          status as "healthy" | "ready" | "degraded" | "unreachable" | "error"
        )
      )}
      title={`${label}: ${status}`}
    >
      {label}: {statusLabel(status as "healthy" | "ready" | "degraded" | "unreachable" | "error")}
    </span>
  );
}
