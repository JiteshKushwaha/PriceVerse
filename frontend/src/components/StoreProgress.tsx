import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import type { SiteStatus } from "../types";
import { fmtINR, storeColor, storeLabel } from "../lib/format";
import { Skeleton } from "./comic";

const CAPTIONS = ["THWIP!", "Crawling the web…", "Spidey-sense tingling…", "Swinging past the villains…", "Checking every rooftop…"];

function statusLine(s: SiteStatus): { text: string; tone: string } {
  switch (s.status) {
    case "searching": return { text: "Searching…", tone: "" };
    case "ok": return { text: `✔ Found ${s.result_count} deal${s.result_count === 1 ? "" : "s"}`, tone: "bg-electric/20" };
    case "blocked": return { text: "✖ Blocked, skipped", tone: "bg-spidey/15" };
    case "timeout": return { text: "⏱ Too slow, skipped", tone: "bg-comic/25" };
    case "empty": return { text: "∅ No matches", tone: "" };
    default: return { text: "✖ Error, skipped", tone: "bg-spidey/15" };
  }
}

function SitePanel({ s }: { s: SiteStatus }) {
  const { text, tone } = statusLine(s);
  return (
    <motion.div key={s.status} initial={{ rotateY: 90, opacity: 0 }} animate={{ rotateY: 0, opacity: 1 }} transition={{ duration: 0.35 }}
      className={`panel flex h-32 flex-col justify-between p-4 ${tone}`}>
      <span className="flex items-center gap-2 font-caption text-lg font-bold uppercase">
        <span className="h-3 w-3 rounded-full border-2 border-black" style={{ background: storeColor(s.site) }} aria-hidden="true" />
        {storeLabel(s.site)}
      </span>
      <span className={`font-display text-xl tracking-wide ${s.status === "searching" ? "animate-pulse" : ""}`}>{text}</span>
      <span className="text-xs opacity-80">
        {s.status === "ok" && s.min_price != null ? `from ${fmtINR(s.min_price)}` : s.message ?? ""}
        {s.duration_ms ? ` · ${(s.duration_ms / 1000).toFixed(1)}s` : ""}
      </span>
    </motion.div>
  );
}

export function StoreProgress({ sites }: { sites: Record<string, SiteStatus> }) {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((x) => (x + 1) % CAPTIONS.length), 1400);
    return () => clearInterval(t);
  }, []);
  const list = Object.values(sites);
  const done = list.filter((s) => s.status !== "searching").length;
  return (
    <section aria-live="polite" aria-busy="true" aria-label="Search progress">
      <h2 className="headline text-4xl sm:text-5xl">SPIDEY-SENSE TINGLING…</h2>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className="caption">{CAPTIONS[i]}</span>
        {list.length > 0 && <span className="font-mono text-sm">{done}/{list.length} stores checked</span>}
      </div>
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4" style={{ perspective: 800 }}>
        {list.length === 0
          ? Array.from({ length: 6 }).map((_, k) => <Skeleton key={k} className="h-32" />)
          : list.map((s) => <div key={s.site}><SitePanel s={s} /></div>)}
      </div>
    </section>
  );
}