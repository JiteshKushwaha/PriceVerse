import { useId, useState } from "react";
import { motion } from "framer-motion";
import type { Product } from "../types";
import { redirectUrl } from "../lib/api";
import { useCountUp } from "../hooks/useCountUp";
import { BADGE_LABEL, deliveryLabel, fmtINR, OFFER_LABEL, storeColor, storeLabel } from "../lib/format";
import { ComicLink, StarBurst } from "./comic";

export function Stars({ rating, count }: { rating: number; count: number | null }) {
  const full = Math.round(rating);
  return (
    <span className="text-sm" aria-label={`Rated ${rating} out of 5${count ? ` from ${count} reviews` : ""}`}>
      <span aria-hidden="true" className="text-comic [text-shadow:1px_1px_0_#000]">{"★".repeat(full)}</span>
      <span aria-hidden="true" className="opacity-30">{"★".repeat(5 - full)}</span>{" "}
      <span className="font-semibold">{rating.toFixed(1)}</span>
      {count ? <span className="opacity-75"> ({count.toLocaleString("en-IN")})</span> : null}
    </span>
  );
}

function Price({ p }: { p: Product }) {
  const v = useCountUp(p.price);
  return (
    <div className="flex flex-wrap items-baseline gap-2">
      <span className="font-mono text-2xl font-bold">{fmtINR(v)}</span>
      {p.mrp && <span className="font-mono text-sm line-through opacity-60">{fmtINR(p.mrp)}</span>}
    </div>
  );
}

export function ProductCard({ p, index }: { p: Product; index: number }) {
  const [showAll, setShowAll] = useState(false);
  const [imgOk, setImgOk] = useState(true);
  const tip = useId();
  const specs = Object.entries(p.specs);
  const visible = showAll ? specs : specs.slice(0, 4);
  const tilt = ["-rotate-[0.6deg]", "rotate-[0.5deg]", "rotate-0"][index % 3];

  return (
    <motion.article layout initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(index, 8) * 0.05 }}
      className={`panel flex flex-col overflow-hidden ${tilt} transition-transform hover:rotate-0`}>
      <div className="relative grid h-44 place-items-center border-b-[3px] border-black bg-white">
        {p.image_url && imgOk ? (
          <img src={p.image_url} alt="" loading="lazy" referrerPolicy="no-referrer" onError={() => setImgOk(false)} className="max-h-40 object-contain p-2" />
        ) : (
          <div className="halftone grid h-full w-full place-items-center">
            <span className="font-display text-4xl text-miles/70">{storeLabel(p.site).slice(0, 2).toUpperCase()}</span>
          </div>
        )}
        <span className="chip absolute left-2 top-2 flex items-center gap-1 bg-white text-miles">
          <span className="h-2.5 w-2.5 rounded-full border border-black" style={{ background: storeColor(p.site) }} aria-hidden="true" />
          {storeLabel(p.site)}
        </span>
        {p.discount_percent ? (
          <StarBurst className="absolute -right-1 -top-1" size={66}>-{Math.round(p.discount_percent)}%</StarBurst>
        ) : null}
        {p.badges.length > 0 && (
          <div className="absolute bottom-2 left-2 flex flex-wrap gap-1">
            {p.badges.map((b) => (
              <span key={b} className={`chip ${b === "CHEAPEST" ? "bg-spidey text-white" : b === "BEST_DEAL" ? "bg-electric text-miles" : "bg-comic text-miles"}`}>
                {BADGE_LABEL[b] ?? b}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <h3 className="line-clamp-2 font-semibold leading-snug" title={p.name}>{p.name}</h3>
        <Price p={p} />
        {p.rating != null && <Stars rating={p.rating} count={p.review_count} />}
        <p className="text-sm">🚚 {deliveryLabel(p)}</p>

        {p.offers.length > 0 && (
          <ul className="flex flex-wrap gap-1.5" aria-label="Offers">
            {p.offers.slice(0, 3).map((o, i) => (
              <li key={i} className="group relative">
                <span tabIndex={0} aria-describedby={`${tip}-${i}`} className="chip cursor-help bg-paper text-miles">
                  {OFFER_LABEL[o.type] ?? "Offer"}{o.estimated_saving_inr ? ` · ${fmtINR(o.estimated_saving_inr)}` : ""}
                </span>
                <span role="tooltip" id={`${tip}-${i}`}
                  className="pointer-events-none absolute bottom-full left-0 z-20 mb-2 w-56 rounded border-2 border-black bg-comic p-2 text-xs text-miles opacity-0 transition group-hover:opacity-100 group-focus-within:opacity-100">
                  {o.text}
                </span>
              </li>
            ))}
          </ul>
        )}

        {specs.length > 0 && (
          <div>
            <ul className="flex flex-wrap gap-1.5" aria-label="Specifications">
              {visible.map(([k, v]) => (
                <li key={k} className="rounded border border-black/40 px-2 py-0.5 text-xs dark:border-white/40"><b>{k}:</b> {v}</li>
              ))}
            </ul>
            {specs.length > 4 && (
              <button type="button" onClick={() => setShowAll((s) => !s)} className="mt-1 text-xs font-semibold underline">
                {showAll ? "Show less" : `Show all ${specs.length}`}
              </button>
            )}
          </div>
        )}

        <div className="flex flex-wrap gap-1 text-xs">
          {!p.in_stock && <span className="chip bg-spidey text-white">Out of stock</span>}
          {!p.verified && <span className="chip bg-comic text-miles">Google price · unverified</span>}
          {p.stale && <span className="chip bg-comic text-miles">Last known price</span>}
          {p.source === "demo" && <span className="chip bg-venom text-white">Demo</span>}
        </div>
        <ComicLink href={redirectUrl(p)} target="_blank" rel="noopener noreferrer" className="mt-auto w-full" size="md"
          aria-label={`Go to ${storeLabel(p.site)} for ${p.name} (opens in new tab)`}>
          GO TO {storeLabel(p.site).toUpperCase()} ➜
        </ComicLink>
      </div>
    </motion.article>
  );
}