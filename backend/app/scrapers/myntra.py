import json
import re
from urllib.parse import quote
from app.scrapers.base import BaseScraper

SELECTORS = {
    "card": ["li.product-base"],
    "title": ["h4.product-product", "h3.product-brand"],
    "price": ["span.product-discountedPrice", "div.product-price span"],
    "mrp": ["span.product-strike"],
    "link": ["a@href"],
    "image": ["img.img-responsive@src", "picture img@src"],
    "rating": ["div.product-ratingsContainer span"],
    "reviews": ["div.product-ratingsCount"],
}

class Myntra(BaseScraper):
    name, domain, base_url, needs_browser = "myntra", "myntra.com", "https://www.myntra.com", True
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.myntra.com/{quote(query.replace(' ', '-'))}?rawQuery={quote(query)}"

    def parse_state(self, html: str) -> list[dict]:
        # Myntra embeds search data in `window.__myx = {...}`
        m = re.search(r"window\.__myx\s*=\s*(\{.*?\})\s*;?\s*</script>", html, re.S)
        if not m:
            return []
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return []
        products = (data.get("searchData") or {}).get("results", {}).get("products", [])
        out = []
        for p in products:
            out.append({
                "name": f"{p.get('brand', '')} {p.get('productName') or p.get('product', '')}".strip(),
                "price": p.get("price"), "mrp": p.get("mrp"),
                "url": f"{self.base_url}/{p.get('landingPageUrl', '')}",
                "image_url": p.get("searchImage"), "rating": p.get("rating"),
                "review_count": p.get("ratingCount"), "pid": str(p.get("productId", "")) or None,
                "in_stock": bool(p.get("inventoryInfo", [{}])) if "inventoryInfo" in p else True,
            })
        return out