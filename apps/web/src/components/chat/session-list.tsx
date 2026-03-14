"use client";

import { SessionListItem } from "./session-list-item";
import type { SessionSummary } from "@/lib/types/sessions";

interface SessionListProps {
  sessions: SessionSummary[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onRenameSession: (id: string, title: string) => void;
  onDeleteSession: (id: string) => void;
}

export function SessionList({
  sessions,
  activeSessionId,
  onSelectSession,
  onRenameSession,
  onDeleteSession,
}: SessionListProps) {
  if (sessions.length === 0) {
    return (
      <p className="px-3 py-4 text-sm text-slate-500">No chats yet. Start a new chat.</p>
    );
  }
  return (
    <ul className="flex flex-col gap-0.5" role="list">
      {sessions.map((s) => (
        <li key={s.id}>
          <SessionListItem
            session={s}
            isActive={s.id === activeSessionId}
            onSelect={() => onSelectSession(s.id)}
            onRename={(title) => onRenameSession(s.id, title)}
            onDelete={() => onDeleteSession(s.id)}
          />
        </li>
      ))}
    </ul>
  );
}
