from datetime import date
from pydantic import BaseModel, Field


class PositionInput(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)
    quantity: float = Field(gt=0)
    average_cost: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    benchmark_ticker: str = "SPY"
    base_currency: str = "USD"
    positions: list[PositionInput] = []


class PortfolioSummary(BaseModel):
    id: str
    name: str
    benchmark_ticker: str
    base_currency: str
    total_value: float
    day_change_pct: float
    positions_count: int


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


class MarketRegime(BaseModel):
    score: int = Field(ge=0, le=100)
    label: str
    as_of: date
    components: dict[str, float]
