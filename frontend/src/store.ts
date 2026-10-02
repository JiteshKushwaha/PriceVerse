import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Product, SortKey } from "./types";

export interface Filters {
  sort: SortKey; stores: string[]; maxPrice: number | null; inStock: boolean; freeDelivery: boolean;
}
export const DEFAULT_FILTERS: Filters = { sort: "recommended", stores: [], maxPrice: null, inStock: false, freeDelivery: false };

interface UIState {
  theme: "dark" | "light";
  view: "grid" | "table";
  filters: Filters;
  toggleTheme: () => void;
  setView: (v: "grid" | "table") => void;
  setFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  toggleStore: (site: string) => void;
  resetFilters: () => void;
}

export const useUI = create<UIState>()(
  persist(
    (set) => ({
      theme: "dark",
      view: "grid",
      filters: DEFAULT_FILTERS,
      toggleTheme: () => set((s) => ({ theme: s.theme === "dark" ? "light" : "dark" })),
      setView: (view) => set({ view }),
      setFilter: (key, value) => set((s) => ({ filters: { ...s.filters, [key]: value } })),
      toggleStore: (site) =>
        set((s) => ({
          filters: {
            ...s.filters,
            stores: s.filters.stores.includes(site) ? s.filters.stores.filter((x) => x !== site) : [...s.filters.stores, site],
          },
        })),
      resetFilters: () => set({ filters: DEFAULT_FILTERS }),
    }),
    { name: "priceverse-ui", partialize: (s) => ({ theme: s.theme, view: s.view }) },
  ),
);

const SORTERS: Record<SortKey, (a: Product, b: Product) => number> = {
  recommended: (a, b) => b.score - a.score,
  price: (a, b) => a.price - b.price,
  discount: (a, b) => (b.discount_percent ?? 0) - (a.discount_percent ?? 0),
  rating: (a, b) => (b.rating ?? 0) - (a.rating ?? 0),
  delivery: (a, b) => (a.delivery.estimated_days ?? 99) - (b.delivery.estimated_days ?? 99),
};
export function applyFilters(list: Product[], f: Filters): Product[] {
  return list
    .filter((p) =>
      (f.stores.length === 0 || f.stores.includes(p.site)) &&
      (f.maxPrice == null || p.price <= f.maxPrice) &&
      (!f.inStock || p.in_stock) &&
      (!f.freeDelivery || p.delivery.free))
    .sort(SORTERS[f.sort]);
}