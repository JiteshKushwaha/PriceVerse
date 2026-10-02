import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_health, routes_history, routes_redirect, routes_search
from app.config import settings
from app.core.cache import cache
from app.core.errors import install_handlers
from app.core.logging import request_id_var, setup_logging
from app.models.db import init_db
from app.scrapers.browser_pool import browser_pool
@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging(settings.log_level)
    await init_db()
    await cache.connect()
    if settings.use_browser and not settings.demo_mode:
        await browser_pool.start()
    yield
    await browser_pool.stop()
    await cache.close()

app = FastAPI(title="PriceVerse: E-Commerce Price Comparison & Product Recommendation System",
              version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=False,
                   allow_methods=["GET", "POST"], allow_headers=["*"], expose_headers=["Retry-After", "X-Request-ID"])

@app.middleware("http")
async def request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    request_id_var.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

install_handlers(app)
for r in (routes_search, routes_health, routes_history, routes_redirect):
    app.include_router(r.router)

@app.get("/")
async def root() -> dict:
    return {"name": app.title, "docs": "/docs"}