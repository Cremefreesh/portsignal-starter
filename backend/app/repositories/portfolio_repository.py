from copy import deepcopy
from uuid import uuid4

from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PositionCreate,
    PositionResponse,
    PositionUpdate,
)


class PortfolioRepository:
    """
    Temporary in-memory repository.

    This lets us build and test the complete API before replacing
    this implementation with Supabase.
    """

    def __init__(self) -> None:
        self._portfolios: dict[str, PortfolioResponse] = {}

    def list_portfolios(self) -> list[PortfolioSummary]:
        summaries: list[PortfolioSummary] = []

        for portfolio in self._portfolios.values():
            total_cost = sum(
                position.quantity * position.average_cost
                for position in portfolio.positions
            )

            summaries.append(
                PortfolioSummary(
                    id=portfolio.id,
                    name=portfolio.name,
                    benchmark_ticker=portfolio.benchmark_ticker,
                    base_currency=portfolio.base_currency,
                    positions_count=len(portfolio.positions),
                    total_cost=round(total_cost, 2),
                )
            )

        return summaries

    def get_portfolio(self, portfolio_id: str) -> PortfolioResponse | None:
        portfolio = self._portfolios.get(portfolio_id)

        if portfolio is None:
            return None

        return deepcopy(portfolio)

    def create_portfolio(
        self,
        payload: PortfolioCreate,
    ) -> PortfolioResponse:
        portfolio_id = str(uuid4())

        positions = [
            self._build_position(position)
            for position in payload.positions
        ]

        portfolio = PortfolioResponse(
            id=portfolio_id,
            name=payload.name.strip(),
            benchmark_ticker=payload.benchmark_ticker.strip().upper(),
            base_currency=payload.base_currency.strip().upper(),
            positions=positions,
        )

        self._portfolios[portfolio_id] = portfolio

        return deepcopy(portfolio)

    def add_position(
        self,
        portfolio_id: str,
        payload: PositionCreate,
    ) -> PositionResponse | None:
        portfolio = self._portfolios.get(portfolio_id)

        if portfolio is None:
            return None

        ticker = payload.ticker.strip().upper()

        existing_position = next(
            (
                position
                for position in portfolio.positions
                if position.ticker == ticker
            ),
            None,
        )

        if existing_position is not None:
            raise ValueError(
                f"{ticker} already exists in this portfolio"
            )

        position = self._build_position(payload)
        portfolio.positions.append(position)

        return position.model_copy(deep=True)

    def update_position(
        self,
        portfolio_id: str,
        position_id: str,
        payload: PositionUpdate,
    ) -> PositionResponse | None:
        portfolio = self._portfolios.get(portfolio_id)

        if portfolio is None:
            return None

        position = next(
            (
                position
                for position in portfolio.positions
                if position.id == position_id
            ),
            None,
        )

        if position is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "currency" and value is not None:
                value = value.upper()

            setattr(position, field, value)

        return position.model_copy(deep=True)

    def delete_position(
        self,
        portfolio_id: str,
        position_id: str,
    ) -> bool:
        portfolio = self._portfolios.get(portfolio_id)

        if portfolio is None:
            return False

        original_length = len(portfolio.positions)

        portfolio.positions = [
            position
            for position in portfolio.positions
            if position.id != position_id
        ]

        return len(portfolio.positions) < original_length

    def delete_portfolio(self, portfolio_id: str) -> bool:
        if portfolio_id not in self._portfolios:
            return False

        del self._portfolios[portfolio_id]
        return True

    @staticmethod
    def _build_position(
        payload: PositionCreate,
    ) -> PositionResponse:
        return PositionResponse(
            id=str(uuid4()),
            ticker=payload.ticker.strip().upper(),
            quantity=payload.quantity,
            average_cost=payload.average_cost,
            currency=payload.currency.strip().upper(),
        )


portfolio_repository = PortfolioRepository()