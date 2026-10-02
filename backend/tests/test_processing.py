from app.services.processing import canonical_url, parse_offers, process_site
from app.services.query_normalizer import normalize

def test_normalizer():
    q = normalize("Buy iPhone 15 128GB Black online best price")
    assert q.clean == "iphone 15 128gb black"
    assert q.brand == "apple" and q.attributes["storage"] == "128gb" and q.attributes["color"] == "black"

def test_canonical_amazon():
    assert canonical_url("https://www.amazon.in/Apple-iPhone/dp/B0CHX1W1XY/ref=sr_1?x=1", "amazon.in") == \
        "https://www.amazon.in/dp/B0CHX1W1XY"

def test_relevance_dedupe_accessory():
    q = normalize("iphone 15 128gb")
    raw = [
        {"name": "Apple iPhone 15 (128 GB) - Black", "price": "₹61,999", "url": "https://www.amazon.in/dp/B0CHX1W1XY"},
        {"name": "Apple iPhone 15 (128 GB) - Black", "price": "₹61,999", "url": "https://www.amazon.in/x/dp/B0CHX1W1XY?t=1"},
        {"name": "Back Cover Case for iPhone 15 128GB", "price": "₹299", "url": "https://www.amazon.in/dp/B0CASE0001"},
        {"name": "Samsung Galaxy S24", "price": "₹64,999", "url": "https://www.amazon.in/dp/B0SAMSUNG1"},
        {"name": "Apple iPhone 15 (128 GB)", "price": None, "url": "https://www.amazon.in/dp/B0NOPRICE1"},
    ]
    out = process_site("amazon.in", raw, q)
    assert len(out) == 1 and out[0].id == "amazon.in:B0CHX1W1XY"

def test_offers():
    offers = parse_offers(["10% instant discount with HDFC Bank cards up to ₹1,500", "No Cost EMI"], 60000)
    assert offers[0].type == "bank" and offers[0].estimated_saving_inr == 1500
    assert offers[1].type == "emi"