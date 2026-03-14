"use client";

import { cn } from "@/lib/utils/cn";
import type { ChatMessage } from "@/lib/types/chat";
import { SourceList } from "./source-list";
import { formatDate } from "@/lib/utils/format";

interface MessageBubbleProps {
  message: ChatMessage;
  showDebug?: boolean;
}

export function MessageBubble({ message, showDebug }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm",
          isUser
            ? "bg-slate-800 text-white"
            : "bg-white border border-slate-200 text-slate-800 shadow-sm"
        )}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        {message.error && (
          <p className="mt-2 text-red-600 text-xs font-medium" role="alert">
            {message.error}
          </p>
        )}
        {isAssistant && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-100">
            <SourceList sources={message.sources} />
          </div>
        )}
        {isAssistant && showDebug && message.debug && (
          <div className="mt-3 pt-3 border-t border-slate-100">
            <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-500">
              <dt>top_k</dt>
              <dd>{message.debug.top_k_used}</dd>
              <dt>min_score</dt>
              <dd>{message.debug.min_score_used}</dd>
              <dt>context chars</dt>
              <dd>{message.debug.context_char_count}</dd>
              <dt>retrieved</dt>
              <dd>{message.debug.retrieved_count}</dd>
              <dt>selected</dt>
              <dd>{message.debug.selected_count}</dd>
              <dt>model</dt>
              <dd className="truncate" title={message.debug.model}>
                {message.debug.model}
              </dd>
              <dt>prompt</dt>
              <dd className="truncate" title={message.debug.prompt_name}>
                {message.debug.prompt_name}
              </dd>
            </dl>
          </div>
        )}
        <div
          className={cn(
            "mt-1 text-xs",
            isUser ? "text-slate-300" : "text-slate-400"
          )}
        >
          {formatDate(message.createdAt)}
        </div>
      </div>
    </div>
  );
}
