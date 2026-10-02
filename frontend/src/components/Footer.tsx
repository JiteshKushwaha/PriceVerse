const STACK = ["FastAPI", "Playwright", "httpx", "Redis", "SQLAlchemy", "pandas", "React", "Tailwind", "Framer Motion", "Recharts"];
export function Footer() {
  return (
    <footer className="border-t-[3px] border-black bg-miles text-paper">
      <div className="zigzag" aria-hidden="true" />
      <div className="mx-auto max-w-[1200px] px-4 py-10">
        <p className="font-display text-2xl tracking-wider">Made with <span className="text-spidey">❤</span> for Data Engineering Honours: Web Scraping &amp; APIs</p>
        <p className="mt-2 max-w-3xl text-sm opacity-90">
          Disclaimer: prices, offers and delivery dates change often and may differ from what is shown. Always check on the store's site before buying.
          This project is not affiliated with any store or with Marvel/Sony; the comic style is original and only inspired by them.
        </p>
        <ul className="mt-4 flex flex-wrap gap-2" aria-label="Tech stack">
          {STACK.map((s) => <li key={s} className="chip border-paper/70 text-paper">{s}</li>)}
        </ul>
      </div>
    </footer>
  );
}