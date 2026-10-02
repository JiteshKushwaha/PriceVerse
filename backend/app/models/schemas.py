from pydantic import BaseModel, Field
class Offer(BaseModel):
    type: str
    text: str
    estimated_saving_inr: float | None = None

class Delivery(BaseModel):
    text: str | None = None
    estimated_date: str | None = None
    estimated_days: int | None = None
    free: bool = False

class Product(BaseModel):
    id: str
    site: str
    name: str
    image_url: str | None = None
    specs: dict[str, str] = Field(default_factory=dict)
    price: float = Field(gt=0)
    mrp: float | None = None
    currency: str = "INR"
    discount_percent: float | None = None
    discount_amount: float | None = None
    offers: list[Offer] = Field(default_factory=list)
    delivery: Delivery = Field(default_factory=Delivery)
    rating: float | None = None
    review_count: int | None = None
    in_stock: bool = True
    sponsored: bool = False
    url: str
    score: float = 0.0
    badges: list[str] = Field(default_factory=list)
    source: str = "scrape"       # scrape | google_snippet | demo
    verified: bool = True
    stale: bool = False

class SiteStatus(BaseModel):
    site: str
    status: str                  # searching | ok | empty | blocked | timeout | error
    duration_ms: int = 0
    error: str | None = None
    message: str | None = None
    min_price: float | None = None
    result_count: int = 0

class QueryInfo(BaseModel):
    raw: str
    clean: str
    brand: str | None = None
    tokens: list[str] = Field(default_factory=list)
    attributes: dict[str, str] = Field(default_factory=dict)

class ScraperResult(BaseModel):
    site: str
    status: str
    error: str | None = None
    items: list[dict] = Field(default_factory=list)
    duration_ms: int = 0

class SearchResponse(BaseModel):
    query: QueryInfo
    cached: bool = False
    cached_at: str | None = None
    demo: bool = False
    generated_at: str
    took_ms: int
    sites: list[SiteStatus]
    results: list[Product]
    summary: dict

class SearchBody(BaseModel):
    q: str