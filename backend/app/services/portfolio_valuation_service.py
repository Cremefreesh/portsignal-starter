import asyncio

from app.repositories.portfolio_repository import (
    portfolio_repository,
)
from app.schemas.market_data import (
    PortfolioValuation,
    ValuedPosition,
)
from app.services.market_data_service import (
    market_data_service,
)


class PortfolioValuationService:
    async def value_portfolio(
        self,
        portfolio_id: str,
    ) -> PortfolioValuation | None:
        portfolio = portfolio_repository.get_portfolio(
            portfolio_id
        )

        if portfolio is None:
            return None

        warnings: list[str] = []

        usd_positions = [
            position
            for position in portfolio.positions
            if position.currency.upper() == "USD"
        ]

        excluded_positions = [
            position
            for position in portfolio.positions
            if position.currency.upper() != "USD"
        ]

        if excluded_positions:
            excluded_tickers = ", ".join(
                position.ticker
                for position in excluded_positions
            )

            warnings.append(
                "FX conversion is not implemented yet. "
                f"Excluded non-USD positions: {excluded_tickers}."
            )

        quote_results = await asyncio.gather(
            *[
                market_data_service.get_quote(
                    position.ticker
                )
                for position in usd_positions
            ],
            return_exceptions=True,
        )

        valued_positions: list[ValuedPosition] = []

        for position, result in zip(
            usd_positions,
            quote_results,
        ):
            if isinstance(result, Exception):
                warnings.append(
                    f"Could not retrieve {position.ticker}: "
                    f"{result}"
                )
                continue

            quote = result

            cost_basis = (
                position.quantity
                * position.average_cost
            )

            market_value = (
                position.quantity
                * quote.current_price
            )

            total_gain = market_value - cost_basis

            total_gain_percent = (
                total_gain / cost_basis * 100
                if cost_basis > 0
                else None
            )

            previous_value = (
                position.quantity
                * quote.previous_close
            )

            day_change = (
                market_value - previous_value
            )

            valued_positions.append(
                ValuedPosition(
                    position_id=position.id,
                    ticker=position.ticker,
                    quantity=position.quantity,
                    average_cost=position.average_cost,
                    currency=position.currency,
                    current_price=round(
                        quote.current_price,
                        4,
                    ),
                    previous_close=round(
                        quote.previous_close,
                        4,
                    ),
                    cost_basis=round(
                        cost_basis,
                        2,
                    ),
                    market_value=round(
                        market_value,
                        2,
                    ),
                    total_gain=round(
                        total_gain,
                        2,
                    ),
                    total_gain_percent=(
                        round(total_gain_percent, 2)
                        if total_gain_percent is not None
                        else None
                    ),
                    day_change=round(
                        day_change,
                        2,
                    ),
                    day_change_percent=round(
                        quote.change_percent,
                        2,
                    ),
                )
            )

        total_cost_basis = sum(
            position.cost_basis
            for position in valued_positions
        )

        total_market_value = sum(
            position.market_value
            for position in valued_positions
        )

        total_gain = (
            total_market_value - total_cost_basis
        )

        total_gain_percent = (
            total_gain / total_cost_basis * 100
            if total_cost_basis > 0
            else None
        )

        previous_total_value = sum(
            position.quantity
            * position.previous_close
            for position in valued_positions
        )

        total_day_change = (
            total_market_value
            - previous_total_value
        )

        total_day_change_percent = (
            total_day_change
            / previous_total_value
            * 100
            if previous_total_value > 0
            else None
        )

        return PortfolioValuation(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            valuation_currency="USD",
            total_cost_basis=round(
                total_cost_basis,
                2,
            ),
            total_market_value=round(
                total_market_value,
                2,
            ),
            total_gain=round(
                total_gain,
                2,
            ),
            total_gain_percent=(
                round(total_gain_percent, 2)
                if total_gain_percent is not None
                else None
            ),
            total_day_change=round(
                total_day_change,
                2,
            ),
            total_day_change_percent=(
                round(total_day_change_percent, 2)
                if total_day_change_percent is not None
                else None
            ),
            positions=valued_positions,
            warnings=warnings,
        )


portfolio_valuation_service = (
    PortfolioValuationService()
)