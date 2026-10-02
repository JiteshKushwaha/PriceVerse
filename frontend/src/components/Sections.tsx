import { ComicPanel, SectionTitle } from "./comic";

const STEPS = [
  ["Normalize", "We clean your query and detect the brand, storage, colour and size."],
  ["Discover", "Google Shopping (SerpAPI) or Custom Search hints at where the product lives."],
  ["Scrape", "Eight store adapters run in parallel with Playwright or httpx, politely rate-limited."],
  ["Clean", "Prices, offers, delivery and ratings are parsed. Accessories and duplicates are dropped."],
  ["Rank", "Score = 45% price, 20% discount, 15% rating, 10% delivery, 10% trust."],
];

export function HowItWorks() {
  return (
    <section id="how" className="brick relative scroll-mt-28 py-16 text-paper">
      <div className="mx-auto max-w-[1200px] px-4">
        <SectionTitle kicker="Origin story" title="HOW IT WORKS" />
        <ol className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {STEPS.map(([t, d], i) => (
            <li key={t}>
              <ComicPanel caption={`Step ${i + 1}`} className="h-full">
                <p className="mt-3 font-display text-2xl tracking-wide">{t}</p>
                <p className="mt-1 text-sm">{d}</p>
              </ComicPanel>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

export function About() {
  return (
    <section id="about" className="mx-auto max-w-[1200px] scroll-mt-28 px-4 py-16">
      <SectionTitle kicker="Behind the mask" title="ABOUT THIS PROJECT" />
      <div className="grid gap-6 md:grid-cols-2">
        <ComicPanel>
          <p><b>PriceVerse</b> is an academic Data Engineering Honours project (Web Scraping &amp; APIs). It shows a full data pipeline:
            discovery through APIs, concurrent scraping, extraction from JSON-LD/state/XHR/CSS, normalization, validation, ranking,
            caching, rate limiting and persistence.</p>
        </ComicPanel>
        <ComicPanel>
          <p>Scraping is for demonstration only. Store layouts change, and stores may block automated traffic. The app never solves CAPTCHAs.
            It falls back to Google hints, the last known prices, or clearly labelled demo data. For production, use the official affiliate or product APIs.</p>
        </ComicPanel>
      </div>
    </section>
  );
}