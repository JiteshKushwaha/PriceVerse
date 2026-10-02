"""Save live HTML for offline tests:  python -m scripts.record_fixtures "iphone 15" amazon_in snapdeal"""
import asyncio
import pathlib
import sys
from app.scrapers.base import http_fetch
from app.scrapers.browser_pool import browser_pool
from app.scrapers.registry import ALL
OUT = pathlib.Path(__file__).resolve().parents[1] / "tests" / "fixtures"

async def main(query: str, names: list[str]) -> None:
    await browser_pool.start()
    try:
        for n in names or list(ALL):
            s = ALL[n]()
            url = s.search_url(query)
            res = (await browser_pool.fetch(url, s.SELECTORS.get("card", []))
                   if s.needs_browser and browser_pool.ready else await http_fetch(url))
            (OUT / f"{n}_live.html").write_text(res.html, encoding="utf-8")
            print(f"{n}: HTTP {res.status}, {len(res.html)} bytes, {len(s.extract(res))} items")
    finally:
        await browser_pool.stop()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "iphone 15", sys.argv[2:]))