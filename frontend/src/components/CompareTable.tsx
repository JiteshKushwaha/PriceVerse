import { useMemo } from "react";
import type { Product } from "../types";
import { redirectUrl } from "../lib/api";
import { deliveryLabel, fmtINR, OFFER_LABEL, storeLabel } from "../lib/format";
import { Stars } from "./ProductCard";

export function CompareTable({ results }: { results: Product[] }) {
  const rows = useMemo(() => {
    const m = new Map<string, Product>();
    results.forEach((p) => {
      const c = m.get(p.site);
      if (!c || p.price < c.price) m.set(p.site, p);
    });
    return [...m.values()].sort((a, b) => a.price - b.price);
  }, [results]);
  const min = rows[0]?.price;
  return (
    <div className="panel max-h-[70vh] overflow-auto">
      <table className="w-full min-w-[880px] border-collapse text-left text-sm">
        <caption className="sr-only">Lowest price per store</caption>
        <thead className="sticky top-0 z-10 bg-miles text-paper">
          <tr>
            {["Store", "Product", "Price", "Discount", "Offers", "Delivery", "Rating", ""].map((h) => (
              <th key={h} scope="col" className="px-3 py-3 font-caption text-base font-bold uppercase">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.id} className="border-t-2 border-black/20 align-top dark:border-white/20">
              <th scope="row" className="px-3 py-3 font-caption text-base font-bold uppercase">{storeLabel(p.site)}</th>
              <td className="max-w-[260px] px-3 py-3"><span className="line-clamp-2" title={p.name}>{p.name}</span></td>
              <td className={`px-3 py-3 font-mono text-base font-bold ${p.price === min ? "bg-electric text-miles" : ""}`}>
                {fmtINR(p.price)}{p.price === min && <span className="block font-caption text-xs">LOWEST</span>}
              </td>
              <td className="px-3 py-3">{p.discount_percent ? `${p.discount_percent}% (${fmtINR(p.discount_amount)})` : "—"}</td>
              <td className="px-3 py-3">
                {p.offers.length ? p.offers.slice(0, 2).map((o, i) => <span key={i} className="block" title={o.text}>{OFFER_LABEL[o.type] ?? "Offer"}</span>) : "—"}
              </td>
              <td className="px-3 py-3">{deliveryLabel(p)}</td>
              <td className="px-3 py-3">{p.rating != null ? <Stars rating={p.rating} count={p.review_count} /> : "—"}</td>
              <td className="px-3 py-3">
                <a href={redirectUrl(p)} target="_blank" rel="noopener noreferrer"
                  className="inline-block whitespace-nowrap rounded border-[3px] border-black bg-spidey px-3 py-1.5 font-display tracking-wider text-white shadow-comic-sm active:translate-y-0.5">
                  GO ➜
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}