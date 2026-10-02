import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useRecent } from "../hooks/useRecent";
import { STORES } from "../lib/format";
import { ComicButton, HalftoneBg, StarBurst } from "./comic";

const EXAMPLES = ["iPhone 15 128GB", "boAt Airdopes 141", "Nike Air Max shoes", "Sony WH-1000XM5", "MacBook Air M2"];
const QUICK: [string, string][] = [["iPhone 15", "iphone 15"], ["Sneakers", "adidas sneakers"], ["Laptop", "hp laptop"], ["Headphones", "sony wh-1000xm5"]];

function MaskArt() {
  return (
    <svg viewBox="0 0 200 240" className="h-full w-full drop-shadow-[8px_8px_0_#000]" aria-hidden="true">
      <defs>
        <pattern id="web" width="22" height="22" patternUnits="userSpaceOnUse">
          <path d="M0 11h22M11 0v22" stroke="#E23636" strokeWidth="1.5" opacity=".9" />
        </pattern>
        <clipPath id="head"><path d="M100 8C45 8 18 60 22 120c4 62 40 110 78 112 38-2 74-50 78-112C182 60 155 8 100 8z" /></clipPath>
      </defs>
      <path d="M100 8C45 8 18 60 22 120c4 62 40 110 78 112 38-2 74-50 78-112C182 60 155 8 100 8z" fill="#0B0B12" />
      <rect width="200" height="240" fill="url(#web)" clipPath="url(#head)" />
      <path d="M100 8C45 8 18 60 22 120c4 62 40 110 78 112 38-2 74-50 78-112C182 60 155 8 100 8z" fill="none" stroke="#000" strokeWidth="7" />
      <path d="M38 102c20-8 44 0 54 28-24 9-48 2-54-28z" fill="#F7F3E8" stroke="#000" strokeWidth="6" />
      <path d="M162 102c-20-8-44 0-54 28 24 9 48 2 54-28z" fill="#F7F3E8" stroke="#000" strokeWidth="6" />
    </svg>
  );
}

