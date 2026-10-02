import asyncio
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser, Node
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from app.config import settings
from app.core.errors import BlockedError, NetworkError, ParseError, ScrapeTimeout, ScraperError
from app.core.logging import log
from app.core.rate_limit import domain_limiter
from app.models.schemas import QueryInfo, ScraperResult
from app.scrapers.anti_bot import browser_headers, detect_block, pick_proxy, scraper_api_url
from app.scrapers.browser_pool import FetchResult, browser_pool

logger = logging.getLogger("scraper")
NAME_KEYS = ("name", "productName", "productname", "title", "displayName")
PRICE_KEYS = ("price", "sellingPrice", "winningSellerPrice", "offerPrice", "discountedPrice", "finalPrice", "sp")
MRP_KEYS = ("mrp", "mrpPrice", "wasPriceData", "listPrice", "originalPrice", "strikePrice")
URL_KEYS = ("url", "landingPageUrl", "webURL", "productUrl", "pdpUrl", "link")
IMG_KEYS = ("image", "imageURL", "searchImage", "plpImage", "imageUrl", "thumbnail")

def num(v: Any) -> float | None:
    """Pulls a number out of nested price structures like {'value': 999} or '₹999'."""
    from app.utils.price import parse_price
    if isinstance(v, dict):
        for k in ("value", "doubleValue", "amount", "formattedValue", "price", "decimalValue"):
            if k in v:
                return num(v[k])
        return None
    if isinstance(v, list) and v:
        return num(v[0])
    return parse_price(v)

def first_key(d: dict, keys: tuple[str, ...]) -> Any:
    for k in keys:
        if d.get(k) not in (None, "", [], {}):
            return d[k]
    return None

def pick(node: Node, selectors: list[str]) -> str | None:
    """Selector syntax: 'css' -> text, 'css@attr' -> attribute, '@attr' -> attribute of node itself."""
    for s in selectors:
        css, _, attr = s.partition("@")
        target = node.css_first(css) if css else node
        if target is None:
            continue
        val = target.attributes.get(attr) if attr else target.text(strip=True)
        if val and val.strip():
            return val.strip()
    return None

def parse_jsonld(html: str, base: str) -> list[dict]:
    out: list[dict] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, list):
            for o in obj:
                walk(o)
        elif isinstance(obj, dict):
            t = obj.get("@type")
            types = t if isinstance(t, list) else [t]
            if "Product" in types:
                p = ld_product(obj, base)
                if p:
                    out.append(p)
                return
            for v in obj.values():
                if isinstance(v, (list, dict)):
                    walk(v)

    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        try:
            walk(json.loads(m.group(1).strip()))
        except (json.JSONDecodeError, ValueError):
            continue
    return out

def ld_product(node: dict, base: str) -> dict | None:
    offers = node.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price = num(offers.get("price") or offers.get("lowPrice")) if isinstance(offers, dict) else None
    url = node.get("url") or (offers.get("url") if isinstance(offers, dict) else None)
    if not (node.get("name") and price and url):
        return None
    img = node.get("image")
    if isinstance(img, list):
        img = img[0] if img else None
    if isinstance(img, dict):
        img = img.get("url")
    agg = node.get("aggregateRating") or {}
    specs = {}
    for prop in node.get("additionalProperty") or []:
        if isinstance(prop, dict) and prop.get("name") and prop.get("value"):
            specs[str(prop["name"])] = str(prop["value"])
    avail = str(offers.get("availability", "")) if isinstance(offers, dict) else ""
    return {
        "name": node["name"], "price": price, "url": urljoin(base, url), "image_url": img,
        "rating": num(agg.get("ratingValue")), "review_count": num(agg.get("reviewCount") or agg.get("ratingCount")),
        "pid": node.get("sku") or node.get("productID"), "specs": specs,
        "in_stock": "OutOfStock" not in avail, "brand": (node.get("brand") or {}).get("name")
        if isinstance(node.get("brand"), dict) else node.get("brand"),
    }

def generic_json_products(obj: Any, base: str, depth: int = 0) -> list[dict]:
    """Recursively finds the first list of product-like dicts inside captured XHR / state JSON."""
    if depth > 8:
        return []
    if isinstance(obj, list) and len(obj) >= 2 and all(isinstance(x, dict) for x in obj[:3]):
        sample = obj[0]
        if first_key(sample, NAME_KEYS) and first_key(sample, PRICE_KEYS):
            items = []
            for d in obj:
                name, price = first_key(d, NAME_KEYS), num(first_key(d, PRICE_KEYS))
                url = first_key(d, URL_KEYS)
                if not (name and price and isinstance(url, str)):
                    continue
                img = first_key(d, IMG_KEYS)
                if isinstance(img, list):
                    img = img[0] if img else None
                if isinstance(img, dict):
                    img = img.get("url")
                items.append({
                    "name": str(name), "price": price, "mrp": num(first_key(d, MRP_KEYS)),
                    "url": urljoin(base, url), "image_url": img if isinstance(img, str) else None,
                    "rating": num(d.get("rating") or d.get("averageRating")),
                    "review_count": num(d.get("ratingCount") or d.get("reviewCount")),
                    "pid": str(d.get("productId") or d.get("code") or d.get("id") or "") or None,
                })
            if items:
                return items
    if isinstance(obj, dict):
        for v in obj.values():
            found = generic_json_products(v, base, depth + 1)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj[:50]:
            found = generic_json_products(v, base, depth + 1)
            if found:
                return found
    return []

