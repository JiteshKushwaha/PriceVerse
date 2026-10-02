import os
import pathlib
import pytest

os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("REDIS_URL", "redis://localhost:1/0")  # force in-memory fallback
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test.db")
FIXTURES = pathlib.Path(__file__).parent / "fixtures"

@pytest.fixture
def fixture_html():
    return lambda name: (FIXTURES / name).read_text(encoding="utf-8")