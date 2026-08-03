from typing import Any

import httpx

from app.core.config import get_settings


class AlphaVantageAPIError(RuntimeError):
    pass


class AlphaVantageClient:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.alpha_vantage_api_key:
            raise RuntimeError(
                "ALPHA_VANTAGE_API_KEY is missing"
            )

        self.api_key = settings.alpha_vantage_api_key

    async def _get(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        request_params = {
            **params,
            "apikey": self.api_key,
        }

        async with httpx.AsyncClient(
            timeout=20.0,
        ) as client:
            response = await client.get(
                self.BASE_URL,
                params=request_params,
            )

        if response.status_code >= 400:
            raise AlphaVantageAPIError(
                "Alpha Vantage request failed: "
                f"HTTP {response.status_code}"
            )

        try:
            payload = response.json()
        except ValueError as error:
            raise AlphaVantageAPIError(
                "Alpha Vantage returned invalid JSON"
            ) from error

        if "Error Message" in payload:
            raise AlphaVantageAPIError(
                str(payload["Error Message"])
            )

        if "Information" in payload:
            raise AlphaVantageAPIError(
                str(payload["Information"])
            )

        if "Note" in payload:
            raise AlphaVantageAPIError(
                str(payload["Note"])
            )

        return payload

    async def get_daily_prices(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        return await self._get(
            {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",
            }
        )