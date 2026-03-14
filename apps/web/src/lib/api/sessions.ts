/**
 * Sessions API: list, create, get, rename, delete.
 */

import { apiRequest } from "./client";
import type { SessionSummary, SessionDetailResponse } from "@/lib/types/sessions";

export async function listSessions(): Promise<{ sessions: SessionSummary[] }> {
  return apiRequest<{ sessions: SessionSummary[] }>("/sessions", { method: "GET" });
}

export async function createSession(title?: string): Promise<{ session: SessionSummary }> {
  return apiRequest<{ session: SessionSummary }>("/sessions", {
    method: "POST",
    body: JSON.stringify(title != null && title !== "" ? { title } : {}),
  });
}

export async function getSession(sessionId: string): Promise<SessionDetailResponse> {
  return apiRequest<SessionDetailResponse>(`/sessions/${sessionId}`, { method: "GET" });
}

export async function renameSession(
  sessionId: string,
  title: string
): Promise<{ status: string; session_id: string }> {
  return apiRequest(`/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

export async function deleteSession(
  sessionId: string
): Promise<{ status: string; session_id: string }> {
  return apiRequest(`/sessions/${sessionId}`, { method: "DELETE" });
}
