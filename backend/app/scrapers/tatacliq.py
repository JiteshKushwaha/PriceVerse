from urllib.parse import quote_plus
from app.scrapers.base import BaseScraper, first_key, num

SELECTORS = {
    "card": ["div.ProductModule__base", "div[class*='ProductModule__base']"],
    "title": ["h2.ProductDescription__description", "div[class*='ProductDescription__description']"],
    "price": ["h3.ProductDescription__boldText", "div[class*='ProductDescription__discount'] h3"],
    "mrp": ["div.ProductDescription__priceCancelled", "div[class*='priceCancelled']"],
    "link": ["a@href"],
    "image": ["img@src"],
}

class TataCliq(BaseScraper):
    name, domain, base_url, needs_browser = "tatacliq", "tatacliq.com", "https://www.tatacliq.com", True
    SELECTORS = SELECTORS

    def search_url(self, query: str) -> str:
        return f"https://www.tatacliq.com/search/?searchCategory=all&text={quote_plus(query)}"

    def parse_xhr(self, payloads: list) -> list[dict]:
        # TataCliq search API returns {"searchresult": [{productname, winningSellerPrice, mrpPrice, webURL, imageURL}]}
        for p in payloads:
            if isinstance(p, dict) and isinstance(p.get("searchresult"), list):
                out = []
                for d in p["searchresult"]:
                    url = d.get("webURL")
                    price = num(first_key(d, ("winningSellerPrice", "price")))
                    if url and price:
                        out.append({
                            "name": f"{d.get('brandname', '')} {d.get('productname', '')}".strip(),
                            "price": price, "mrp": num(d.get("mrpPrice")),
                            "url": url if url.startswith("http") else f"{self.base_url}{url}",
                            "image_url": d.get("imageURL"), "pid": d.get("productId"),
                            "rating": num(d.get("averageRating")), "review_count": num(d.get("ratingCount")),
                        })
                if out:
                    return out
        return super().parse_xhr(payloads)