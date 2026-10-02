from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper

# Croma is a client-rendered SPA: Playwright + XHR capture (generic JSON walker) first.
SELECTORS = {
    "card": ["li.product-item", "div.product-item", "div.cp-product"],
    "title": ["h3.product-title a", "h3.product-title", "a.product-title"],
    "price": ["span.amount[data-testid='new-price']", "span.new-price span.amount", "span.amount"],
    "mrp": ["span#old-price", "span.old-price span.amount"],
    "link": ["h3.product-title a@href", "a@href"],
    "image": ["img@data-src", "img@src"],
    "rating": ["span.rating-text"],
    "delivery": ["div.delivery-text", "span.delivery-info"],}

class Croma(BaseScraper):
    name, domain, base_url, needs_browser = "croma", "croma.com", "https://www.croma.com", True
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.croma.com/searchB?q={quote_plus(query)}%3Arelevance&text={quote_plus(query)}"