"use client";

import { useState, useCallback } from "react";
import { cn } from "@/lib/utils/cn";
import type { ChatMessage } from "@/lib/types/chat";
import type { FeedbackType } from "@/lib/types/feedback";
import { SourceList } from "./source-list";
import { formatDate } from "@/lib/utils/format";
import { submitFeedback } from "@/lib/api/feedback";

interface MessageBubbleProps {
  message: ChatMessage;
  showDebug?: boolean;
  sessionId?: string;
}

export function MessageBubble({ message, showDebug, sessionId }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const [feedbackSent, setFeedbackSent] = useState<FeedbackType | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const canFeedback =
    isAssistant &&
    sessionId &&
    message.messageId &&
    message.content &&
    !feedbackSent;

  const sendFeedback = useCallback(
    async (type: FeedbackType) => {
      if (!sessionId || !message.messageId || submitting || feedbackSent) return;
      setSubmitting(true);
      setFeedbackError(null);
      try {
        await submitFeedback({
          session_id: sessionId,
          message_id: message.messageId,
          feedback_type: type,
          answer_text: message.content,
          sources: message.sources,
          debug: message.debug ?? undefined,
        });
        setFeedbackSent(type);
      } catch {
        setFeedbackError("Could not send feedback");
      } finally {
        setSubmitting(false);
      }
    },
    [sessionId, message.messageId, message.content, message.sources, message.debug, submitting, feedbackSent]
  );

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
        {canFeedback && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs text-slate-500">Helpful?</span>
            <button
              type="button"
              onClick={() => sendFeedback("up")}
              disabled={submitting}
              className={cn(
                "rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50",
                feedbackSent === "up" && "text-green-600"
              )}
              aria-label="Thumbs up"
              title="Helpful"
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 11V4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7" />
              </svg>
            </button>
            <button
              type="button"
              onClick={() => sendFeedback("down")}
              disabled={submitting}
              className={cn(
                "rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50",
                feedbackSent === "down" && "text-red-600"
              )}
              aria-label="Thumbs down"
              title="Not helpful"
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-11V4a1 1 0 0 0-1-1h-2a1 1 0 0 0-1 1v7" />
              </svg>
            </button>
            {feedbackSent && (
              <span className="text-xs text-slate-500">
                {feedbackSent === "up" ? "Thanks" : "Recorded"}
              </span>
            )}
            {feedbackError && (
              <span className="text-xs text-red-600" role="alert">
                {feedbackError}
              </span>
            )}
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
