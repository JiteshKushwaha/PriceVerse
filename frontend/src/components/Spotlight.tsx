import { useEffect, useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { Product } from "../types";
import { redirectUrl } from "../lib/api";
import { fmtINR, storeLabel } from "../lib/format";

function SpotCard({ p, rank, active }: { p: Product; rank: number; active: boolean }) {
  return (
    <div className="panel flex h-[300px] flex-col gap-2 p-5">
      <div className="flex items-start justify-between">
        <span className="font-display text-5xl text-spidey [text-shadow:3px_3px_0_#000]">#{rank}</span>
        <span className="chip bg-electric text-miles">Score {p.score}</span>
      </div>
      <p className="font-caption text-lg font-bold uppercase">{storeLabel(p.site)}</p>
      <p className="line-clamp-2 font-semibold" title={p.name}>{p.name}</p>
      <p className="font-mono text-2xl font-bold">{fmtINR(p.price)}</p>
      {p.discount_percent ? <p className="text-sm">{p.discount_percent}% off MRP</p> : null}
      <a href={redirectUrl(p)} target="_blank" rel="noopener noreferrer" tabIndex={active ? 0 : -1}
        className="mt-auto rounded border-[3px] border-black bg-spidey py-2 text-center font-display tracking-wider text-white shadow-comic-sm">
        GO TO {storeLabel(p.site).toUpperCase()} ➜
      </a>
    </div>
  );
}

export function Spotlight({ results }: { results: Product[] }) {
  const top = useMemo(() => [...results].sort((a, b) => b.score - a.score).slice(0, 5), [results]);
  const [idx, setIdx] = useState(0);
  const reduce = useReducedMotion();
  const [paused, setPaused] = useState(!!reduce);
  const n = top.length;

  useEffect(() => setIdx(0), [results]);
  useEffect(() => {
    if (paused || n < 2) return;
    const t = setInterval(() => setIdx((i) => (i + 1) % n), 4000);
    return () => clearInterval(t);
  }, [paused, n]);
  if (n === 0) return null;

  const go = (d: number) => setIdx((i) => (i + d + n) % n);
  const pad = (x: number) => String(x).padStart(2, "0");

  return (
    <div role="region" aria-roledescription="carousel" aria-label="Recommended picks" tabIndex={0}
      onKeyDown={(e) => { if (e.key === "ArrowLeft") go(-1); if (e.key === "ArrowRight") go(1); }}
      className="rounded-xl bg-miles p-4 text-paper sm:p-6">
      <div className="relative h-[340px] overflow-hidden">
        {top.map((p, i) => {
          let off = i - idx;
          if (off > n / 2) off -= n;
          if (off < -n / 2) off += n;
          const hidden = Math.abs(off) > 1;
          return (
            <motion.div key={p.id} aria-hidden={off !== 0}
              className={`absolute left-1/2 top-4 w-[260px] -ml-[130px] text-miles sm:w-[300px] sm:-ml-[150px] ${off !== 0 ? "pointer-events-none" : ""}`}
              animate={{ x: `${off * 72}%`, rotate: off * 8, scale: off === 0 ? 1 : 0.85, opacity: hidden ? 0 : off === 0 ? 1 : 0.55 }}
              transition={{ type: "spring", stiffness: 200, damping: 24 }} style={{ zIndex: 10 - Math.abs(off) }}>
              <SpotCard p={p} rank={i + 1} active={off === 0} />
            </motion.div>
          );
        })}
      </div>
      <div className="mt-2 flex items-center justify-center gap-3">
        <button type="button" onClick={() => go(-1)} aria-label="Previous" className="h-11 w-11 rounded-full border-2 border-paper/60 hover:bg-paper hover:text-miles">←</button>
        <button type="button" onClick={() => setPaused((p) => !p)} aria-label={paused ? "Play" : "Pause"} className="h-11 w-11 rounded-full border-2 border-paper/60 hover:bg-paper hover:text-miles">
          {paused ? "▶" : "❚❚"}
        </button>
        <button type="button" onClick={() => go(1)} aria-label="Next" className="h-11 w-11 rounded-full border-2 border-paper/60 hover:bg-paper hover:text-miles">→</button>
        <span className="ml-2 font-mono text-sm" aria-live="polite">{pad(idx + 1)} / {pad(n)}</span>
      </div>
    </div>
  );
}