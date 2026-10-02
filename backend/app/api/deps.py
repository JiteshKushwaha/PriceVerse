import re
from fastapi import HTTPException, Request
from app.core.rate_limit import ip_limiter
from app.utils.text import strip_html
def validate_query(q: str | None) -> str:
    if q is None:
        raise HTTPException(422, "Query is required")
    q = re.sub(r"\s+", " ", strip_html(q)).strip()
    if not 2 <= len(q) <= 100:
        raise HTTPException(422, "Query must be 2-100 characters")
    return q

def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")

async def enforce_rate_limit(request: Request) -> None:
    await ip_limiter.check_ip(client_ip(request))