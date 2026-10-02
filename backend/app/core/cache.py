import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from app.config import settings

logger = logging.getLogger("cache")

try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover
    aioredis = None


class Cache:
    """Redis JSON cache with an in-memory TTL fallback and a stampede lock."""

    def __init__(self) -> None:
        self.redis: Any = None
        self._mem: dict[str, tuple[float, str]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def connect(self) -> None:
        if aioredis is None:
            return
        try:
            client = aioredis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            self.redis = client
            logger.info("redis connected")
        except Exception as exc:
            self.redis = None
            logger.warning(f"redis unavailable, using in-memory fallback: {exc}")

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()

    @property
    def backend(self) -> str:
        return "redis" if self.redis else "memory"

    async def get_json(self, key: str) -> Any:
        try:
            if self.redis:
                raw = await self.redis.get(key)
            else:
                item = self._mem.get(key)
                raw = item[1] if item and item[0] > time.time() else None
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning(f"cache get failed: {exc}")
            return None

    async def set_json(self, key: str, value: Any, ttl: int) -> None:
        raw = json.dumps(value, default=str)
        try:
            if self.redis:
                await self.redis.set(key, raw, ex=ttl)
            else:
                self._mem[key] = (time.time() + ttl, raw)
        except Exception as exc:
            logger.warning(f"cache set failed: {exc}")

    @asynccontextmanager
    async def lock(self, key: str, timeout: int = 45) -> AsyncIterator[bool]:
        """Yields True if this caller owns the lock (should do the work)."""
        if self.redis:
            name, token = f"lock:{key}", uuid.uuid4().hex
            try:
                acquired = bool(await self.redis.set(name, token, nx=True, ex=timeout))
            except Exception:
                acquired = True
            try:
                yield acquired
            finally:
                if acquired:
                    try:
                        if await self.redis.get(name) == token:
                            await self.redis.delete(name)
                    except Exception:
                        pass
        else:
            lk = self._locks.setdefault(key, asyncio.Lock())
            if lk.locked():
                yield False
            else:
                async with lk:
                    yield True

cache = Cache()