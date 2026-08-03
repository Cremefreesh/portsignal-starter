import asyncio
from dataclasses import dataclass
from time import monotonic

from app.clients.finnhub_client import (
    FinnhubAPIError,
    FinnhubClient,
)
from app.schemas.market_data import (
    StockQuote,
    SymbolSearchResult,
)


@dataclass
class CacheEntry:
    expires_at: float
    quote: StockQuote


class MarketDataService:
    QUOTE_CACHE_SECONDS = 60

    def __init__(self) -> None:
        self.client = FinnhubClient()
        self._quote_cache: dict[str, CacheEntry] = {}
        self._cache_lock = asyncio.Lock()

    async def search_symbols(
        self,
        query: str,
    ) -> list[SymbolSearchResult]:
        clean_query = query.strip()

        if len(clean_query) < 1:
            return []

        payload = await self.client.search_symbols(
            clean_query
        )

        raw_results = payload.get("result", [])

        results: list[SymbolSearchResult] = []

        for item in raw_results[:10]:
            symbol = str(
                item.get("symbol", "")
            ).strip()

            if not symbol:
                continue

            results.append(
                SymbolSearchResult(
                    symbol=symbol,
                    display_symbol=str(
                        item.get("displaySymbol", symbol)
                    ),
                    description=str(
                        item.get("description", "")
                    ),
                    security_type=str(
                        item.get("type", "Unknown")
                    ),
                )
            )

        return results

    async def get_quote(
        self,
        symbol: str,
    ) -> StockQuote:
        ticker = symbol.strip().upper()

        if not ticker:
            raise ValueError("Ticker cannot be empty")

        now = monotonic()

        async with self._cache_lock:
            cached = self._quote_cache.get(ticker)

            if (
                cached is not None
                and cached.expires_at > now
            ):
                return cached.quote

        payload = await self.client.get_quote(ticker)

        current_price = float(payload.get("c", 0) or 0)
        previous_close = float(
            payload.get("pc", 0) or 0
        )

        if current_price <= 0:
            raise ValueError(
                f"No valid market quote was found for {ticker}"
            )

        quote = StockQuote(
            symbol=ticker,
            current_price=current_price,
            change=float(payload.get("d", 0) or 0),
            change_percent=float(
                payload.get("dp", 0) or 0
            ),
            day_high=float(payload.get("h", 0) or 0),
            day_low=float(payload.get("l", 0) or 0),
            open_price=float(
                payload.get("o", 0) or 0
            ),
            previous_close=previous_close,
            timestamp=int(payload.get("t", 0) or 0),
        )

        async with self._cache_lock:
            self._quote_cache[ticker] = CacheEntry(
                expires_at=(
                    monotonic()
                    + self.QUOTE_CACHE_SECONDS
                ),
                quote=quote,
            )

        return quote


market_data_service = MarketDataService()