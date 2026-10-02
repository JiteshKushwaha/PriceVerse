export interface Offer { type: string; text: string; estimated_saving_inr: number | null }
export interface Delivery { text: string | null; estimated_date: string | null; estimated_days: number | null; free: boolean }
export interface Product {
  id: string; site: string; name: string; image_url: string | null; specs: Record<string, string>;
  price: number; mrp: number | null; currency: string; discount_percent: number | null; discount_amount: number | null;
  offers: Offer[]; delivery: Delivery; rating: number | null; review_count: number | null; in_stock: boolean;
  sponsored: boolean; url: string; score: number; badges: string[]; source: string; verified: boolean; stale: boolean;
}
export type SiteState = "searching" | "ok" | "empty" | "blocked" | "timeout" | "error";
export interface SiteStatus {
  site: string; status: SiteState; duration_ms: number; error: string | null; message: string | null;
  min_price: number | null; result_count: number;
}
export interface QueryInfo { raw: string; clean: string; brand: string | null; tokens: string[]; attributes: Record<string, string> }
export interface Summary {
  cheapest?: { id: string; site: string; price: number };
  best_deal?: { id: string; site: string; price: number; score: number; reason: string };
  fastest_delivery?: { id: string; site: string; price: number; days: number } | null;
  highest_rated?: { id: string; site: string; rating: number } | null;
  savings_vs_highest?: { inr: number; percent: number };
  explanation?: string;
}
export interface SearchResponse {
  query: QueryInfo; cached: boolean; cached_at: string | null; demo: boolean; generated_at: string; took_ms: number;
  sites: SiteStatus[]; results: Product[]; summary: Summary;}
export interface SiteInfo { name: string; site: string; label: string; needs_browser: boolean; mode: string }
export interface HistoryPoint { date: string; min_price: number; avg_price: number; synthetic: boolean }
export type SortKey = "recommended" | "price" | "discount" | "rating" | "delivery";