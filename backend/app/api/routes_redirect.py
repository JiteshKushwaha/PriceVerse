from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.config import SITE_DOMAINS
from app.services.history import log_click
router = APIRouter(prefix="/api", tags=["redirect"])

@router.get("/redirect")
async def redirect(url: str, site: str = "") -> RedirectResponse:
    p = urlparse(url)
    host = (p.hostname or "").lower()
    if p.scheme not in ("http", "https") or not any(host == d or host.endswith("." + d) for d in SITE_DOMAINS):
        raise HTTPException(400, "URL host not in allow-list")
    try:
        await log_click(site or host, url)
    except Exception:
        pass
    return RedirectResponse(url, status_code=302)