import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.api.deps import enforce_rate_limit, validate_query
from app.core.errors import RateLimitExceeded
from app.models.schemas import SearchBody, SearchResponse
from app.services.orchestrator import run_search

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_get(request: Request, q: str, fresh: bool = False) -> dict:
    query = validate_query(q)
    await enforce_rate_limit(request)
    return await run_search(query, fresh=fresh)


@router.post("/search", response_model=SearchResponse)
async def search_post(request: Request, body: SearchBody) -> dict:
    query = validate_query(body.q)
    await enforce_rate_limit(request)
    return await run_search(query)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.get("/search/stream")
async def search_stream(request: Request, q: str, fresh: bool = False) -> StreamingResponse:
    """Server-Sent Events: `site` per-store status, then `result` (full response) or `error`."""
    query = validate_query(q)
    queue: asyncio.Queue[str | None] = asyncio.Queue()

    async def progress(event: str, data: dict) -> None:
        await queue.put(_sse(event, data))

    async def worker() -> None:
        try:
            await enforce_rate_limit(request)
            result = await run_search(query, progress, fresh=fresh)
            await queue.put(_sse("result", result))
        except RateLimitExceeded as exc:
            await queue.put(_sse("error", {"status": 429, "message": "Slow down, hero!", "retry_after": exc.retry_after}))
        except Exception as exc:
            await queue.put(_sse("error", {"status": 500, "message": type(exc).__name__}))
        finally:
            await queue.put(None)

    async def gen():
        task = asyncio.create_task(worker())
        try:
            yield ": connected\n\n"
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
                    continue
                if item is None:
                    break
                yield item
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})