from datetime import date
from app.utils.delivery import parse_delivery
from app.utils.price import compute_discount, fmt_inr, parse_price
def test_parse_price_variants():
    assert parse_price("₹1,29,999") == 129999.0
    assert parse_price("Rs. 999") == 999.0
    assert parse_price("from ₹499 - ₹899") == 499.0
    assert parse_price("₹58,999.50") == 58999.5
    assert parse_price(None) is None and parse_price("N/A") is None and parse_price(0) is None

def test_discount_and_format():
    assert compute_discount(58999, 79900) == (20901, 26.2)
    assert compute_discount(100, 90) == (None, None)
    assert fmt_inr(129999) == "₹1,29,999"

def test_delivery():
    today = date(2025, 10, 11)
    d = parse_delivery("FREE delivery Tue, 14 Oct", today)
    assert d["estimated_date"] == "2025-10-14" and d["estimated_days"] == 3 and d["free"]
    assert parse_delivery("Get it by Tomorrow", today)["estimated_days"] == 1
    assert parse_delivery("Delivery in 3-5 days", today)["estimated_days"] == 5
    assert parse_delivery(None)["estimated_days"] is None