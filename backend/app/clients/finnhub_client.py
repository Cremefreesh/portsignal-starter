from typing import Any

import httpx

from app.core.config import get_settings


class FinnhubAPIError(RuntimeError):
    pass


class FinnhubClient:
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.finnhub_api_key:
            raise RuntimeError("FINNHUB_API_KEY is missing")

        self.api_key = settings.finnhub_api_key

    async def _get(
        self,
        path: str,
        params: dict[str, Any],
    ) -> Any:
        request_params = {
            **params,
            "token": self.api_key,
        }

        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=15.0,
        ) as client:
            response = await client.get(
                path,
                params=request_params,
            )

        if response.status_code == 429:
            raise FinnhubAPIError(
                "Finnhub API rate limit exceeded"
            )

        if response.status_code >= 400:
            raise FinnhubAPIError(
                f"Finnhub returned HTTP {response.status_code}"
            )

        try:
            return response.json()
        except ValueError as error:
            raise FinnhubAPIError(
                "Finnhub returned invalid JSON"
            ) from error

    async def search_symbols(
        self,
        query: str,
    ) -> dict[str, Any]:
        return await self._get(
            "/search",
            {
                "q": query,
                "exchange": "US",
            },
        )

    async def get_quote(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        return await self._get(
            "/quote",
            {
                "symbol": symbol,
            },
        )

    async def get_company_profile(
    self,
    symbol: str,
    ) -> dict[str, Any]:
        payload = await self._get(
            "/stock/profile2",
            {
                "symbol": symbol,
            },
        )

        if not isinstance(payload, dict):
            raise FinnhubAPIError(
                "Finnhub returned an invalid company profile"
            )

        return payload


    async def get_basic_financials(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        payload = await self._get(
            "/stock/metric",
            {
                "symbol": symbol,
                "metric": "all",
            },
        )

        if not isinstance(payload, dict):
            raise FinnhubAPIError(
                "Finnhub returned invalid financial metrics"
            )

        return payload



    async def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict[str, Any]]:
        payload = await self._get(
            "/company-news",
            {
                "symbol": symbol,
                "from": from_date,
                "to": to_date,
            },
        )

        if not isinstance(payload, list):
            raise FinnhubAPIError(
                "Finnhub returned invalid company news"
            )

        return payload