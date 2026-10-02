from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

SITE_DOMAINS = [
    "amazon.in", "flipkart.com", "myntra.com", "croma.com",
    "reliancedigital.in", "ajio.com", "snapdeal.com", "tatacliq.com",
]
# Per-site trust constant (0-1) used in ranking.
TRUST = {
    "amazon.in": 0.95, "flipkart.com": 0.93, "croma.com": 0.90, "reliancedigital.in": 0.88,
    "tatacliq.com": 0.86, "myntra.com": 0.90, "ajio.com": 0.85, "snapdeal.com": 0.70,
}
SITE_LABELS = {
    "amazon.in": "Amazon", "flipkart.com": "Flipkart", "myntra.com": "Myntra", "croma.com": "Croma",
    "reliancedigital.in": "Reliance Digital", "ajio.com": "AJIO", "snapdeal.com": "Snapdeal",
    "tatacliq.com": "Tata CLiQ",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    serpapi_key: str = ""
    google_cse_key: str = ""
    google_cse_cx: str = ""
    proxy_url: str = ""            # comma-separated list supported (rotating)
    scraper_api_key: str = ""      # ScraperAPI key, used only when blocked
    enabled_scrapers: str = "amazon_in,flipkart,myntra,croma,reliance_digital,ajio,snapdeal,tatacliq"
    cache_ttl_seconds: int = 1800
    rate_limit_per_min: int = 10
    rate_limit_per_hour: int = 100
    demo_mode: bool = False
    allowed_origins: str = "http://localhost:5173,http://localhost:8080"
    database_url: str = "sqlite+aiosqlite:///./data/prices.db"
    global_timeout: float = 25.0
    scraper_timeout: float = 18.0
    max_concurrency: int = 4
    results_per_site: int = 8
    use_browser: bool = True
    fetch_details: bool = False    # open top product page for specs/offers
    domain_delay_seconds: float = 2.0
    log_level: str = "INFO"

    @property
    def scraper_list(self) -> list[str]:
        return [s.strip() for s in self.enabled_scrapers.split(",") if s.strip()]

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def proxies(self) -> list[str]:
        return [p.strip() for p in self.proxy_url.split(",") if p.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
settings = get_settings()