"use client";

import { useState, useCallback, KeyboardEvent } from "react";
import { cn } from "@/lib/utils/cn";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Ask a question…",
}: ChatInputProps) {
  const [value, setValue] = useState("");

  const send = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="flex gap-2 items-end rounded-xl border border-slate-200 bg-white p-2 shadow-sm focus-within:ring-2 focus-within:ring-slate-300 focus-within:border-slate-300">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="min-h-[44px] max-h-32 flex-1 resize-y bg-transparent px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 outline-none disabled:opacity-60"
        aria-label="Message"
      />
      <button
        type="button"
        onClick={send}
        disabled={!canSend}
        className={cn(
          "shrink-0 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
          canSend
            ? "bg-slate-800 text-white hover:bg-slate-700"
            : "bg-slate-200 text-slate-500 cursor-not-allowed"
        )}
        aria-label="Send"
      >
        Send
      </button>
    </div>
  );
}
