import asyncio
from dataclasses import dataclass
from datetime import date
from time import monotonic

import pandas as pd

from app.clients.alpha_vantage_client import (
    AlphaVantageAPIError,
    AlphaVantageClient,
)


@dataclass
class PriceCacheEntry:
    expires_at: float
    prices: pd.Series


class PriceHistoryService:
    CACHE_SECONDS = 60 * 60

    def __init__(self) -> None:
        self.client = AlphaVantageClient()
        self._cache: dict[str, PriceCacheEntry] = {}
        self._cache_lock = asyncio.Lock()

    async def get_daily_closes(
        self,
        symbol: str,
    ) -> pd.Series:
        ticker = symbol.strip().upper()

        if not ticker:
            raise ValueError("Ticker cannot be empty")

        now = monotonic()

        async with self._cache_lock:
            cached = self._cache.get(ticker)

            if (
                cached is not None
                and cached.expires_at > now
            ):
                return cached.prices.copy()

        payload = await self.client.get_daily_prices(
            ticker
        )

        raw_series = payload.get(
            "Time Series (Daily)"
        )

        if not isinstance(raw_series, dict):
            raise AlphaVantageAPIError(
                f"No daily price data found for {ticker}"
            )

        rows: list[tuple[date, float]] = []

        for date_text, values in raw_series.items():
            try:
                price_date = date.fromisoformat(
                    date_text
                )

                close = float(values["4. close"])
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            if close <= 0:
                continue

            rows.append((price_date, close))

        if len(rows) < 3:
            raise AlphaVantageAPIError(
                f"Insufficient price history for {ticker}"
            )

        rows.sort(key=lambda row: row[0])

        prices = pd.Series(
            data=[row[1] for row in rows],
            index=pd.to_datetime(
                [row[0] for row in rows]
            ),
            name=ticker,
            dtype="float64",
        )

        async with self._cache_lock:
            self._cache[ticker] = PriceCacheEntry(
                expires_at=(
                    monotonic()
                    + self.CACHE_SECONDS
                ),
                prices=prices,
            )

        return prices.copy()


price_history_service = PriceHistoryService()