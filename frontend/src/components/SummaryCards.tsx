import { useMemo } from "react";
import { motion } from "framer-motion";
import type { Product, SearchResponse } from "../types";
import { useCountUp } from "../hooks/useCountUp";
import { fmtINR, storeLabel } from "../lib/format";
import { SpeechBubble } from "./comic";

function PowerCard({ title, tone, p, note, delay }: { title: string; tone: string; p?: Product; note: string; delay: number }) {
  const price = useCountUp(p?.price ?? 0);
  return (
    <motion.div initial={{ opacity: 0, scale: 0.85, rotate: -2 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ delay, type: "spring", stiffness: 220, damping: 16 }}
      className={`comic-border rounded-md p-5 ${tone}`}>
      <p className="font-display text-2xl tracking-wider">{title}</p>
      {p ? (
        <>
          <p className="mt-1 font-caption text-lg font-bold uppercase">{storeLabel(p.site)}</p>
          <p className="font-mono text-3xl font-bold">{fmtINR(price)}</p>
          <p className="mt-1 line-clamp-2 text-sm font-semibold" title={p.name}>{p.name}</p>
        </>
      ) : <p className="mt-2 font-semibold">Not available</p>}
      <p className="mt-2 text-sm font-semibold">{note}</p>
    </motion.div>
  );
}

export function SummaryCards({ data }: { data: SearchResponse }) {
  const byId = useMemo(() => new Map(data.results.map((p) => [p.id, p])), [data]);
  const s = data.summary;
  const cards = [
    {
      title: "CHEAPEST", tone: "bg-spidey text-white", p: s.cheapest ? byId.get(s.cheapest.id) : undefined,
      note: s.savings_vs_highest && s.savings_vs_highest.inr > 0
        ? `Save ${fmtINR(s.savings_vs_highest.inr)} (${s.savings_vs_highest.percent}%) vs the priciest store` : "Lowest price found",
    },
    {
      title: "BEST DEAL", tone: "bg-electric text-miles", p: s.best_deal ? byId.get(s.best_deal.id) : undefined,
      note: s.best_deal ? `Recommendation score ${s.best_deal.score}/100` : "",
    },
    {
      title: "FASTEST DELIVERY", tone: "bg-comic text-miles", p: s.fastest_delivery ? byId.get(s.fastest_delivery.id) : undefined,
      note: s.fastest_delivery ? `Arrives in ~${s.fastest_delivery.days} day(s)` : "No delivery estimates",
    },
  ];
  return (
    <section aria-label="Summary" className="space-y-8">
      <div className="grid gap-5 md:grid-cols-3">
        {cards.map((c, i) => <PowerCard key={c.title} {...c} delay={i * 0.1} />)}
      </div>
      {s.explanation && (
        <SpeechBubble>
          {s.explanation} {s.best_deal?.reason ? <span className="opacity-80">Best overall: {s.best_deal.reason}</span> : null}
        </SpeechBubble>
      )}
    </section>
  );
}