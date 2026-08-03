import numpy as np
import pandas as pd

TRADING_DAYS = 252


def _as_series(values: list[float], name: str) -> pd.Series:
    series = pd.Series(values, dtype="float64", name=name).dropna()
    if len(series) < 3:
        raise ValueError(f"{name} requires at least three observations")
    return series


def calculate_risk_metrics(
    portfolio_returns: list[float],
    benchmark_returns: list[float],
    weights: list[float],
    risk_free_rate: float,
    market_risk_premium: float,
) -> dict[str, float | None]:
    portfolio = _as_series(portfolio_returns, "portfolio_returns")
    benchmark = _as_series(benchmark_returns, "benchmark_returns")

    aligned = pd.concat([portfolio, benchmark], axis=1).dropna()
    if len(aligned) < 3:
        raise ValueError("Not enough overlapping return observations")

    portfolio = aligned.iloc[:, 0]
    benchmark = aligned.iloc[:, 1]

    mean_daily = float(portfolio.mean())
    annualised_return = (1 + mean_daily) ** TRADING_DAYS - 1
    annualised_volatility = float(portfolio.std(ddof=1) * np.sqrt(TRADING_DAYS))

    benchmark_variance = float(benchmark.var(ddof=1))
    beta = (
        float(portfolio.cov(benchmark) / benchmark_variance)
        if benchmark_variance > 0
        else 0.0
    )

    capm_expected_return = risk_free_rate + beta * market_risk_premium
    sharpe_ratio = (
        (annualised_return - risk_free_rate) / annualised_volatility
        if annualised_volatility > 0
        else None
    )

    wealth = (1 + portfolio).cumprod()
    running_peak = wealth.cummax()
    drawdowns = wealth / running_peak - 1
    maximum_drawdown = float(drawdowns.min())

    historical_var_95 = float(-np.quantile(portfolio, 0.05))

    clean_weights = np.asarray(weights, dtype="float64")
    if clean_weights.size == 0 or clean_weights.sum() <= 0:
        raise ValueError("At least one positive portfolio weight is required")

    clean_weights = clean_weights / clean_weights.sum()
    concentration_hhi = float(np.square(clean_weights).sum())
    effective_number = float(1 / concentration_hhi)

    return {
        "annualised_return": round(float(annualised_return), 6),
        "annualised_volatility": round(annualised_volatility, 6),
        "beta": round(beta, 6),
        "capm_expected_return": round(float(capm_expected_return), 6),
        "sharpe_ratio": round(float(sharpe_ratio), 6) if sharpe_ratio is not None else None,
        "maximum_drawdown": round(maximum_drawdown, 6),
        "historical_var_95": round(historical_var_95, 6),
        "concentration_hhi": round(concentration_hhi, 6),
        "effective_number_of_holdings": round(effective_number, 3),
    }
