from app.models.schemas import Delivery, Product
from app.services.ranking import rank

def mk(site, price, rating=4.4, rc=1000, days=3):
    return Product(id=f"{site}:1", site=site, name="X", price=price, rating=rating, review_count=rc,
                   delivery=Delivery(estimated_days=days), url=f"https://www.{site}/p")

def test_rank_summary():
    products, summary = rank([mk("amazon.in", 60999), mk("flipkart.com", 58999, days=1), mk("croma.com", 62999)])
    assert summary["cheapest"]["site"] == "flipkart.com"
    assert summary["fastest_delivery"]["site"] == "flipkart.com"
    assert summary["savings_vs_highest"]["inr"] == 4000
    assert "Flipkart" in summary["explanation"] and "₹2,000 below Amazon" in summary["explanation"]
    assert products[0].score >= products[-1].score and 0 <= products[-1].score <= 100
    assert "CHEAPEST" in next(p for p in products if p.site == "flipkart.com").badges

def test_rank_empty():
    assert rank([]) == ([], {})