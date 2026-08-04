import asyncio

from app.clients.finnhub_client import FinnhubClient
from app.repositories.watchlist_repository import (
    watchlist_repository,
)
from app.schemas.watchlist import (
    WatchlistItem,
    WatchlistResponse,
)
from app.services.market_data_service import (
    market_data_service,
)


class WatchlistService:
    def __init__(self) -> None:
        self.client = FinnhubClient()

    async def get_watchlist(
        self,
    ) -> WatchlistResponse:
        watchlist = (
            watchlist_repository
            .get_or_create_main_watchlist()
        )

        stored_items = (
            watchlist_repository.list_items(
                watchlist["id"]
            )
        )

        async def hydrate(
            row: dict,
        ) -> WatchlistItem:
            ticker = row["ticker"]

            quote, profile = await asyncio.gather(
                market_data_service.get_quote(ticker),
                self.client.get_company_profile(ticker),
            )

            return WatchlistItem(
                id=row["id"],
                ticker=ticker,
                company_name=(
                    str(profile.get("name"))
                    if profile.get("name")
                    else ticker
                ),
                industry=(
                    str(profile["finnhubIndustry"])
                    if profile.get("finnhubIndustry")
                    else None
                ),
                logo_url=(
                    str(profile["logo"])
                    if profile.get("logo")
                    else None
                ),
                current_price=quote.current_price,
                change=quote.change,
                change_percent=quote.change_percent,
                previous_close=quote.previous_close,
            )

        results = await asyncio.gather(
            *[
                hydrate(item)
                for item in stored_items
            ],
            return_exceptions=True,
        )

        items: list[WatchlistItem] = []
        warnings: list[str] = []

        for stored, result in zip(
            stored_items,
            results,
        ):
            if isinstance(result, Exception):
                warnings.append(
                    f"Could not load "
                    f"{stored['ticker']}: {result}"
                )
                continue

            items.append(result)

        return WatchlistResponse(
            id=watchlist["id"],
            name=watchlist["name"],
            items=items,
            warnings=warnings,
        )

    async def add_ticker(
        self,
        ticker: str,
    ) -> WatchlistResponse:
        clean_ticker = ticker.strip().upper()

        # Validate before storing.
        await market_data_service.get_quote(
            clean_ticker
        )

        watchlist = (
            watchlist_repository
            .get_or_create_main_watchlist()
        )

        try:
            watchlist_repository.add_item(
                watchlist["id"],
                clean_ticker,
            )
        except Exception as error:
            if "duplicate" not in str(error).lower():
                raise

        return await self.get_watchlist()

    async def remove_item(
        self,
        item_id: str,
    ) -> WatchlistResponse:
        deleted = (
            watchlist_repository.remove_item(
                item_id
            )
        )

        if not deleted:
            raise ValueError(
                "Watchlist item not found"
            )

        return await self.get_watchlist()


watchlist_service = WatchlistService()