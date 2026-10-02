from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper

# Amazon search is server-rendered: httpx first. Selectors best-effort as of 2024-25; adjust here.
SELECTORS = {
    "card": ['div[data-component-type="s-search-result"]', "div.s-result-item[data-asin]"],
    "pid": ["@data-asin"],
    "title": ["h2 a span", "h2 span", "span.a-size-medium.a-color-base.a-text-normal", "span.a-size-base-plus"],
    "price": ["span.a-price:not(.a-text-price) span.a-offscreen", "span.a-price-whole"],
    "mrp": ["span.a-price.a-text-price span.a-offscreen", "span.a-text-price span.a-offscreen"],
    "link": ["h2 a@href", "a.a-link-normal.s-no-outline@href", "a.a-link-normal@href"],
    "image": ["img.s-image@src"],
    "rating": ["span.a-icon-alt", "i.a-icon-star-small span"],
    "reviews": ["span.a-size-base.s-underline-text", "a[href*='customerReviews'] span"],
    "delivery": ['[data-cy="delivery-recipe"]', "div.udm-primary-delivery-message", "span.a-color-base.a-text-bold"],
    "offer": ["span.s-coupon-unclipped", "span.a-color-secondary span.a-text-bold"],
    "sponsored": [".puis-sponsored-label-text", "span.s-label-popover-default", "a.puis-label-popover"],
    "detail_offers": ["#itembox-InstantBankDiscount .a-truncate-full", ".offers-items-content"],
    "detail_delivery": ["#mir-layout-DELIVERY_BLOCK span[data-csa-c-delivery-time]", "#deliveryBlockMessage"],
}


class AmazonIn(BaseScraper):
    name, domain, base_url, needs_browser = "amazon_in", "amazon.in", "https://www.amazon.in", False
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.amazon.in/s?k={quote_plus(query)}"