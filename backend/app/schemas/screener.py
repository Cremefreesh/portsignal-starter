from pydantic import BaseModel, Field


class ScreenerRequest(BaseModel):
    tickers: list[str] = Field(
        min_length=1,
        max_length=20,
    )

    minimum_price: float | None = Field(
        default=None,
        ge=0,
    )

    maximum_price: float | None = Field(
        default=None,
        ge=0,
    )

    minimum_market_cap: float | None = Field(
        default=None,
        ge=0,
    )

    maximum_pe: float | None = Field(
        default=None,
        ge=0,
    )

    minimum_daily_change: float | None = None
    industry: str | None = None


class ScreenerResult(BaseModel):
    ticker: str
    company_name: str
    industry: str | None
    exchange: str | None
    logo_url: str | None

    current_price: float
    daily_change_percent: float

    market_cap_millions: float | None
    pe_ratio: float | None
    dividend_yield_percent: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None


class ScreenerResponse(BaseModel):
    results: list[ScreenerResult]
    rejected_tickers: list[str]
    warnings: list[str]