"use client";

import { useState, useRef, useEffect } from "react";
import type { SessionSummary } from "@/lib/types/sessions";

interface SessionListItemProps {
  session: SessionSummary;
  isActive: boolean;
  onSelect: () => void;
  onRename: (title: string) => void;
  onDelete: () => void;
}

export function SessionListItem({
  session,
  isActive,
  onSelect,
  onRename,
  onDelete,
}: SessionListItemProps) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(session.title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) {
      setEditValue(session.title);
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [editing, session.title]);

  const handleSubmit = () => {
    const t = editValue.trim();
    if (t && t !== session.title) onRename(t);
    setEditing(false);
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => !editing && onSelect()}
      onKeyDown={(e) => {
        if (editing) {
          if (e.key === "Enter") handleSubmit();
          if (e.key === "Escape") setEditing(false);
        } else if (e.key === "Enter" || e.key === " ") onSelect();
      }}
      className={`group flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
        isActive
          ? "bg-slate-200 font-medium text-slate-900"
          : "text-slate-700 hover:bg-slate-100"
      }`}
    >
      {editing ? (
        <input
          ref={inputRef}
          type="text"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={handleSubmit}
          onKeyDown={(e) => {
            e.stopPropagation();
            if (e.key === "Enter") handleSubmit();
            if (e.key === "Escape") setEditing(false);
          }}
          className="min-w-0 flex-1 rounded border border-slate-300 bg-white px-2 py-1 text-slate-900"
          aria-label="Rename session"
        />
      ) : (
        <>
          <span className="min-w-0 flex-1 truncate" title={session.title}>
            {session.title}
          </span>
          <div className="flex shrink-0 gap-0.5 opacity-0 group-hover:opacity-100">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setEditing(true);
              }}
              className="rounded p-1 text-slate-500 hover:bg-slate-200 hover:text-slate-700"
              aria-label="Rename"
            >
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              className="rounded p-1 text-slate-500 hover:bg-red-100 hover:text-red-700"
              aria-label="Delete"
            >
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
