import asyncio

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.repositories.portfolio_repository import (
    portfolio_repository,
)
from app.schemas.analytics import (
    PortfolioAnalytics,
    PortfolioHistoryPoint,
)
from app.services.portfolio_valuation_service import (
    portfolio_valuation_service,
)
from app.services.price_history_service import (
    price_history_service,
)


TRADING_DAYS = 252


class PortfolioAnalyticsService:
    async def analyse_portfolio(
        self,
        portfolio_id: str,
    ) -> PortfolioAnalytics | None:
        portfolio = portfolio_repository.get_portfolio(
            portfolio_id
        )

        if portfolio is None:
            return None

        valuation = (
            await portfolio_valuation_service
            .value_portfolio(portfolio_id)
        )

        if valuation is None:
            return None

        warnings = list(valuation.warnings)

        valued_positions = valuation.positions

        if not valued_positions:
            raise ValueError(
                "The portfolio has no valued positions"
            )

        total_market_value = sum(
            position.market_value
            for position in valued_positions
        )

        if total_market_value <= 0:
            raise ValueError(
                "Portfolio market value must be positive"
            )

        weights = {
            position.ticker: (
                position.market_value
                / total_market_value
            )
            for position in valued_positions
        }

        symbols = list(weights.keys())

        price_results = await asyncio.gather(
            *[
                price_history_service
                .get_daily_closes(symbol)
                for symbol in symbols
            ],
            return_exceptions=True,
        )

        price_series: dict[str, pd.Series] = {}

        for symbol, result in zip(
            symbols,
            price_results,
        ):
            if isinstance(result, Exception):
                warnings.append(
                    f"Historical data unavailable "
                    f"for {symbol}: {result}"
                )
                continue

            price_series[symbol] = result

        if not price_series:
            raise ValueError(
                "No historical price data could be loaded"
            )

        benchmark_symbol = (
            portfolio.benchmark_ticker
            .strip()
            .upper()
        )

        benchmark_prices = (
            await price_history_service
            .get_daily_closes(benchmark_symbol)
        )

        prices_frame = pd.concat(
            price_series.values(),
            axis=1,
            join="inner",
        ).dropna()

        if len(prices_frame) < 20:
            raise ValueError(
                "At least 20 overlapping price "
                "observations are required"
            )

        available_symbols = [
            column
            for column in prices_frame.columns
        ]

        available_weights = np.array(
            [
                weights[str(symbol)]
                for symbol in available_symbols
            ],
            dtype="float64",
        )

        available_weights = (
            available_weights
            / available_weights.sum()
        )

        asset_returns = (
            prices_frame
            .pct_change()
            .dropna()
        )

        portfolio_returns = pd.Series(
            asset_returns.to_numpy()
            @ available_weights,
            index=asset_returns.index,
            name="portfolio",
        )

        benchmark_returns = (
            benchmark_prices
            .pct_change()
            .dropna()
            .rename("benchmark")
        )

        aligned_returns = pd.concat(
            [
                portfolio_returns,
                benchmark_returns,
            ],
            axis=1,
            join="inner",
        ).dropna()

        if len(aligned_returns) < 20:
            raise ValueError(
                "Insufficient overlap with benchmark"
            )

        portfolio_returns = (
            aligned_returns["portfolio"]
        )

        benchmark_returns = (
            aligned_returns["benchmark"]
        )

        settings = get_settings()

        annualised_return = (
            (1 + portfolio_returns.mean())
            ** TRADING_DAYS
            - 1
        )

        annualised_volatility = (
            portfolio_returns.std(ddof=1)
            * np.sqrt(TRADING_DAYS)
        )

        benchmark_variance = (
            benchmark_returns.var(ddof=1)
        )

        beta = (
            portfolio_returns.cov(
                benchmark_returns
            )
            / benchmark_variance
            if benchmark_variance > 0
            else 0.0
        )

        capm_expected_return = (
            settings.risk_free_rate
            + beta
            * settings.market_risk_premium
        )

        sharpe_ratio = (
            (
                annualised_return
                - settings.risk_free_rate
            )
            / annualised_volatility
            if annualised_volatility > 0
            else None
        )

        downside_returns = portfolio_returns[
            portfolio_returns < 0
        ]

        downside_deviation = (
            downside_returns.std(ddof=1)
            * np.sqrt(TRADING_DAYS)
            if len(downside_returns) > 1
            else 0.0
        )

        sortino_ratio = (
            (
                annualised_return
                - settings.risk_free_rate
            )
            / downside_deviation
            if downside_deviation > 0
            else None
        )

        cumulative_growth = (
            1 + portfolio_returns
        ).cumprod()

        rolling_peak = cumulative_growth.cummax()

        drawdown = (
            cumulative_growth
            / rolling_peak
            - 1
        )

        maximum_drawdown = float(
            drawdown.min()
        )

        historical_var_95 = float(
            -np.quantile(
                portfolio_returns,
                0.05,
            )
        )

        concentration_hhi = float(
            np.square(available_weights).sum()
        )

        effective_holdings = (
            1 / concentration_hhi
            if concentration_hhi > 0
            else 0
        )

        largest_position_weight = float(
            available_weights.max()
        )

        starting_value = total_market_value

        portfolio_value_history = (
            cumulative_growth
            / cumulative_growth.iloc[-1]
            * starting_value
        )

        history = [
            PortfolioHistoryPoint(
                date=index.date(),
                portfolio_value=round(
                    float(value),
                    2,
                ),
                cumulative_return=round(
                    float(
                        cumulative_growth.loc[index]
                        - 1
                    ),
                    6,
                ),
            )
            for index, value
            in portfolio_value_history.items()
        ]

        return PortfolioAnalytics(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            benchmark_ticker=benchmark_symbol,
            observation_count=len(
                portfolio_returns
            ),
            start_date=(
                portfolio_returns.index[0].date()
            ),
            end_date=(
                portfolio_returns.index[-1].date()
            ),
            annualised_return=round(
                float(annualised_return),
                6,
            ),
            annualised_volatility=round(
                float(annualised_volatility),
                6,
            ),
            beta=round(float(beta), 6),
            capm_expected_return=round(
                float(capm_expected_return),
                6,
            ),
            sharpe_ratio=(
                round(float(sharpe_ratio), 6)
                if sharpe_ratio is not None
                else None
            ),
            sortino_ratio=(
                round(float(sortino_ratio), 6)
                if sortino_ratio is not None
                else None
            ),
            maximum_drawdown=round(
                maximum_drawdown,
                6,
            ),
            historical_var_95=round(
                historical_var_95,
                6,
            ),
            concentration_hhi=round(
                concentration_hhi,
                6,
            ),
            effective_holdings=round(
                effective_holdings,
                3,
            ),
            largest_position_weight=round(
                largest_position_weight,
                6,
            ),
            history=history,
            warnings=warnings,
        )


portfolio_analytics_service = (
    PortfolioAnalyticsService()
)