"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { SessionList } from "./session-list";
import {
  listSessions,
  createSession,
  renameSession,
  deleteSession,
} from "@/lib/api/sessions";
import type { SessionSummary } from "@/lib/types/sessions";

interface SessionSidebarProps {
  activeSessionId: string | null;
  onSessionSelect: (sessionId: string | null) => void;
  onSessionsChange?: () => void;
}

export function SessionSidebar({
  activeSessionId,
  onSessionSelect,
  onSessionsChange,
}: SessionSidebarProps) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const initialLoadDone = useRef(false);

  const fetchSessions = useCallback(async () => {
    try {
      const res = await listSessions();
      setSessions(res.sessions);
      if (!initialLoadDone.current && res.sessions.length > 0) {
        onSessionSelect(res.sessions[0].id);
        initialLoadDone.current = true;
      }
    } catch {
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, [onSessionSelect]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleNewChat = useCallback(async () => {
    if (creating) return;
    setCreating(true);
    try {
      const { session } = await createSession();
      setSessions((prev) => [session, ...prev]);
      onSessionSelect(session.id);
      onSessionsChange?.();
    } catch {
      // ignore
    } finally {
      setCreating(false);
    }
  }, [creating, onSessionSelect, onSessionsChange]);

  const handleRename = useCallback(
    async (id: string, title: string) => {
      try {
        await renameSession(id, title);
        setSessions((prev) =>
          prev.map((s) => (s.id === id ? { ...s, title } : s))
        );
        onSessionsChange?.();
      } catch {
        // ignore
      }
    },
    [onSessionsChange]
  );

  const handleDelete = useCallback(
    async (id: string) => {
      if (!confirm("Delete this chat? This cannot be undone.")) return;
      try {
        await deleteSession(id);
        setSessions((prev) => prev.filter((s) => s.id !== id));
        if (activeSessionId === id) onSessionSelect(null);
        onSessionsChange?.();
      } catch {
        // ignore
      }
    },
    [activeSessionId, onSessionSelect, onSessionsChange]
  );

  return (
    <aside
      className="flex w-56 shrink-0 flex-col rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden"
      aria-label="Chat sessions"
    >
      <div className="shrink-0 border-b border-slate-200 p-2">
        <button
          type="button"
          onClick={handleNewChat}
          disabled={loading || creating}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New chat
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        {loading ? (
          <p className="px-3 py-4 text-sm text-slate-500">Loading…</p>
        ) : (
          <SessionList
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={onSessionSelect}
            onRenameSession={handleRename}
            onDeleteSession={handleDelete}
          />
        )}
      </div>
    </aside>
  );
}
