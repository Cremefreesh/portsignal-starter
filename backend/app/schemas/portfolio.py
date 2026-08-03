from pydantic import BaseModel, Field


class PositionCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)
    quantity: float = Field(gt=0)
    average_cost: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class PositionUpdate(BaseModel):
    quantity: float | None = Field(default=None, gt=0)
    average_cost: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class PositionResponse(BaseModel):
    id: str
    ticker: str
    quantity: float
    average_cost: float
    currency: str


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    benchmark_ticker: str = Field(default="SPY", min_length=1, max_length=20)
    base_currency: str = Field(default="GBP", min_length=3, max_length=3)
    positions: list[PositionCreate] = Field(default_factory=list)


class PortfolioResponse(BaseModel):
    id: str
    name: str
    benchmark_ticker: str
    base_currency: str
    positions: list[PositionResponse] = Field(default_factory=list)


class PortfolioSummary(BaseModel):
    id: str
    name: str
    benchmark_ticker: str
    base_currency: str
    positions_count: int
    total_cost: float


class RiskMetrics(BaseModel):
    annualised_return: float
    annualised_volatility: float
    beta: float
    capm_expected_return: float
    sharpe_ratio: float | None
    maximum_drawdown: float
    historical_var_95: float
    concentration_hhi: float
    effective_number_of_holdings: float
