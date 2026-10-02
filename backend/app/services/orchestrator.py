import asyncio
import logging
import random
import time
from datetime import datetime
from typing import Awaitable, Callable
from zoneinfo import ZoneInfo

from app.config import settings
from app.core.cache import cache
from app.core.logging import log
from app.models.schemas import Product, QueryInfo, ScraperResult, SiteStatus
from app.scrapers import registry
from app.services import demo_data, google_search, history
from app.services.processing import process_site
from app.services.query_normalizer import normalize
from app.services.ranking import rank

logger = logging.getLogger("orchestrator")
Progress = Callable[[str, dict], Awaitable[None]] | None
IST = ZoneInfo("Asia/Kolkata")
FRIENDLY = {"blocked": "Villain interference: this store blocked us", "timeout": "Store took too long, skipped",
            "error": "Something broke while reading this store", "empty": "No matching products found"}


async def _emit(progress: Progress, event: str, data: dict) -> None:
    if progress:
        try:
            await progress(event, data)
        except Exception:
            pass


def _status(site: str, status: str, products: list[Product], duration: int, error: str | None, msg: str | None = None) -> SiteStatus:
    return SiteStatus(site=site, status=status, duration_ms=duration, error=error,
                      message=msg or (None if status == "ok" else FRIENDLY.get(status)),
                      min_price=min((p.price for p in products), default=None), result_count=len(products))


async def _finalize(r: ScraperResult, q: QueryInfo, qh: str, hints: dict) -> tuple[SiteStatus, list[Product]]:
    products = process_site(r.site, r.items, q, settings.results_per_site)
    lastgood_key = f"lastgood:v1:{r.site}:{qh}"
    if products:
        await cache.set_json(lastgood_key, [p.model_dump() for p in products], 7 * 86400)
        return _status(r.site, "ok", products, r.duration_ms, None), products
    status = r.status if r.status != "ok" else "empty"
    if hints.get(r.site):  # (b) Google snippet fallback
        products = process_site(r.site, hints[r.site], q, 3)
        if products:
            return _status(r.site, status, products, r.duration_ms, r.error, "Showing Google price (unverified)"), products
    if last := await cache.get_json(lastgood_key):  # (c) stale cache fallback
        products = [Product(**{**p, "stale": True}) for p in last]
        return _status(r.site, status, products, r.duration_ms, r.error, "Showing last known price (stale)"), products
    return _status(r.site, status, [], r.duration_ms, r.error), []


async def _demo(q: QueryInfo, progress: Progress) -> tuple[list[SiteStatus], list[Product]]:
    sites, products = [], []
    raw = demo_data.generate_items(q.clean)
    for site in raw:
        await _emit(progress, "site", SiteStatus(site=site, status="searching").model_dump())
    for site, items in raw.items():
        await asyncio.sleep(random.uniform(0.15, 0.5))  # make the loading panels visible
        ps = process_site(site, items, q, settings.results_per_site, relevance=False)
        st = _status(site, "ok", ps, random.randint(900, 4000), None)
        sites.append(st)
        products += ps
        await _emit(progress, "site", st.model_dump())
    return sites, products


async def _live(q: QueryInfo, qh: str, progress: Progress) -> tuple[list[SiteStatus], list[Product]]:
    scrapers = registry.enabled()
    for s in scrapers:
        await _emit(progress, "site", SiteStatus(site=s.domain, status="searching").model_dump())
    hints = await google_search.discover(q.clean)
    sem = asyncio.Semaphore(settings.max_concurrency)

    async def run_one(s) -> ScraperResult:
        async with sem:
            try:
                return await asyncio.wait_for(s.search(q, settings.results_per_site), settings.scraper_timeout)
            except asyncio.TimeoutError:
                return ScraperResult(site=s.domain, status="timeout", error="timeout: per-scraper limit",
                                     duration_ms=int(settings.scraper_timeout * 1000))

    tasks = {asyncio.create_task(run_one(s)): s for s in scrapers}
    pending = set(tasks)
    loop = asyncio.get_running_loop()
    deadline = loop.time() + settings.global_timeout
    sites, products = [], []
    while pending:
        remaining = deadline - loop.time()
        if remaining <= 0:
            break
        done, pending = await asyncio.wait(pending, timeout=remaining, return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            s = tasks[t]
            try:
                r = t.result()
            except Exception as exc:
                r = ScraperResult(site=s.domain, status="error", error=f"unexpected: {exc}")
            st, ps = await _finalize(r, q, qh, hints)
            sites.append(st)
            products += ps
            await _emit(progress, "site", st.model_dump())
    for t in pending:
        t.cancel()
        st, ps = await _finalize(ScraperResult(site=tasks[t].domain, status="timeout", error="timeout: global limit",
                                               duration_ms=int(settings.global_timeout * 1000)), q, qh, hints)
        sites.append(st)
        products += ps
        await _emit(progress, "site", st.model_dump())
    return sites, products


async def _execute(q: QueryInfo, qh: str, progress: Progress) -> dict:
    demo = settings.demo_mode
    if demo:
        sites, products = await _demo(q, progress)
    else:
        sites, products = await _live(q, qh, progress)
        if not products:  # automatic demo fallback: all live scrapers failed
            log(logger, logging.WARNING, "all scrapers failed, demo fallback", query=q.clean)
            demo = True
            sites, products = await _demo(q, progress)
    ranked, summary = rank(products)
    return {"query": q.model_dump(), "cached": False, "cached_at": None, "demo": demo,
            "generated_at": datetime.now(IST).isoformat(timespec="seconds"), "took_ms": 0,
            "sites": [s.model_dump() for s in sites], "results": [p.model_dump() for p in ranked], "summary": summary}

async def run_search(raw: str, progress: Progress = None, fresh: bool = False) -> dict:
    t0 = time.perf_counter()
    q = normalize(raw)
    qh = history.qhash(q.clean)
    key = f"search:v1:{qh}"

    async def from_cache() -> dict | None:
        hit = await cache.get_json(key)
        if hit:
            hit["cached"] = True
            for s in hit["sites"]:
                await _emit(progress, "site", s)
        return hit

    if not fresh and (hit := await from_cache()):
        return hit
    async with cache.lock(key) as owner:
        if not owner:
            for _ in range(int(settings.global_timeout * 2) + 10):
                await asyncio.sleep(0.5)
                if hit := await from_cache():
                    return hit
        resp = await _execute(q, qh, progress)
        resp["took_ms"] = int((time.perf_counter() - t0) * 1000)
        resp["cached_at"] = resp["generated_at"]
        await cache.set_json(key, resp, settings.cache_ttl_seconds)
    try:
        await history.save_points(qh, q.clean, [Product(**p) for p in resp["results"]])
    except Exception as exc:
        log(logger, logging.WARNING, "history save failed", error=str(exc))
    return resp