from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper

SELECTORS = {
    "card": ["li.grid", "div.product-card", "div.sp.grid"],
    "title": ["p.sp__name", "div.product-card-title", "p[class*='name']"],
    "price": ["span[class*='TextWeb__Text'] span:nth-child(2)", "div.price", "span.price"],
    "mrp": ["span[class*='StyledPriceBoxM__MRPText']", "div.mrp", "span.mrp"],
    "link": ["a@href"],
    "image": ["img@data-srcset", "img@src"],
    "rating": ["span.rating"],
}


class RelianceDigital(BaseScraper):
    name, domain, base_url, needs_browser = "reliance_digital", "reliancedigital.in", "https://www.reliancedigital.in", True
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.reliancedigital.in/products?q={quote_plus(query)}"