async def http_fetch(url: str, timeout: float = 12.0) -> FetchResult:
    proxy = pick_proxy()
    try:
        async with httpx.AsyncClient(headers=browser_headers(), follow_redirects=True,
                                     timeout=timeout, proxy=proxy, http2=False) as client:
            r = await client.get(url)
            return FetchResult(status=r.status_code, html=r.text, url=str(r.url))
    except httpx.TimeoutException as exc:
        raise ScrapeTimeout(str(exc)) from exc
    except httpx.HTTPError as exc:
        raise NetworkError(str(exc)) from exc

class BaseScraper(ABC):
    name: str = "base"
    domain: str = ""
    base_url: str = ""
    needs_browser: bool = False
    SELECTORS: dict[str, list[str]] = {}

    @abstractmethod
    def search_url(self, query: str) -> str: ...

    # ---------- extraction layers (override where a site has a known structure) ----------
    def parse_state(self, html: str) -> list[dict]:
        return []

    def parse_xhr(self, payloads: list) -> list[dict]:
        for p in payloads:
            items = generic_json_products(p, self.base_url)
            if items:
                return items
        return []

    def parse_listing(self, html: str) -> list[dict]:
        S = self.SELECTORS
        tree = HTMLParser(html)
        cards: list[Node] = []
        for sel in S.get("card", []):
            cards = tree.css(sel)
            if cards:
                break
        out = []
        for card in cards:
            name, price, link = pick(card, S.get("title", [])), pick(card, S.get("price", [])), pick(card, S.get("link", []))
            if not (name and price and link):
                continue
            out.append({
                "name": name, "price": price, "mrp": pick(card, S.get("mrp", [])),
                "url": urljoin(self.base_url, link), "image_url": pick(card, S.get("image", [])),
                "rating": pick(card, S.get("rating", [])), "review_count": pick(card, S.get("reviews", [])),
                "delivery_text": pick(card, S.get("delivery", [])), "pid": pick(card, S.get("pid", [])),
                "offers_text": [t for t in [pick(card, S.get("offer", []))] if t],
                "sponsored": any(card.css_first(s) is not None for s in S.get("sponsored", [])),
            })
        return out

    def parse_product(self, html: str) -> dict:
        """Detail-page enrichment: specs/offers/delivery."""
        tree = HTMLParser(html)
        S = self.SELECTORS
        items = parse_jsonld(html, self.base_url)
        detail: dict = {"specs": items[0].get("specs", {}) if items else {}}
        offers = [n.text(strip=True) for s in S.get("detail_offers", []) for n in tree.css(s)][:6]
        if offers:
            detail["offers_text"] = offers
        root = tree.root
        if root is not None:
            d = pick(root, S.get("detail_delivery", []))
            if d:
                detail["delivery_text"] = d
        return detail

    def extract(self, res: FetchResult) -> list[dict]:
        layers = (
            lambda: parse_jsonld(res.html, self.base_url),
            lambda: self.parse_state(res.html),
            lambda: self.parse_xhr(res.json_responses),
            lambda: self.parse_listing(res.html),
        )
        for layer in layers:
            try:
                items = layer()
            except Exception as exc:
                log(logger, logging.DEBUG, "layer failed", site=self.domain, error=str(exc))
                items = []
            if items:
                return items
        return []

    # ---------- fetching ----------
    async def fetch(self, url: str) -> FetchResult:
        await domain_limiter.wait(self.domain)
        if self.needs_browser and browser_pool.ready and settings.use_browser:
            try:
                res = await browser_pool.fetch(url, self.SELECTORS.get("card", []))
            except Exception as exc:
                if "Timeout" in type(exc).__name__:
                    raise ScrapeTimeout(str(exc)) from exc
                raise NetworkError(str(exc)) from exc
        else:
            res = await http_fetch(url)
        detect_block(res.status, res.html, res.url)
        return res

    async def search(self, query: QueryInfo, limit: int) -> ScraperResult:
        t0 = time.perf_counter()
        url = self.search_url(query.clean)
        ms = lambda: int((time.perf_counter() - t0) * 1000)  # noqa: E731
        try:
            res: FetchResult | None = None
            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(2), reraise=True,
                    wait=wait_random_exponential(multiplier=1, min=2, max=5),
                    retry=retry_if_exception_type((BlockedError, NetworkError)),
                ):
                    with attempt:
                        res = await self.fetch(url)  # new context + new UA on every attempt
            except BlockedError:
                if not settings.scraper_api_key:
                    raise
                res = await http_fetch(scraper_api_url(url), timeout=15)
                detect_block(res.status, res.html, res.url)
            assert res is not None
            items = self.extract(res)[:limit]
            if items and settings.fetch_details:
                try:
                    detail_res = await self.fetch(items[0]["url"])
                    items[0].update({k: v for k, v in self.parse_product(detail_res.html).items() if v})
                except ScraperError:
                    pass
            status = "ok" if items else "empty"
            log(logger, logging.INFO, "scrape done", site=self.domain, query=query.clean,
                status=status, count=len(items), duration_ms=ms())
            return ScraperResult(site=self.domain, status=status, items=items, duration_ms=ms())
        except asyncio.CancelledError:
            raise
        except ScraperError as exc:
            status = {"blocked": "blocked", "timeout": "timeout"}.get(exc.kind, "error")
            log(logger, logging.WARNING, "scrape failed", site=self.domain, query=query.clean,
                kind=exc.kind, error=str(exc), duration_ms=ms())
            return ScraperResult(site=self.domain, status=status, error=f"{exc.kind}: {exc}", duration_ms=ms())
        except Exception as exc:
            err = ParseError(str(exc))
            log(logger, logging.ERROR, "scrape unexpected", site=self.domain, error=repr(exc), duration_ms=ms())
            return ScraperResult(site=self.domain, status="error", error=f"unexpected: {err}", duration_ms=ms())