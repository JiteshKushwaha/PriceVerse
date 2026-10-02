import random
from urllib.parse import quote
from app.config import settings
from app.core.errors import BlockedError

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",]

BLOCK_MARKERS = [
    "enter the characters you see below", "validatecaptcha", "robot check",
    "access denied", "just a moment...", "attention required", "are you a human",
    "unusual traffic", "request blocked", "pardon our interruption",]

def random_ua() -> str:
    return random.choice(USER_AGENTS)

def browser_headers(ua: str | None = None) -> dict[str, str]:
    return {
        "User-Agent": ua or random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",}

def pick_proxy() -> str | None:
    return random.choice(settings.proxies) if settings.proxies else None

def scraper_api_url(url: str) -> str:
    return f"https://api.scraperapi.com/?api_key={settings.scraper_api_key}&country_code=in&url={quote(url, safe='')}"

def detect_block(status: int, html: str, url: str) -> None:
    """Raises BlockedError on CAPTCHA / WAF / empty pages. Never tries to solve CAPTCHAs."""
    if status in (403, 429, 503):
        raise BlockedError(f"HTTP {status}")
    if "validatecaptcha" in url.lower() or "/captcha" in url.lower():
        raise BlockedError("CAPTCHA redirect")
    head = (html or "")[:30000].lower()
    for marker in BLOCK_MARKERS:
        if marker in head and len(html) < 200_000:
            raise BlockedError(f"Block page detected: '{marker}'")
    if len(html or "") < 1500:
        raise BlockedError("Empty/suspiciously small page")