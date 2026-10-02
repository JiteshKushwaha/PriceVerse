from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class ScraperError(Exception):
    kind = "unexpected"

class BlockedError(ScraperError):
    kind = "blocked"

class ScrapeTimeout(ScraperError):
    kind = "timeout"

class ParseError(ScraperError):
    kind = "parse_error"

class NetworkError(ScraperError):
    kind = "network_error"

class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded, retry in {retry_after}s")

def install_handlers(app: FastAPI) -> None:
    @app.exception_handler(RateLimitExceeded)
    async def _rl(_: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": "Slow down, hero!", "retry_after": exc.retry_after},
            headers={"Retry-After": str(exc.retry_after)},
        )
    @app.exception_handler(Exception)
    async def _any(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": f"Internal error: {type(exc).__name__}"})