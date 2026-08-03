from app.core.config import get_settings
from app.core.database import get_supabase
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PositionCreate,
    PositionResponse,
    PositionUpdate,
)


class PortfolioRepository:
    def __init__(self) -> None:
        self.supabase = get_supabase()
        self.settings = get_settings()

        if not self.settings.dev_user_id:
            raise RuntimeError("DEV_USER_ID is missing")

    def list_portfolios(self) -> list[PortfolioSummary]:
        response = (
            self.supabase
            .table("portfolios")
            .select(
                "id,name,benchmark_ticker,"
                "base_currency,positions("
                "id,ticker,quantity,average_cost,currency"
                ")"
            )
            .eq("user_id", self.settings.dev_user_id)
            .order("created_at", desc=True)
            .execute()
        )

        summaries: list[PortfolioSummary] = []

        for portfolio in response.data:
            positions = portfolio.get("positions", [])

            total_cost = sum(
                float(position["quantity"])
                * float(position["average_cost"])
                for position in positions
            )

            summaries.append(
                PortfolioSummary(
                    id=portfolio["id"],
                    name=portfolio["name"],
                    benchmark_ticker=(
                        portfolio["benchmark_ticker"]
                    ),
                    base_currency=portfolio["base_currency"],
                    positions_count=len(positions),
                    total_cost=round(total_cost, 2),
                )
            )

        return summaries

    def get_portfolio(
        self,
        portfolio_id: str,
    ) -> PortfolioResponse | None:
        response = (
            self.supabase
            .table("portfolios")
            .select(
                "id,name,benchmark_ticker,"
                "base_currency,positions("
                "id,ticker,quantity,average_cost,currency"
                ")"
            )
            .eq("id", portfolio_id)
            .eq("user_id", self.settings.dev_user_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            return None

        return self._map_portfolio(response.data)

    def create_portfolio(
        self,
        payload: PortfolioCreate,
    ) -> PortfolioResponse:
        portfolio_payload = {
            "user_id": self.settings.dev_user_id,
            "name": payload.name.strip(),
            "benchmark_ticker": (
                payload.benchmark_ticker.strip().upper()
            ),
            "base_currency": (
                payload.base_currency.strip().upper()
            ),
        }

        portfolio_response = (
            self.supabase
            .table("portfolios")
            .insert(portfolio_payload)
            .execute()
        )

        if not portfolio_response.data:
            raise RuntimeError(
                "Supabase did not return the created portfolio"
            )

        portfolio = portfolio_response.data[0]
        portfolio_id = portfolio["id"]

        if payload.positions:
            position_rows = [
                {
                    "portfolio_id": portfolio_id,
                    "ticker": position.ticker.strip().upper(),
                    "quantity": position.quantity,
                    "average_cost": position.average_cost,
                    "currency": (
                        position.currency.strip().upper()
                    ),
                }
                for position in payload.positions
            ]

            try:
                (
                    self.supabase
                    .table("positions")
                    .insert(position_rows)
                    .execute()
                )
            except Exception:
                # Avoid leaving an empty portfolio behind if
                # inserting one of its positions fails.
                (
                    self.supabase
                    .table("portfolios")
                    .delete()
                    .eq("id", portfolio_id)
                    .eq(
                        "user_id",
                        self.settings.dev_user_id,
                    )
                    .execute()
                )
                raise

        created = self.get_portfolio(portfolio_id)

        if created is None:
            raise RuntimeError(
                "Created portfolio could not be reloaded"
            )

        return created

    def add_position(
        self,
        portfolio_id: str,
        payload: PositionCreate,
    ) -> PositionResponse | None:
        portfolio = self.get_portfolio(portfolio_id)

        if portfolio is None:
            return None

        ticker = payload.ticker.strip().upper()

        if any(
            position.ticker == ticker
            for position in portfolio.positions
        ):
            raise ValueError(
                f"{ticker} already exists in this portfolio"
            )

        response = (
            self.supabase
            .table("positions")
            .insert(
                {
                    "portfolio_id": portfolio_id,
                    "ticker": ticker,
                    "quantity": payload.quantity,
                    "average_cost": payload.average_cost,
                    "currency": (
                        payload.currency.strip().upper()
                    ),
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Supabase did not return the created position"
            )

        return self._map_position(response.data[0])

    def update_position(
        self,
        portfolio_id: str,
        position_id: str,
        payload: PositionUpdate,
    ) -> PositionResponse | None:
        portfolio = self.get_portfolio(portfolio_id)

        if portfolio is None:
            return None

        owns_position = any(
            position.id == position_id
            for position in portfolio.positions
        )

        if not owns_position:
            return None

        update_data = payload.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "currency" in update_data:
            update_data["currency"] = (
                update_data["currency"].strip().upper()
            )

        if not update_data:
            return next(
                position
                for position in portfolio.positions
                if position.id == position_id
            )

        response = (
            self.supabase
            .table("positions")
            .update(update_data)
            .eq("id", position_id)
            .eq("portfolio_id", portfolio_id)
            .execute()
        )

        if not response.data:
            return None

        return self._map_position(response.data[0])

    def delete_position(
        self,
        portfolio_id: str,
        position_id: str,
    ) -> bool:
        portfolio = self.get_portfolio(portfolio_id)

        if portfolio is None:
            return False

        owns_position = any(
            position.id == position_id
            for position in portfolio.positions
        )

        if not owns_position:
            return False

        (
            self.supabase
            .table("positions")
            .delete()
            .eq("id", position_id)
            .eq("portfolio_id", portfolio_id)
            .execute()
        )

        return True

    def delete_portfolio(
        self,
        portfolio_id: str,
    ) -> bool:
        portfolio = self.get_portfolio(portfolio_id)

        if portfolio is None:
            return False

        (
            self.supabase
            .table("portfolios")
            .delete()
            .eq("id", portfolio_id)
            .eq("user_id", self.settings.dev_user_id)
            .execute()
        )

        return True

    @staticmethod
    def _map_position(
        row: dict,
    ) -> PositionResponse:
        return PositionResponse(
            id=row["id"],
            ticker=row["ticker"],
            quantity=float(row["quantity"]),
            average_cost=float(row["average_cost"]),
            currency=row["currency"],
        )

    def _map_portfolio(
        self,
        row: dict,
    ) -> PortfolioResponse:
        return PortfolioResponse(
            id=row["id"],
            name=row["name"],
            benchmark_ticker=row["benchmark_ticker"],
            base_currency=row["base_currency"],
            positions=[
                self._map_position(position)
                for position in row.get("positions", [])
            ],
        )


portfolio_repository = PortfolioRepository()