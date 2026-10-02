from fastapi import APIRouter
from app.config import SITE_LABELS, TRUST, settings
from app.core.cache import cache
from app.scrapers import registry
from app.scrapers.browser_pool import browser_pool

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "cache": cache.backend, "browser": browser_pool.ready, "demo_mode": settings.demo_mode}

@router.get("/sites")
async def sites() -> list[dict]:
    return [{"name": s.name, "site": s.domain, "label": SITE_LABELS.get(s.domain, s.domain),
             "needs_browser": s.needs_browser, "trust": TRUST.get(s.domain),
             "mode": "demo" if settings.demo_mode else ("browser" if s.needs_browser and browser_pool.ready else "http")}
            for s in registry.enabled()]