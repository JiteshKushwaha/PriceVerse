import { ThemeToggle, WebLogo } from "./comic";

const LINKS: [string, string][] = [
  ["Home", "#home"], ["How it works", "#how"], ["Compare", "#compare"], ["History", "#history"], ["About", "#about"],
];

function Links({ className = "" }: { className?: string }) {
  return (
    <ul className={`flex gap-1 rounded-full border-[3px] border-black bg-white dark:bg-navy px-2 py-1 ${className}`}>
      {LINKS.map(([label, href]) => (
        <li key={href}>
          <a href={href} className="web-underline block whitespace-nowrap px-3 py-1 font-caption font-bold uppercase text-sm rounded-full hover:text-spidey dark:hover:text-electric">
            {label}
          </a>
        </li>
      ))}
    </ul>
  );
}

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b-[3px] border-black bg-paper/95 dark:bg-miles/95 backdrop-blur">
      <div className="mx-auto flex max-w-[1200px] items-center gap-3 px-4 py-2">
        <a href="#home" className="flex min-w-0 items-center gap-2" aria-label="PriceVerse home">
          <WebLogo className="h-10 w-10 shrink-0" />
          <span className="min-w-0 leading-tight">
            <span className="font-display text-2xl tracking-wider">PRICE<span className="text-spidey">VERSE</span></span>
            <span className="block truncate font-caption text-[11px] font-bold uppercase opacity-80">
              E-Commerce Price Comparison &amp; Product Recommendation System
            </span>
          </span>
        </a>
        <nav aria-label="Main" className="ml-auto hidden md:block"><Links /></nav>
        <div className="ml-auto md:ml-0"><ThemeToggle /></div>
      </div>
      <nav aria-label="Main mobile" className="overflow-x-auto px-4 pb-2 md:hidden"><Links className="w-max" /></nav>
    </header>
  );
}