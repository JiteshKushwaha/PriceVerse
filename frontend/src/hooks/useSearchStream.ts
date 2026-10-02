import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ApiError, streamSearch } from "../lib/api";
import type { SearchResponse, SiteStatus } from "../types";

export type Phase = "idle" | "loading" | "done" | "error";
interface State { phase: Phase; sites: Record<string, SiteStatus>; data: SearchResponse | null; error: ApiError | null }
const IDLE: State = { phase: "idle", sites: {}, data: null, error: null };
const toMap = (list: SiteStatus[]) => Object.fromEntries(list.map((s) => [s.site, s]));

export function useSearchStream(q: string) {
  const qc = useQueryClient();
  const [state, setState] = useState<State>(IDLE);
  const [retryKey, setRetryKey] = useState<{ q: string; n: number }>({ q: "", n: 0 });
  const fresh = retryKey.q === q && retryKey.n > 0;

  useEffect(() => {
    if (!q) { setState(IDLE); return; }
    const cached = fresh ? undefined : qc.getQueryData<SearchResponse>(["search", q]);
    if (cached) {
      setState({ phase: "done", sites: toMap(cached.sites), data: cached, error: null });
      return;
    }
    setState({ ...IDLE, phase: "loading" });
    return streamSearch(q, fresh, {
      onSite: (s) => setState((st) => ({ ...st, sites: { ...st.sites, [s.site]: s } })),
      onResult: (d) => {
        qc.setQueryData(["search", q], d);
        setState({ phase: "done", sites: toMap(d.sites), data: d, error: null });
      },
      onError: (e) => setState((st) => ({ ...st, phase: "error", error: e })),
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, retryKey, qc]);

  const retry = () => setRetryKey((r) => ({ q, n: r.q === q ? r.n + 1 : 1 }));
  return { ...state, retry };
}