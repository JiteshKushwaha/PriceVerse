import asyncio
import logging
import random
from dataclasses import dataclass, field
from app.config import settings
from app.scrapers.anti_bot import pick_proxy, random_ua

logger = logging.getLogger("browser")

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
window.chrome = window.chrome || { runtime: {} };
"""
BLOCKED_TYPES = {"image", "font", "media"}
BLOCKED_HOSTS = ("google-analytics", "googletagmanager", "doubleclick", "facebook", "hotjar", "clarity.ms")

@dataclass
class FetchResult:
    status: int
    html: str
    url: str
    json_responses: list = field(default_factory=list)

class BrowserPool:
    def __init__(self) -> None:
        self._pw = None
        self.browser = None

    @property
    def ready(self) -> bool:
        return self.browser is not None

    async def start(self) -> None:
        try:
            from playwright.async_api import async_playwright
            self._pw = await async_playwright().start()
            proxy = pick_proxy()
            self.browser = await self._pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
                proxy={"server": proxy} if proxy else None,
            )
            logger.info("chromium started")
        except Exception as exc:
            logger.warning(f"playwright unavailable, browser scrapers will use httpx: {exc}")
            self.browser = None

    async def stop(self) -> None:
        try:
            if self.browser:
                await self.browser.close()
            if self._pw:
                await self._pw.stop()
        except Exception:
            pass

    async def _route(self, route) -> None:
        req = route.request
        if req.resource_type in BLOCKED_TYPES or any(h in req.url for h in BLOCKED_HOSTS):
            await route.abort()
        else:
            await route.continue_()

    async def fetch(self, url: str, wait_selectors: list[str], timeout_ms: int = 15000,
                    capture_json: bool = True) -> FetchResult:
        assert self.browser is not None
        ctx = await self.browser.new_context(
            user_agent=random_ua(),
            viewport={"width": random.choice([1366, 1440, 1536]), "height": random.choice([768, 900])},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={"Accept-Language": "en-IN,en;q=0.9"},
        )
        captured: list = []
        try:
            await ctx.add_init_script(STEALTH_JS)
            page = await ctx.new_page()
            await page.route("**/*", self._route)

            async def on_response(resp) -> None:
                try:
                    if "json" in (resp.headers.get("content-type") or "") and len(captured) < 25:
                        captured.append(await resp.json())
                except Exception:
                    pass

            if capture_json:
                page.on("response", lambda r: asyncio.ensure_future(on_response(r)))
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            status = resp.status if resp else 0
            for sel in wait_selectors:
                try:
                    await page.wait_for_selector(sel, timeout=4000)
                    break
                except Exception:
                    continue
            for _ in range(2):  # trigger lazy loading
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight / 2)")
                await page.wait_for_timeout(500)
            try:
                await page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass
            return FetchResult(status=status, html=await page.content(), url=page.url, json_responses=captured)
        finally:
            await ctx.close()

browser_pool = BrowserPool()