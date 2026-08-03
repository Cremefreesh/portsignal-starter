from pydantic import BaseModel


class SymbolSearchResult(BaseModel):
    symbol: str
    display_symbol: str
    description: str
    security_type: str


class StockQuote(BaseModel):
    symbol: str
    current_price: float
    change: float
    change_percent: float
    day_high: float
    day_low: float
    open_price: float
    previous_close: float
    timestamp: int


class ValuedPosition(BaseModel):
    position_id: str
    ticker: str
    quantity: float
    average_cost: float
    currency: str

    current_price: float
    previous_close: float

    cost_basis: float
    market_value: float
    total_gain: float
    total_gain_percent: float | None

    day_change: float
    day_change_percent: float


class PortfolioValuation(BaseModel):
    portfolio_id: str
    portfolio_name: str
    valuation_currency: str

    total_cost_basis: float
    total_market_value: float
    total_gain: float
    total_gain_percent: float | None
    total_day_change: float
    total_day_change_percent: float | None

    positions: list[ValuedPosition]
    warnings: list[str]