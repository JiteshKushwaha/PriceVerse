import { useMemo } from "react";
import toast from "react-hot-toast";
import type { Product, SortKey } from "../types";
import { useUI } from "../store";
import { fmtINR, storeLabel } from "../lib/format";

const SORTS: [SortKey, string][] = [
  ["recommended", "Recommended"], ["price", "Price: low → high"], ["discount", "Discount"], ["rating", "Rating"], ["delivery", "Fastest delivery"],
];

export function FilterBar({ results, shown }: { results: Product[]; shown: number }) {
  const { filters, setFilter, toggleStore, resetFilters, view, setView } = useUI();
  const stores = useMemo(() => Array.from(new Set(results.map((p) => p.site))), [results]);
  const [lo, hi] = useMemo(() => {
    const prices = results.map((p) => p.price);
    return [Math.floor(Math.min(...prices)), Math.ceil(Math.max(...prices))];
  }, [results]);
  const current = filters.maxPrice ?? hi;

  const share = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) await navigator.share({ title: "PriceVerse deal", url });
      else { await navigator.clipboard.writeText(url); toast.success("Link copied! Share the deal."); }
    } catch { /* user cancelled */ }
  };

  return (
    <div className="sticky top-[104px] z-30 md:top-[68px]">
      <div className="panel flex flex-wrap items-center gap-x-5 gap-y-3 p-3 text-sm">
        <label className="flex items-center gap-2 font-semibold">
          Sort
          <select value={filters.sort} onChange={(e) => setFilter("sort", e.target.value as SortKey)}
            className="rounded border-2 border-black bg-white px-2 py-1 text-miles">
            {SORTS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
          </select>
        </label>

        <fieldset className="flex flex-wrap items-center gap-1.5">
          <legend className="sr-only">Stores</legend>
          {stores.map((s) => {
            const on = filters.stores.includes(s);
            return (
              <button key={s} type="button" aria-pressed={on} onClick={() => toggleStore(s)}
                className={`chip px-2.5 py-1 ${on ? "bg-miles text-paper dark:bg-paper dark:text-miles" : "bg-white text-miles"}`}>
                {storeLabel(s)}
              </button>
            );
          })}
        </fieldset>

        {hi > lo && (
          <label className="flex items-center gap-2 font-semibold">
            Max <span className="font-mono">{fmtINR(current)}</span>
            <input type="range" min={lo} max={hi} step={Math.max(1, Math.round((hi - lo) / 100))} value={current}
              onChange={(e) => { const v = Number(e.target.value); setFilter("maxPrice", v >= hi ? null : v); }}
              className="w-32 accent-spidey" aria-label="Maximum price" />
          </label>
        )}

        <label className="flex items-center gap-1.5 font-semibold">
          <input type="checkbox" checked={filters.inStock} onChange={(e) => setFilter("inStock", e.target.checked)} className="h-4 w-4 accent-spidey" />
          In stock only
        </label>
        <label className="flex items-center gap-1.5 font-semibold">
          <input type="checkbox" checked={filters.freeDelivery} onChange={(e) => setFilter("freeDelivery", e.target.checked)} className="h-4 w-4 accent-spidey" />
          Free delivery
        </label>

        <div className="ml-auto flex items-center gap-2">
          <span className="font-mono text-xs" aria-live="polite">{shown}/{results.length}</span>
          <button type="button" onClick={resetFilters} className="chip bg-white px-2.5 py-1 text-miles">Reset</button>
          <div role="group" aria-label="View" className="flex overflow-hidden rounded-full border-2 border-black">
            {(["grid", "table"] as const).map((v) => (
              <button key={v} type="button" aria-pressed={view === v} onClick={() => setView(v)}
                className={`px-3 py-1 font-caption font-bold uppercase ${view === v ? "bg-spidey text-white" : "bg-white text-miles"}`}>{v}</button>
            ))}
          </div>
          <button type="button" onClick={share} className="chip bg-comic px-2.5 py-1 text-miles" aria-label="Copy or share link">🔗 Share</button>
        </div>
      </div>
    </div>
  );
}