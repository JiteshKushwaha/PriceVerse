import json
import re
from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper

SELECTORS = {
    "card": ["div.item.rilrtl-products-list__item", "div.rilrtl-products-list__item"],
    "title": ["div.nameCls", "div.brand"],
    "price": ["span.price strong", "span.price"],
    "mrp": ["span.orginal-price"],
    "link": ["a.rilrtl-products-list__link@href", "a@href"],
    "image": ["img.rilrtl-lazy-img@src", "img@src"],
}

class Ajio(BaseScraper):
    name, domain, base_url, needs_browser = "ajio", "ajio.com", "https://www.ajio.com", True
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.ajio.com/search/?text={quote_plus(query)}"

    def parse_state(self, html: str) -> list[dict]:
        m = re.search(r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});?\s*</script>", html, re.S)
        if not m:
            return []
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return []
        entities = ((data.get("grid") or {}).get("entities") or {})
        out = []
        for p in entities.values():
            brand = (p.get("fnlColorVariantData") or {}).get("brandName", "")
            imgs = p.get("images") or [{}]
            out.append({
                "name": f"{brand} {p.get('name', '')}".strip(),
                "price": (p.get("price") or {}).get("value"),
                "mrp": (p.get("wasPriceData") or {}).get("value"),
                "url": f"{self.base_url}{p.get('url', '')}", "image_url": imgs[0].get("url"),
                "pid": p.get("code"),
            })
        return out