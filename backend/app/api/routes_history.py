from fastapi import APIRouter, Query
from app.api.deps import validate_query
from app.config import settings
from app.services.history import get_history
from app.services.query_normalizer import normalize

router = APIRouter(prefix="/api", tags=["history"])

@router.get("/history")
async def history(q: str, days: int = Query(30, ge=1, le=365)) -> dict:
    clean = normalize(validate_query(q)).clean
    return {"query": clean, "days": days, "points": await get_history(clean, days, synthesize=settings.demo_mode)}