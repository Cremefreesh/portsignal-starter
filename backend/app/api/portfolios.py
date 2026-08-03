from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.schemas.portfolio import (
    MarketRegime,
    PortfolioCreate,
    PortfolioSummary,
    RiskMetrics,
)
from app.services.market_regime import calculate_market_regime
from app.services.risk import calculate_risk_metrics

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("", response_model=list[PortfolioSummary])
def list_portfolios() -> list[PortfolioSummary]:
    return [
        PortfolioSummary(
            id="demo-portfolio",
            name="Archie's Portfolio",
            benchmark_ticker="SPY",
            base_currency="GBP",
            total_value=18240.50,
            day_change_pct=0.84,
            positions_count=6,
        )
    ]


@router.post("", response_model=PortfolioCreate, status_code=201)
def create_portfolio(payload: PortfolioCreate) -> PortfolioCreate:
    return payload


@router.get("/{portfolio_id}/risk", response_model=RiskMetrics)
def get_portfolio_risk(portfolio_id: str) -> RiskMetrics:
    if portfolio_id != "demo-portfolio":
        raise HTTPException(status_code=404, detail="Portfolio not found")

    settings = get_settings()

    portfolio_returns = [
        0.004, -0.006, 0.009, 0.002, -0.011, 0.014, 0.003, -0.004,
        0.008, 0.005, -0.003, 0.012, -0.007, 0.004, 0.006, -0.002,
    ]
    benchmark_returns = [
        0.003, -0.004, 0.007, 0.001, -0.008, 0.010, 0.002, -0.003,
        0.006, 0.004, -0.002, 0.008, -0.005, 0.003, 0.004, -0.001,
    ]
    weights = [0.26, 0.21, 0.18, 0.14, 0.12, 0.09]

    result = calculate_risk_metrics(
        portfolio_returns=portfolio_returns,
        benchmark_returns=benchmark_returns,
        weights=weights,
        risk_free_rate=settings.risk_free_rate,
        market_risk_premium=settings.market_risk_premium,
    )
    return RiskMetrics(**result)


@router.get("/{portfolio_id}/market-regime", response_model=MarketRegime)
def get_market_regime(portfolio_id: str) -> MarketRegime:
    if portfolio_id != "demo-portfolio":
        raise HTTPException(status_code=404, detail="Portfolio not found")

    result = calculate_market_regime(
        market_momentum=0.08,
        market_volatility=0.19,
        safe_haven_demand=-0.01,
        junk_bond_spread=0.035,
        breadth=0.62,
    )
    return MarketRegime(**result)
