from app.config import settings
from app.scrapers.ajio import Ajio
from app.scrapers.amazon_in import AmazonIn
from app.scrapers.base import BaseScraper
from app.scrapers.croma import Croma
from app.scrapers.flipkart import Flipkart
from app.scrapers.myntra import Myntra
from app.scrapers.reliance_digital import RelianceDigital
from app.scrapers.snapdeal import Snapdeal
from app.scrapers.tatacliq import TataCliq

# Adding a store = new file + one line here.
ALL: dict[str, type[BaseScraper]] = {
    "amazon_in": AmazonIn,
    "flipkart": Flipkart,
    "myntra": Myntra,
    "croma": Croma,
    "reliance_digital": RelianceDigital,
    "ajio": Ajio,
    "snapdeal": Snapdeal,
    "tatacliq": TataCliq,}

def enabled() -> list[BaseScraper]:
    return [ALL[n]() for n in settings.scraper_list if n in ALL]

def by_domain(domain: str) -> BaseScraper | None:
    for cls in ALL.values():
        if cls.domain == domain:
            return cls()
    return None