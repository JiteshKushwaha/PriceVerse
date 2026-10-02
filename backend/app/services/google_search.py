import logging
from collections import defaultdict
from urllib.parse import urlparse
import httpx
from app.config import SITE_DOMAINS, settings
from app.core.logging import log

logger = logging.getLogger("google")
SOURCE_MAP = {"amazon": "amazon.in", "flipkart": "flipkart.com", "myntra": "myntra.com", "croma": "croma.com",
              "reliance": "reliancedigital.in", "ajio": "ajio.com", "snapdeal": "snapdeal.com", "tata": "tatacliq.com"}


def domain_of(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower()
    return next((d for d in SITE_DOMAINS if host == d or host.endswith("." + d)), None)


def _hint(name: str, price: object, url: str, **extra: object) -> dict:
    return {"name": name, "price": price, "url": url, "source": "google_snippet", "verified": False, **extra}


async def _serpapi(client: httpx.AsyncClient, q: str, out: dict) -> None:
    base = {"api_key": settings.serpapi_key, "gl": "in", "hl": "en", "location": "India"}
    r = await client.get("https://serpapi.com/search.json", params={**base, "engine": "google_shopping", "q": q})
    if r.status_code == 200:
        for it in r.json().get("shopping_results", [])[:40]:
            link = it.get("link") or it.get("product_link") or ""
            dom = domain_of(link) or next((v for k, v in SOURCE_MAP.items() if k in str(it.get("source", "")).lower()), None)
            if dom and domain_of(link):
                out[dom].append(_hint(it.get("title", ""), it.get("extracted_price") or it.get("price"), link,
                                      image_url=it.get("thumbnail"), rating=it.get("rating"),
                                      review_count=it.get("reviews"), delivery_text=it.get("delivery")))
    sites = " OR ".join(f"site:{d}" for d in ("amazon.in", "flipkart.com", "myntra.com"))
    r = await client.get("https://serpapi.com/search.json", params={**base, "engine": "google", "q": f"{q} {sites}"})
    if r.status_code == 200:
        for it in r.json().get("organic_results", [])[:20]:
            link = it.get("link", "")
            dom = domain_of(link)
            ext = ((it.get("rich_snippet") or {}).get("bottom") or {}).get("detected_extensions") or {}
            if dom and ext.get("price"):
                out[dom].append(_hint(it.get("title", ""), ext.get("price"), link))


async def _cse(client: httpx.AsyncClient, q: str, out: dict) -> None:
    r = await client.get("https://www.googleapis.com/customsearch/v1",
                         params={"key": settings.google_cse_key, "cx": settings.google_cse_cx, "q": q, "gl": "in", "num": 10})
    if r.status_code != 200:
        return
    for it in r.json().get("items", []):
        link = it.get("link", "")
        dom = domain_of(link)
        pm = it.get("pagemap") or {}
        price = ((pm.get("offer") or [{}])[0].get("price")) or ((pm.get("product") or [{}])[0].get("price"))
        if dom and price:
            img = (pm.get("cse_image") or [{}])[0].get("src")
            out[dom].append(_hint(it.get("title", ""), price, link, image_url=img))


async def discover(q: str) -> dict[str, list[dict]]:
    """Google discovery. Snippet prices are hints only; used as fallback when a site blocks us."""
    out: dict[str, list[dict]] = defaultdict(list)
    if not (settings.serpapi_key or (settings.google_cse_key and settings.google_cse_cx)):
        return out
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            if settings.serpapi_key:
                await _serpapi(client, q, out)
            if not out and settings.google_cse_key and settings.google_cse_cx:
                await _cse(client, q, out)
    except Exception as exc:  # quota / network: skip silently
        log(logger, logging.WARNING, "google discovery failed", error=str(exc))
    return out