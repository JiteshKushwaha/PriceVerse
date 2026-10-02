import type { HistoryPoint, Product, SearchResponse, SiteInfo, SiteStatus } from "../types";

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(public status: number, message: string, public retryAfter?: number) {
    super(message);
  }
}

async function get<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`);
  } catch {
    throw new ApiError(0, "Server offline");
  }
  if (!res.ok) {
    let body: { detail?: unknown; retry_after?: number } = {};
    try { body = await res.json(); } catch { /* not JSON */ }
    const ra = Number(res.headers.get("Retry-After") || body.retry_after || 0) || undefined;
    throw new ApiError(res.status, body.detail ? String(body.detail) : `HTTP ${res.status}`, ra);
  }
  return (await res.json()) as T;
}

export const api = {
  search: (q: string, fresh = false) =>
    get<SearchResponse>(`/api/search?q=${encodeURIComponent(q)}${fresh ? "&fresh=true" : ""}`),
  sites: () => get<SiteInfo[]>("/api/sites"),
  health: () => get<{ status: string; cache: string; browser: boolean; demo_mode: boolean }>("/api/health"),
  history: (q: string, days = 30) =>
    get<{ query: string; days: number; points: HistoryPoint[] }>(`/api/history?q=${encodeURIComponent(q)}&days=${days}`),
};

export const redirectUrl = (p: Product) =>
  `${API_BASE}/api/redirect?url=${encodeURIComponent(p.url)}&site=${encodeURIComponent(p.site)}`;

interface StreamHandlers {
  onSite: (s: SiteStatus) => void;
  onResult: (d: SearchResponse) => void;
  onError: (e: ApiError) => void;
}

/** Opens an SSE stream; falls back to a plain GET if EventSource fails. Returns a cancel function. */
export function streamSearch(q: string, fresh: boolean, h: StreamHandlers): () => void {
  const url = `${API_BASE}/api/search/stream?q=${encodeURIComponent(q)}${fresh ? "&fresh=true" : ""}`;
  let finished = false;
  let es: EventSource;
  try {
    es = new EventSource(url);
  } catch {
    api.search(q, fresh).then(h.onResult).catch(h.onError);
    return () => { finished = true; };
  }
  es.addEventListener("site", (e) => {
    if (!finished) h.onSite(JSON.parse((e as MessageEvent).data));
  });
  es.addEventListener("result", (e) => {
    finished = true;
    es.close();
    h.onResult(JSON.parse((e as MessageEvent).data));
  });
  es.addEventListener("error", (e) => {
    const me = e as MessageEvent;
    if (finished) return;
    finished = true;
    es.close();
    if (me.data) {
      const d = JSON.parse(me.data);
      h.onError(new ApiError(d.status ?? 500, d.message ?? "Error", d.retry_after));
      return;
    }
    // network-level failure of the stream → try once with plain GET
    api.search(q, fresh).then(h.onResult).catch((err) =>
      h.onError(err instanceof ApiError ? err : new ApiError(0, "Server offline")));
  });
  return () => {
    finished = true;
    es.close();
  };
}