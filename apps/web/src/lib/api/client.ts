/**
 * Base API client: configurable base URL, consistent error handling.
 */

const getBaseUrl = (): string => {
  if (typeof window === "undefined") return "";
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
};

export interface ApiError {
  status: number;
  error?: string;
  message?: string;
  detail?: string | Record<string, unknown>;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const base = getBaseUrl().replace(/\/$/, "");
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  let body: unknown;
  const contentType = res.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    try {
      body = await res.json();
    } catch {
      body = null;
    }
  } else {
    body = await res.text();
  }

  if (!res.ok) {
    const err: ApiError = {
      status: res.status,
      message: typeof body === "string" ? body : "Request failed",
    };
    if (body && typeof body === "object" && !Array.isArray(body)) {
      const obj = body as Record<string, unknown>;
      if (typeof obj.error === "string") err.error = obj.error;
      if (typeof obj.message === "string") err.message = obj.message;
      if (obj.detail !== undefined) err.detail = obj.detail as string | Record<string, unknown>;
    }
    throw err;
  }

  return body as T;
}

export function getApiBaseUrl(): string {
  return getBaseUrl();
}
