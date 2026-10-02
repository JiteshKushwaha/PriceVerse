"""Self-contained demo generator (stdlib only, also used by streamlit_app.py)."""
import hashlib
import random
from difflib import SequenceMatcher
from urllib.parse import quote, quote_plus

SEARCH_URLS = {
    "amazon.in": "https://www.amazon.in/s?k={q}",
    "flipkart.com": "https://www.flipkart.com/search?q={q}",
    "myntra.com": "https://www.myntra.com/{slug}",
    "croma.com": "https://www.croma.com/searchB?q={q}%3Arelevance&text={q}",
    "reliancedigital.in": "https://www.reliancedigital.in/products?q={q}",
    "ajio.com": "https://www.ajio.com/search/?text={q}",
    "snapdeal.com": "https://www.snapdeal.com/search?keyword={q}",
    "tatacliq.com": "https://www.tatacliq.com/search/?text={q}",
}
ELECTRONICS = ["amazon.in", "flipkart.com", "croma.com", "reliancedigital.in", "tatacliq.com", "snapdeal.com"]
FASHION = ["amazon.in", "flipkart.com", "myntra.com", "ajio.com", "tatacliq.com", "snapdeal.com"]

CATALOG = [
    ("iphone 15", "Apple iPhone 15 (128 GB) - Black", 61999, 79900, "e", {"Storage": "128 GB", "Display": "6.1 inch", "Chip": "A16 Bionic", "Camera": "48 MP"}),
    ("iphone 15 pro", "Apple iPhone 15 Pro (256 GB) - Natural Titanium", 119900, 144900, "e", {"Storage": "256 GB", "Display": "6.1 inch", "Chip": "A17 Pro"}),
    ("samsung galaxy s24", "Samsung Galaxy S24 5G (8GB RAM, 256GB) - Onyx Black", 64999, 89999, "e", {"RAM": "8 GB", "Storage": "256 GB", "Display": "6.2 inch"}),
    ("oneplus 12", "OnePlus 12 (12GB RAM, 256GB) - Silky Black", 62999, 69999, "e", {"RAM": "12 GB", "Storage": "256 GB", "Battery": "5400 mAh"}),
    ("redmi note 13", "Redmi Note 13 5G (8GB RAM, 256GB) - Arctic White", 18999, 24999, "e", {"RAM": "8 GB", "Storage": "256 GB"}),
    ("boat airdopes 141", "boAt Airdopes 141 TWS Earbuds with 42H Playtime", 1099, 4490, "e", {"Playtime": "42 H", "Bluetooth": "5.1"}),
    ("sony wh-1000xm5", "Sony WH-1000XM5 Wireless Noise Cancelling Headphones", 26990, 34990, "e", {"Type": "Over-ear", "ANC": "Yes", "Battery": "30 H"}),
    ("macbook air m2", "Apple MacBook Air M2 (8GB, 256GB SSD) 13.6 inch", 89990, 114900, "e", {"RAM": "8 GB", "SSD": "256 GB", "Display": "13.6 inch"}),
    ("hp laptop", "HP 15s Intel Core i5 12th Gen (16GB/512GB SSD) Laptop", 52990, 68000, "e", {"RAM": "16 GB", "SSD": "512 GB", "CPU": "i5-1235U"}),
    ("apple watch", "Apple Watch SE (2nd Gen) GPS 44mm", 26900, 32900, "e", {"Size": "44 mm", "GPS": "Yes"}),
    ("nike air max", "Nike Air Max SC Men's Running Shoes", 5295, 6295, "f", {"Type": "Running", "Material": "Mesh"}),
    ("adidas sneakers", "Adidas Men's Grand Court 2.0 Sneakers", 3299, 5999, "f", {"Type": "Sneakers", "Closure": "Lace-up"}),
    ("puma t-shirt", "Puma Men's Regular Fit Cotton T-Shirt", 799, 1599, "f", {"Fabric": "Cotton", "Fit": "Regular"}),
    ("levis jeans", "Levi's Men's 511 Slim Fit Jeans", 1899, 3599, "f", {"Fit": "Slim", "Fabric": "Denim"}),
    ("fossil watch", "Fossil Grant Chronograph Analog Men's Watch", 8995, 12995, "f", {"Dial": "44 mm", "Strap": "Leather"}),
]
OFFERS = ["10% instant discount with HDFC Bank cards up to ₹1,500", "No Cost EMI on select cards",
          "5% cashback with Axis Bank card", "Extra ₹500 off on exchange", "Use coupon SAVE200 for ₹200 off"]


def _seed(*parts: str) -> int:
    return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:8], 16)


def site_search_url(site: str, query: str) -> str:
    return SEARCH_URLS[site].format(q=quote_plus(query), slug=quote(query.replace(" ", "-")))


def match_catalog(query: str):
    best, score = None, 0.0
    for item in CATALOG:
        s = SequenceMatcher(None, query.lower(), item[0]).ratio()
        if item[0] in query.lower():
            s += 0.5
        if s > score:
            best, score = item, s
    return best if score >= 0.55 else None

GENERIC_BASE = [
    (("sanitizer", "soap", "handwash", "shampoo", "toothpaste", "cream", "oil"), 199),
    (("book", "pen", "notebook", "bottle", "bag", "mouse", "cable"), 499),
    (("shirt", "jeans", "shoes", "watch", "dress"), 1499),
]

def generate_items(query: str) -> dict[str, list[dict]]:
    """Returns {site: [raw product dicts]} with realistic variation. URLs are real site search pages."""
    item = match_catalog(query)
    if item:
        _, name, base, mrp, cat, specs = item
    else:
        rnd0 = random.Random(_seed(query))
        # base = rnd0.choice([799, 1499, 2999, 7999, 14999, 29999, 49999])
        q = query.lower()
        base = next((b for kws, b in GENERIC_BASE if any(k in q for k in kws)),
                    rnd0.choice([299, 499, 799, 1299, 1999]))
        mrp, cat, specs = int(base * rnd0.uniform(1.2, 1.8)), "e", {"Category": "General"}
        name = query.strip().title()
    sites = ELECTRONICS if cat == "e" else FASHION
    out: dict[str, list[dict]] = {}
    for site in sites:
        rnd = random.Random(_seed(query, site))
        items = []
        for v in range(2):
            price = round(base * rnd.uniform(0.94, 1.08) / 10) * 10 - 1
            days = rnd.randint(1, 6)
            items.append({
                "name": name if v == 0 else f"{name} (Renewed Box)" if cat == "e" else f"{name} - Combo",
                "price": float(price if v == 0 else round(price * 1.06)), "mrp": float(mrp),
                "url": site_search_url(site, query) + ("" if v == 0 else "&v=2"),
                "image_url": f"https://placehold.co/400x400/101428/FFD60A?text={quote_plus(site.split('.')[0])}", "rating": round(rnd.uniform(3.9, 4.7), 1),
                "review_count": rnd.randint(40, 25000), "delivery_text":
                    f"{'FREE ' if rnd.random() > 0.3 else ''}Delivery in {days} days",
                "offers_text": rnd.sample(OFFERS, k=rnd.randint(1, 3)), "specs": specs,
                "pid": f"DEMO{_seed(query, site, str(v)) % 10**8}", "source": "demo", "in_stock": rnd.random() > 0.08,
            })
        out[site] = items
    return out