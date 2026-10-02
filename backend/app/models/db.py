import os
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.config import settings
if settings.database_url.startswith("sqlite"):
    path = settings.database_url.split("///")[-1]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

engine = create_async_engine(settings.database_url, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_hash: Mapped[str] = mapped_column(String(40), index=True)
    query: Mapped[str] = mapped_column(String(120))
    site: Mapped[str] = mapped_column(String(40), index=True)
    product_url: Mapped[str] = mapped_column(String(1000))
    product_name: Mapped[str] = mapped_column(String(300))
    price: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

class ClickLog(Base):
    __tablename__ = "click_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site: Mapped[str] = mapped_column(String(40))
    url: Mapped[str] = mapped_column(String(1000))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)