export function Hero({ initial, onSearch, busy }: { initial: string; onSearch: (q: string) => void; busy: boolean }) {
  const [value, setValue] = useState(initial);
  const [debounced, setDebounced] = useState(initial);
  const [ph, setPh] = useState(0);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const { recent, add } = useRecent();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => setValue(initial), [initial]);
  useEffect(() => {
    const t = setInterval(() => setPh((i) => (i + 1) % EXAMPLES.length), 2600);
    return () => clearInterval(t);
  }, []);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), 200);
    return () => clearTimeout(t);
  }, [value]);

  const suggestions = useMemo(() => {
    const v = debounced.trim().toLowerCase();
    return Array.from(new Set([...recent, ...EXAMPLES])).filter((s) => !v || s.toLowerCase().includes(v)).slice(0, 6);
  }, [debounced, recent]);

  const submit = (q: string) => {
    const v = q.trim();
    if (v.length < 2) { toast.error("Type at least 2 characters, hero!"); return; }
    if (v.length > 100) { toast.error("Keep it under 100 characters."); return; }
    add(v);
    setValue(v);
    setOpen(false);
    onSearch(v);
  };

  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!open || suggestions.length === 0) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((i) => (i + 1) % suggestions.length); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((i) => (i <= 0 ? suggestions.length - 1 : i - 1)); }
    else if (e.key === "Escape") setOpen(false);
    else if (e.key === "Enter" && active >= 0) { e.preventDefault(); submit(suggestions[active]); }
  };

  return (
    <section id="home" className="relative overflow-hidden scroll-mt-28">
      <div aria-hidden="true" className="sunburst absolute -inset-[50%] animate-[spin_120s_linear_infinite] motion-reduce:animate-none" />
      <HalftoneBg />
      <div className="relative mx-auto grid max-w-[1200px] items-center gap-8 px-4 py-14 md:grid-cols-[1.4fr_1fr] md:py-20">
        <div>
          <motion.div initial={{ scale: 0.6, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", stiffness: 260, damping: 16 }}>
            <span className="caption text-sm">Issue #1 · The Hunt for the Best Deal</span>
            <h1 className="headline mt-4 text-5xl leading-[0.95] sm:text-7xl">SWING TO THE<br /><span className="text-spidey">BEST PRICE!</span></h1>
          </motion.div>
          <p className="mt-5 max-w-xl text-base sm:text-lg">
            Type any product. We search Amazon, Flipkart, Myntra, Croma and more at the same time,
            compare prices, offers and delivery, then point you to the best deal.
          </p>

          <form role="search" className="relative mt-6" onSubmit={(e) => { e.preventDefault(); submit(value); }}>
            <label htmlFor="q" className="sr-only">Search a product</label>
            <div className="flex flex-col gap-3 rounded-md border-[3px] border-black bg-comic p-2 shadow-comic sm:flex-row">
              <input
                id="q" ref={inputRef} value={value} maxLength={100} autoComplete="off"
                role="combobox" aria-expanded={open} aria-controls="suggestions" aria-autocomplete="list"
                aria-activedescendant={active >= 0 ? `sug-${active}` : undefined}
                onChange={(e) => { setValue(e.target.value); setOpen(true); setActive(-1); }}
                onFocus={() => setOpen(true)} onBlur={() => setTimeout(() => setOpen(false), 120)} onKeyDown={onKey}
                placeholder={`Try "${EXAMPLES[ph]}"`}
                className="min-w-0 flex-1 rounded border-2 border-black bg-white px-4 py-3 font-caption text-xl font-bold text-miles placeholder:text-miles/50"
              />
              <ComicButton type="submit" size="lg" disabled={busy} aria-label="Search">
                {busy ? "SWINGING…" : "SWING! 🕸️"}
              </ComicButton>
            </div>
            {open && suggestions.length > 0 && (
              <ul id="suggestions" role="listbox" className="absolute left-0 right-0 top-full z-30 mt-2 overflow-hidden rounded-md border-[3px] border-black bg-white text-miles shadow-comic">
                {suggestions.map((s, i) => (
                  <li key={s} id={`sug-${i}`} role="option" aria-selected={i === active}
                    onMouseDown={(e) => { e.preventDefault(); submit(s); }}
                    className={`cursor-pointer px-4 py-2 font-caption text-lg font-bold ${i === active ? "bg-electric" : "hover:bg-paper"}`}>
                    {recent.includes(s) ? "↺ " : "🔎 "}{s}
                  </li>
                ))}
              </ul>
            )}
          </form>

          <div className="mt-5 flex flex-wrap items-center gap-2">
            <span className="font-caption font-bold uppercase text-sm">Quick picks:</span>
            {QUICK.map(([label, q]) => (
              <button key={q} type="button" onClick={() => submit(q)}
                className="chip bg-white text-miles hover:bg-electric px-3 py-1 text-sm shadow-comic-sm">{label}</button>
            ))}
          </div>
          <ul className="mt-6 flex flex-wrap gap-2" aria-label="Stores we compare">
            {Object.entries(STORES).map(([site, s]) => (
              <li key={site} className="chip flex items-center gap-1.5 bg-white text-miles dark:bg-navy dark:text-paper">
                <span className="h-2.5 w-2.5 rounded-full border border-black" style={{ background: s.color }} aria-hidden="true" />{s.label}
              </li>
            ))}
          </ul>
        </div>
        <div className="relative mx-auto hidden h-80 w-64 md:block">
          <MaskArt />
          <StarBurst className="absolute -left-10 top-4 rotate-[-12deg]" size={96} color="#FF2E93">POW!</StarBurst>
          <StarBurst className="absolute -right-8 bottom-6 rotate-[10deg]" size={88} color="#00E5FF">THWIP!</StarBurst>
        </div>
      </div>
    </section>
  );
}