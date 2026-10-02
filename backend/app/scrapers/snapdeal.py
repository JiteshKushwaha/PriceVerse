from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper

# Snapdeal is server-rendered → httpx + CSS works well.
SELECTORS = {
    "card": ["div.product-tuple-listing", "div.col-xs-6.favDp"],
    "pid": ["@data-js-pdpid", "@id"],
    "title": ["p.product-title", "p.product-title@title"],
    "price": ["span.product-price@data-price", "span.product-price@display-price", "span.product-price"],
    "mrp": ["span.product-desc-price"],
    "link": ["a.dp-widget-link@href", "a@href"],
    "image": ["img.product-image@src", "img.product-image@data-src", "source@srcset"],
    "reviews": ["p.product-rating-count"],
}


class Snapdeal(BaseScraper):
    name, domain, base_url, needs_browser = "snapdeal", "snapdeal.com", "https://www.snapdeal.com", False
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.snapdeal.com/search?keyword={quote_plus(query)}&sort=rlvncy"