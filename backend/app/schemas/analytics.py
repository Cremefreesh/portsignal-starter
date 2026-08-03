from datetime import date

from pydantic import BaseModel


class PortfolioHistoryPoint(BaseModel):
    date: date
    portfolio_value: float
    cumulative_return: float


class PortfolioAnalytics(BaseModel):
    portfolio_id: str
    portfolio_name: str
    benchmark_ticker: str
    observation_count: int
    start_date: date
    end_date: date

    annualised_return: float
    annualised_volatility: float

    beta: float
    capm_expected_return: float

    sharpe_ratio: float | None
    sortino_ratio: float | None

    maximum_drawdown: float
    historical_var_95: float

    concentration_hhi: float
    effective_holdings: float
    largest_position_weight: float

    history: list[PortfolioHistoryPoint]
    warnings: list[str]