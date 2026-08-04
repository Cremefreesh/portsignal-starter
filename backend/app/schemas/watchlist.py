from pydantic import BaseModel, Field


class WatchlistItemCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)


class WatchlistItem(BaseModel):
    id: str
    ticker: str
    company_name: str
    industry: str | None
    logo_url: str | None

    current_price: float
    change: float
    change_percent: float
    previous_close: float


class WatchlistResponse(BaseModel):
    id: str
    name: str
    items: list[WatchlistItem]
    warnings: list[str]