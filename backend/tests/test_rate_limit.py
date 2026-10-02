from app.core.rate_limit import SlidingWindowLimiter

async def test_sliding_window_memory():
    lim = SlidingWindowLimiter()
    for _ in range(3):
        assert await lim.hit("t", 3, 60) == 0
    retry = await lim.hit("t", 3, 60)
    assert 1 <= retry <= 61