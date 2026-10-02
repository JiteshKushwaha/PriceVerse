import { useCallback, useState } from "react";

const KEY = "priceverse-recent";
export function useRecent() {
  const [recent, setRecent] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch { return []; }
  });
  const add = useCallback((q: string) => {
    setRecent((prev) => {
      const next = [q, ...prev.filter((x) => x.toLowerCase() !== q.toLowerCase())].slice(0, 8);
      localStorage.setItem(KEY, JSON.stringify(next));
      return next;
    });
  }, []);
  const clear = useCallback(() => {
    localStorage.removeItem(KEY);
    setRecent([]);
  }, []);
  return { recent, add, clear };
}