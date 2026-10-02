import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { SearchResponse } from "../types";
import { api } from "../lib/api";
import { fmtINR, storeLabel } from "../lib/format";
import { ComicPanel } from "./comic";

const short = (v: number) => (v >= 100000 ? `${(v / 100000).toFixed(1)}L` : v >= 1000 ? `${Math.round(v / 1000)}k` : `${v}`);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function ComicTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded border-[3px] border-black bg-comic px-3 py-2 text-miles shadow-comic-sm">
      <p className="font-caption font-bold uppercase">{label}</p>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {payload.map((e: any) => <p key={e.dataKey} className="font-mono text-sm font-bold">{e.name}: {fmtINR(e.value)}</p>)}
    </div>
  );
}

export function PriceChart({ data, q }: { data: SearchResponse; q: string }) {
  const bars = useMemo(
    () => data.sites.filter((s) => s.min_price != null).map((s) => ({ store: storeLabel(s.site), price: s.min_price as number })).sort((a, b) => a.price - b.price),
    [data],
  );
  const hist = useQuery({ queryKey: ["history", q], queryFn: () => api.history(q, 30), enabled: !!q, staleTime: 60_000 });
  const points = hist.data?.points ?? [];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <ComicPanel caption="Lowest price per store">
        <div className="mt-3 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={bars} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#8885" />
              <XAxis dataKey="store" tick={{ fontSize: 12, fill: "currentColor" }} interval={0} angle={-15} textAnchor="end" height={50} />
              <YAxis tickFormatter={short} tick={{ fontSize: 12, fill: "currentColor" }} width={48} />
              <Tooltip content={<ComicTooltip />} cursor={{ fill: "#FFD60A33" }} />
              <Bar dataKey="price" name="Min price" radius={[4, 4, 0, 0]} stroke="#000" strokeWidth={2}>
                {bars.map((_, i) => <Cell key={i} fill={i === 0 ? "#00E5FF" : "#FF2E93"} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ComicPanel>
      <ComicPanel caption="Price history (30 days)">
        <div className="mt-3 h-72">
          {hist.isLoading ? <p className="p-4">Loading history…</p> : points.length < 2 ? (
            <p className="p-4 text-sm">History grows every time this product is searched. Come back later for a trend line!</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={points} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#8885" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "currentColor" }} tickFormatter={(d: string) => d.slice(5)} />
                <YAxis tickFormatter={short} tick={{ fontSize: 12, fill: "currentColor" }} width={48} domain={["auto", "auto"]} />
                <Tooltip content={<ComicTooltip />} />
                <Legend />
                <Line type="monotone" dataKey="min_price" name="Lowest" stroke="#00E5FF" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="avg_price" name="Average" stroke="#FF2E93" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        {points.some((p) => p.synthetic) && <p className="text-xs opacity-75">Includes simulated demo history.</p>}
      </ComicPanel>
    </div>
  );
}