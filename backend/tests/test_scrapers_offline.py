import pytest
from app.core.errors import BlockedError
from app.scrapers.amazon_in import AmazonIn
from app.scrapers.anti_bot import detect_block
from app.scrapers.base import parse_jsonld
from app.scrapers.myntra import Myntra
from app.scrapers.snapdeal import Snapdeal
from app.services.orchestrator import run_search
from app.services.processing import process_site
from app.services.query_normalizer import normalize
def test_amazon_listing(fixture_html):
    items = AmazonIn().parse_listing(fixture_html("amazon_in.html"))
    assert items[0]["pid"] == "B0CHX1W1XY" and items[1]["sponsored"] is True
    out = process_site("amazon.in", items, normalize("iphone 15 128gb"))
    assert [p.id for p in out] == ["amazon.in:B0CHX1W1XY"]
    assert out[0].price == 61999 and out[0].discount_percent == 22.4 and out[0].rating == 4.5

def test_snapdeal_listing(fixture_html):
    items = Snapdeal().parse_listing(fixture_html("snapdeal.html"))
    p = process_site("snapdeal.com", items, normalize("boat airdopes 141"))[0]
    assert p.price == 1149 and p.mrp == 4490 and "utm_source" not in p.url and p.review_count == 2345

def test_myntra_state(fixture_html):
    items = Myntra().parse_state(fixture_html("myntra.html"))
    assert items[0]["price"] == 5295 and items[0]["url"].startswith("https://www.myntra.com/")

def test_jsonld(fixture_html):
    items = parse_jsonld(fixture_html("jsonld.html"), "https://www.flipkart.com")
    assert items[0]["price"] == 64999 and items[0]["url"].startswith("https://www.flipkart.com/")

def test_block_detection():
    with pytest.raises(BlockedError):
        detect_block(200, "<html>Enter the characters you see below" + "x" * 2000, "https://www.amazon.in/s")
    with pytest.raises(BlockedError):
        detect_block(403, "x" * 5000, "https://x")

async def test_demo_pipeline():
    from app.core.cache import cache
    from app.models.db import init_db
    await init_db()
    await cache.connect()
    resp = await run_search("iphone 15")
    assert resp["demo"] is True and resp["results"] and resp["summary"]["cheapest"]["price"] > 0
    assert (await run_search("iphone 15"))["cached"] is True