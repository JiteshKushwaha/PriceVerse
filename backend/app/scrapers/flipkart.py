import json
import re
from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper, generic_json_products

# Flipkart class names are obfuscated and rotate. Several generations kept as fallbacks.
SELECTORS = {
    "card": ["div[data-id]", "div._1AtVbE div._13oc-S > div", "div.cPHDOP div[data-id]"],
    "pid": ["@data-id"],
    "title": ["div.KzDlHZ", "a.wjcEIp", "div._4rR01T", "a.s1Q9rs", "a.IRpwTa", "a[title]@title"],
    "price": ["div.Nx9bqj", "div._30jeq3", "div._25b18c div"],
    "mrp": ["div.yRaY8j", "div._3I9_wc"],
    "link": ["a.CGtC98@href", "a._1fQZEK@href", "a.wjcEIp@href", "a.s1Q9rs@href", "a.rPDeLR@href", "a@href"],
    "image": ["img.DByuf4@src", "img._396cs4@src", "img._53J4C-@src", "img@src"],
    "rating": ["div.XQDdHH", "div._3LWZlK"],
    "reviews": ["span.Wphh3N", "span._2_R_DZ"],
    "delivery": ["div.yiggsN", "div._2Tpdn3"],
    "offer": ["div.UkUFwK span", "div._3Ay6Sb span"],
    "sponsored": ["div.xgS27m", "div._4HTuuX"],
    "detail_offers": ["li.kF1Ml8", "li._16eBzU"],
    "detail_delivery": ["div.hVvnXm", "div._3XINqE"],
}

class Flipkart(BaseScraper):
    name, domain, base_url, needs_browser = "flipkart", "flipkart.com", "https://www.flipkart.com", False
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.flipkart.com/search?q={quote_plus(query)}&otracker=search&marketplace=FLIPKART"

    def parse_state(self, html: str) -> list[dict]:
        m = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});\s*</script>", html, re.S)
        if not m:
            return []
        try:
            return generic_json_products(json.loads(m.group(1)), self.base_url)
        except json.JSONDecodeError:
            return []