import { useCallback, useEffect, useState } from "react";

const read = () => new URLSearchParams(window.location.search).get("q") ?? "";
/** `?q=` in the URL is the source of truth for the current search. */
export function useQueryParam(): [string, (q: string) => void] {
  const [q, setQ] = useState(read);
  useEffect(() => {
    const onPop = () => setQ(read());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const update = useCallback((value: string) => {
    const url = new URL(window.location.href);
    if (value) url.searchParams.set("q", value);
    else url.searchParams.delete("q");
    window.history.pushState({}, "", url);
    setQ(value);
  }, []);
  return [q, update];
}