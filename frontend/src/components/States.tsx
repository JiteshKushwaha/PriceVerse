import { useEffect, useState } from "react";
import type { SiteStatus } from "../types";
import type { ApiError } from "../lib/api";
import { storeLabel } from "../lib/format";
import { ComicButton, ComicPanel, StarBurst } from "./comic";

export function IdleState() {
  return (
    <ComicPanel caption="Panel 1" className="text-center">
      <p className="headline mt-4 text-3xl">YOUR STORY STARTS HERE</p>
      <p className="mt-2">Type a product above and hit <b>SWING!</b> to compare prices across stores.</p>
    </ComicPanel>
  );
}

export function EmptyState({ onRetry }: { onRetry: () => void }) {
  return (
    <ComicPanel caption="Uh-oh" className="text-center">
      <StarBurst size={90} color="#FF2E93" className="mx-auto mt-2">?!</StarBurst>
      <p className="headline mt-3 text-3xl">NO WEBS HERE!</p>
      <p className="mt-2">We couldn't find matching products. Try a simpler name, like "iphone 15" or "boat airdopes".</p>
      <ComicButton variant="yellow" className="mt-4" onClick={onRetry}>TRY AGAIN</ComicButton>
    </ComicPanel>
  );
}

export function ErrorState({ error, onRetry }: { error: ApiError | null; onRetry: () => void }) {
  const [left, setLeft] = useState(error?.retryAfter ?? 0);
  useEffect(() => {
    setLeft(error?.retryAfter ?? 0);
    if (!error?.retryAfter) return;
    const t = setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [error]);

  const is429 = error?.status === 429;
  const offline = error?.status === 0;
  return (
    <ComicPanel caption={is429 ? "Rate limit" : offline ? "Server offline" : "Error"} className="text-center">
      <p className="headline mt-4 text-3xl">
        {is429 ? "SLOW DOWN, HERO!" : offline ? "SERVER OFFLINE" : "SOMETHING WENT WRONG"}
      </p>
      <p className="mt-2" role="alert">
        {is429 ? `Try again in ${left} s.` : offline ? "Couldn't reach the backend. Is the API running and VITE_API_BASE_URL correct?" : error?.message}
      </p>
      <ComicButton variant="cyan" className="mt-4" disabled={is429 && left > 0} onClick={onRetry}>RETRY</ComicButton>
    </ComicPanel>
  );
}

export function BlockedChips({ sites, onRetry }: { sites: SiteStatus[]; onRetry: () => void }) {
  const bad = sites.filter((s) => ["blocked", "timeout", "error"].includes(s.status));
  if (bad.length === 0) return null;
  return (
    <div className="panel flex flex-wrap items-center gap-2 p-3 text-sm" role="status">
      <span className="font-display text-lg tracking-wide text-spidey">VILLAIN INTERFERENCE:</span>
      {bad.map((s) => (
        <span key={s.site} className="chip bg-spidey/15 px-2.5 py-1" title={s.error ?? ""}>
          {storeLabel(s.site)} · {s.status}{s.result_count ? ` (showing ${s.message?.includes("stale") ? "last known" : "Google"} price)` : ""}
        </span>
      ))}
      <button type="button" onClick={onRetry} className="chip ml-auto bg-comic px-3 py-1 text-miles">↻ Retry</button>
    </div>
  );
}

export function DemoBanner() {
  return (
    <div className="flex items-center gap-3 rounded-md border-[3px] border-black bg-venom p-3 text-white shadow-comic-sm" role="status">
      <StarBurst size={56} color="#FFD60A">DEMO</StarBurst>
      <p className="text-sm font-semibold">
        <b className="font-display text-lg tracking-wider">DEMO DATA</b>: live stores were unavailable or demo mode is on. Prices are simulated; links open real store searches.
      </p>
    </div>
  );
}