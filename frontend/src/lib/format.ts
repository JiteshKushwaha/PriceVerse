import type { Product } from "../types";

const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
export const fmtINR = (n: number | null | undefined) => (n == null ? "—" : inr.format(n));

export const STORES: Record<string, { label: string; color: string }> = {
  "amazon.in": { label: "Amazon", color: "#FF9900" },
  "flipkart.com": { label: "Flipkart", color: "#2874F0" },
  "myntra.com": { label: "Myntra", color: "#FF3F6C" },
  "croma.com": { label: "Croma", color: "#12DAA8" },
  "reliancedigital.in": { label: "Reliance Digital", color: "#E42529" },
  "ajio.com": { label: "AJIO", color: "#5A7A8C" },
  "snapdeal.com": { label: "Snapdeal", color: "#E40046" },
  "tatacliq.com": { label: "Tata CLiQ", color: "#DA1C5C" },
};
export const storeLabel = (s: string) => STORES[s]?.label ?? s;
export const storeColor = (s: string) => STORES[s]?.color ?? "#7B2FF7";

export const BADGE_LABEL: Record<string, string> = {
  CHEAPEST: "CHEAPEST", BEST_DEAL: "BEST DEAL", FASTEST: "FASTEST", TOP_RATED: "TOP RATED",
};
export const OFFER_LABEL: Record<string, string> = {
  bank: "Bank offer", emi: "No-cost EMI", exchange: "Exchange", coupon: "Coupon", cashback: "Cashback", other: "Offer",
};

export function deliveryLabel(p: Product): string {
  const d = p.delivery;
  if (d.estimated_days == null) return d.text ?? "Delivery info on store";
  const when = d.estimated_days === 0 ? "today" : d.estimated_days === 1 ? "tomorrow" : `in ${d.estimated_days} days`;
  return `${d.free ? "FREE delivery" : "Delivery"} ${when}`;}