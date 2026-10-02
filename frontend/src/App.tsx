import { useEffect, useMemo } from "react";
import toast from "react-hot-toast";
import { useQueryParam } from "./hooks/useQueryParam";
import { useSearchStream } from "./hooks/useSearchStream";
import { applyFilters, useUI } from "./store";
import { Navbar } from "./components/Navbar";
import { Hero } from "./components/Hero";
import { StoreProgress } from "./components/StoreProgress";
import { SummaryCards } from "./components/SummaryCards";
import { FilterBar } from "./components/FilterBar";
import { ProductCard } from "./components/ProductCard";
import { CompareTable } from "./components/CompareTable";
import { PriceChart } from "./components/PriceChart";
import { Spotlight } from "./components/Spotlight";
import { BlockedChips, DemoBanner, EmptyState, ErrorState, IdleState } from "./components/States";
import { About, HowItWorks } from "./components/Sections";
import { Footer } from "./components/Footer";
import { ComicPanel, SectionTitle, ZigZag } from "./components/comic";

export default function App() {
  const [q, setQ] = useQueryParam();
  const search = useSearchStream(q);
  const theme = useUI((s) => s.theme);
  const view = useUI((s) => s.view);
  const filters = useUI((s) => s.filters);
  const resetFilters = useUI((s) => s.resetFilters);

  useEffect(() => { document.documentElement.classList.toggle("dark", theme === "dark"); }, [theme]);
  useEffect(() => {
    if (search.error) toast.error(search.error.status === 429 ? "Rate limit hit. Slow down, hero!" : search.error.message);
  }, [search.error]);

  const data = search.data;
  const results = useMemo(() => data?.results ?? [], [data]);
  const filtered = useMemo(() => applyFilters(results, filters), [results, filters]);

  const onSearch = (v: string) => {
    resetFilters();
    setQ(v);
    setTimeout(() => document.getElementById("compare")?.scrollIntoView({ behavior: "smooth" }), 60);
  };

  return (
    <>
      <a href="#compare" className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:bg-comic focus:p-2 focus:text-miles">Skip to results</a>
      <Navbar />
      <main>
        <Hero initial={q} onSearch={onSearch} busy={search.phase === "loading"} />
        <ZigZag />

        <section id="compare" aria-labelledby="compare-title" className="mx-auto max-w-[1200px] scroll-mt-28 space-y-8 px-4 py-14">
          <SectionTitle id="compare-title" kicker={q ? `Searching: "${q}"` : "Compare"} title="THE DEAL HUNT" />
          {search.phase === "idle" && <IdleState />}
          {search.phase === "loading" && <StoreProgress sites={search.sites} />}
          {search.phase === "error" && <ErrorState error={search.error} onRetry={search.retry} />}
          {search.phase === "done" && data && (data.results.length === 0 ? <EmptyState onRetry={search.retry} /> : (
            <>
              {data.demo && <DemoBanner />}
              <p className="font-mono text-xs opacity-80">
                {data.cached ? "⚡ Served from cache" : `Fetched live in ${(data.took_ms / 1000).toFixed(1)} s`} · {data.results.length} products · {data.sites.length} stores
              </p>
              <BlockedChips sites={data.sites} onRetry={search.retry} />
              <SummaryCards data={data} />
              <FilterBar results={results} shown={filtered.length} />
              {filtered.length === 0 ? (
                <ComicPanel caption="Filters"><p className="mt-2">No products match these filters. Try resetting them.</p></ComicPanel>
              ) : view === "grid" ? (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {filtered.map((p, i) => <ProductCard key={p.id} p={p} index={i} />)}
                </div>
              ) : (
                <CompareTable results={filtered} />
              )}
              <div>
                <SectionTitle kicker="Top picks" title="RECOMMENDED SPOTLIGHT" />
                <Spotlight results={results} />
              </div>
            </>
          ))}
        </section>

        <section id="history" aria-labelledby="history-title" className="relative scroll-mt-28 border-y-[3px] border-black bg-navy py-14 text-paper">
          <div className="mx-auto max-w-[1200px] px-4">
            <SectionTitle id="history-title" kicker="Price insights" title="THE PRICE MULTIVERSE" />
            {data && data.results.length > 0
              ? <PriceChart data={data} q={data.query.clean} />
              : <p>Run a search to see the lowest price per store and a price-history chart.</p>}
          </div>
        </section>

        <HowItWorks />
        <About />
      </main>
      <Footer />

    </>
    
  );

}