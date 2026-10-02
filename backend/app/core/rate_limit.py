import asyncio
import random
import time
import uuid
from collections import defaultdict, deque
from app.config import settings
from app.core.cache import cache
from app.core.errors import RateLimitExceeded

class SlidingWindowLimiter:
    """Per-key sliding window. Redis sorted sets, or in-memory deques as fallback."""

    def __init__(self) -> None:
        self._mem: dict[str, deque[float]] = defaultdict(deque)

    async def hit(self, key: str, limit: int, window: int) -> int:
        """Records a hit. Returns 0 if allowed, else retry-after seconds."""
        now = time.time()
        r = cache.redis
        if r:
            k = f"rl:{key}:{window}"
            try:
                pipe = r.pipeline()
                pipe.zremrangebyscore(k, 0, now - window)
                pipe.zcard(k)
                _, count = await pipe.execute()
                if count >= limit:
                    oldest = await r.zrange(k, 0, 0, withscores=True)
                    return max(1, int(oldest[0][1] + window - now) + 1) if oldest else window
                await r.zadd(k, {f"{now}-{uuid.uuid4().hex[:6]}": now})
                await r.expire(k, window)
                return 0
            except Exception:
                pass  # fall through to memory
        dq = self._mem[f"{key}:{window}"]
        while dq and dq[0] <= now - window:
            dq.popleft()
        if len(dq) >= limit:
            return max(1, int(dq[0] + window - now) + 1)
        dq.append(now)
        return 0

    async def check_ip(self, ip: str) -> None:
        for limit, window in ((settings.rate_limit_per_min, 60), (settings.rate_limit_per_hour, 3600)):
            retry = await self.hit(f"ip:{ip}", limit, window)
            if retry:
                raise RateLimitExceeded(retry)

class DomainLimiter:
    """Politeness: max 1 request per `delay` seconds per domain (+ jitter)."""

    def __init__(self, delay: float) -> None:
        self.delay = delay
        self._last: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def wait(self, domain: str) -> None:
        async with self._locks[domain]:
            elapsed = time.monotonic() - self._last.get(domain, 0)
            gap = self.delay - elapsed
            if gap > 0:
                await asyncio.sleep(gap + random.uniform(0, 0.5))
            self._last[domain] = time.monotonic()

ip_limiter = SlidingWindowLimiter()
domain_limiter = DomainLimiter(settings.domain_delay_seconds)