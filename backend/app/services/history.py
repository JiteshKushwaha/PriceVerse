import hashlib
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models.db import ClickLog, PriceHistory, SessionLocal
from app.models.schemas import Product


def qhash(clean: str) -> str:
    return hashlib.sha1(clean.encode()).hexdigest()


async def save_points(query_hash: str, query: str, products: list[Product]) -> None:
    async with SessionLocal() as s:
        s.add_all([PriceHistory(query_hash=query_hash, query=query[:120], site=p.site, product_url=p.url[:1000],
                                product_name=p.name[:300], price=p.price) for p in products])
        await s.commit()


async def log_click(site: str, url: str) -> None:
    async with SessionLocal() as s:
        s.add(ClickLog(site=site, url=url[:1000]))
        await s.commit()

async def get_history(clean: str, days: int = 30, synthesize: bool = False) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    async with SessionLocal() as s:
        rows = (await s.execute(select(PriceHistory.timestamp, PriceHistory.price, PriceHistory.site)
                                .where(PriceHistory.query_hash == qhash(clean), PriceHistory.timestamp >= since))).all()
    buckets: dict[str, list[float]] = defaultdict(list)
    for ts, price, _ in rows:
        buckets[ts.date().isoformat()].append(price)
    points = [{"date": d, "min_price": min(v), "avg_price": round(sum(v) / len(v), 2), "synthetic": False}
              for d, v in sorted(buckets.items())]
    if synthesize and len(points) < 3:
        base = points[-1]["min_price"] if points else 10000.0
        rnd = random.Random(clean)
        today = datetime.now(timezone.utc).date()
        synth = []
        for i in range(14, 0, -1):
            m = base * (1 + rnd.uniform(-0.04, 0.08))
            synth.append({"date": (today - timedelta(days=i)).isoformat(), "min_price": round(m),
                          "avg_price": round(m * rnd.uniform(1.03, 1.1)), "synthetic": True})
        points = synth + points
    return points