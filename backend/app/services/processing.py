import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from pydantic import ValidationError
from app.models.schemas import Delivery, Offer, Product, QueryInfo
from app.utils.delivery import parse_delivery
from app.utils.price import compute_discount, parse_price
from app.utils.text import compact, is_accessory, similarity

KEEP_PARAMS = {"pid", "lid", "p", "productId", "k", "q", "keyword", "text", "rawQuery", "v"}
OFFER_TYPES = [("bank", ["bank", "card", "hdfc", "icici", "sbi", "axis", "kotak"]), ("emi", ["emi"]),
               ("exchange", ["exchange"]), ("coupon", ["coupon", "code"]), ("cashback", ["cashback"])]


def canonical_url(url: str, site: str) -> str:
    p = urlparse(url)
    if site == "amazon.in":
        m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", p.path)
        if m:
            return f"https://www.amazon.in/dp/{m.group(1)}"
    q = urlencode([(k, v) for k, v in parse_qsl(p.query) if k in KEEP_PARAMS])
    return urlunparse((p.scheme or "https", p.netloc, p.path, "", q, ""))


def product_id(site: str, url: str, pid: object) -> str:
    if site == "amazon.in" and (m := re.search(r"/dp/([A-Z0-9]{10})", url)):
        return f"{site}:{m.group(1)}"
    if pid:
        return f"{site}:{pid}"
    return f"{site}:{compact(urlparse(url).path)[-40:]}"


def parse_offers(texts: list[str], price: float) -> list[Offer]:
    out = []
    for t in texts[:6]:
        low = t.lower()
        typ = next((name for name, kws in OFFER_TYPES if any(k in low for k in kws)), "other")
        saving = None
        if m := re.search(r"(?:\u20b9|rs\.?)\s?([\d,]+)", low):
            saving = parse_price(m.group(1))
        elif m := re.search(r"(\d{1,2})\s?%", low):
            saving = round(price * int(m.group(1)) / 100, 0)
            if cap := re.search(r"up to\s*(?:\u20b9|rs\.?)\s?([\d,]+)", low):
                saving = min(saving, parse_price(cap.group(1)) or saving)
        out.append(Offer(type=typ, text=t.strip()[:160], estimated_saving_inr=saving))
    return out


def _rating(v: object) -> float | None:
    if v is None:
        return None
    m = re.search(r"(\d(?:\.\d)?)", str(v))
    r = float(m.group(1)) if m else None
    return r if r is not None and 0 < r <= 5 else None


def _count(v: object) -> int | None:
    if v is None:
        return None
    s = str(v).lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|l)?", s)
    if not m:
        return None
    n = float(m.group(1)) * {"k": 1_000, "l": 100_000}.get(m.group(2) or "", 1)
    return int(n)


def is_relevant(name: str, q: QueryInfo) -> bool:
    if similarity(q.clean, name) < 60:
        return False
    title = compact(name)
    if q.brand and q.brand not in title and not any(t in title for t in q.tokens[:1]):
        return False
    if (st := q.attributes.get("storage")) and st not in title:
        return False
    return not is_accessory(name, q.clean)


def build_product(site: str, raw: dict, q: QueryInfo) -> Product | None:
    price = parse_price(raw.get("price"))
    url = raw.get("url")
    name = re.sub(r"\s+", " ", str(raw.get("name") or "")).strip()
    if not (price and url and name) or raw.get("sponsored"):
        return None
    url = canonical_url(url, site)
    mrp = parse_price(raw.get("mrp"))
    amount, pct = compute_discount(price, mrp)
    specs = {str(k)[:40]: str(v)[:80] for k, v in list((raw.get("specs") or {}).items())[:12]}
    try:
        return Product(
            id=product_id(site, url, raw.get("pid")), site=site, name=name[:200], image_url=raw.get("image_url"),
            specs=specs, price=price, mrp=mrp if amount else None, discount_amount=amount, discount_percent=pct,
            offers=parse_offers(list(raw.get("offers_text") or []), price),
            delivery=Delivery(**parse_delivery(raw.get("delivery_text"))),
            rating=_rating(raw.get("rating")), review_count=_count(raw.get("review_count")),
            in_stock=bool(raw.get("in_stock", True)), url=url,
            source=raw.get("source", "scrape"), verified=bool(raw.get("verified", True)),
            stale=bool(raw.get("stale", False)),
        )
    except ValidationError:
        return None


def process_site(site: str, raw_items: list[dict], q: QueryInfo, limit: int = 8, relevance: bool = True) -> list[Product]:
    seen: set[str] = set()
    out: list[Product] = []
    for raw in raw_items:
        p = build_product(site, raw, q)
        if not p or (relevance and not is_relevant(p.name, q)):
            continue
        if p.id in seen or p.url in seen:
            continue
        seen.update({p.id, p.url})
        out.append(p)
        if len(out) >= limit:
            break
    return out