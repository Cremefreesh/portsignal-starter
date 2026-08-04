import asyncio

from app.clients.finnhub_client import FinnhubClient
from app.schemas.screener import (
    ScreenerRequest,
    ScreenerResponse,
    ScreenerResult,
)
from app.services.market_data_service import (
    market_data_service,
)


class ScreenerService:
    def __init__(self) -> None:
        self.client = FinnhubClient()

    async def screen(
        self,
        request: ScreenerRequest,
    ) -> ScreenerResponse:
        clean_tickers = list(
            dict.fromkeys(
                ticker.strip().upper()
                for ticker in request.tickers
                if ticker.strip()
            )
        )

        async def inspect_ticker(
            ticker: str,
        ) -> ScreenerResult:
            quote, profile, financials = (
                await asyncio.gather(
                    market_data_service.get_quote(
                        ticker
                    ),
                    self.client.get_company_profile(
                        ticker
                    ),
                    self.client.get_basic_financials(
                        ticker
                    ),
                )
            )

            metrics = financials.get(
                "metric",
                {},
            )

            return ScreenerResult(
                ticker=ticker,
                company_name=str(
                    profile.get("name")
                    or ticker
                ),
                industry=(
                    str(profile["finnhubIndustry"])
                    if profile.get("finnhubIndustry")
                    else None
                ),
                exchange=(
                    str(profile["exchange"])
                    if profile.get("exchange")
                    else None
                ),
                logo_url=(
                    str(profile["logo"])
                    if profile.get("logo")
                    else None
                ),
                current_price=quote.current_price,
                daily_change_percent=(
                    quote.change_percent
                ),
                market_cap_millions=(
                    float(
                        profile[
                            "marketCapitalization"
                        ]
                    )
                    if profile.get(
                        "marketCapitalization"
                    )
                    is not None
                    else None
                ),
                pe_ratio=self._number(
                    metrics.get("peTTM")
                ),
                dividend_yield_percent=(
                    self._number(
                        metrics.get(
                            "dividendYieldIndicatedAnnual"
                        )
                    )
                ),
                fifty_two_week_high=self._number(
                    metrics.get("52WeekHigh")
                ),
                fifty_two_week_low=self._number(
                    metrics.get("52WeekLow")
                ),
            )

        raw_results = await asyncio.gather(
            *[
                inspect_ticker(ticker)
                for ticker in clean_tickers
            ],
            return_exceptions=True,
        )

        candidates: list[ScreenerResult] = []
        rejected_tickers: list[str] = []
        warnings: list[str] = []

        for ticker, result in zip(
            clean_tickers,
            raw_results,
        ):
            if isinstance(result, Exception):
                rejected_tickers.append(ticker)
                warnings.append(
                    f"{ticker}: {result}"
                )
                continue

            if self._matches(result, request):
                candidates.append(result)

        candidates.sort(
            key=lambda item: (
                item.market_cap_millions or 0
            ),
            reverse=True,
        )

        return ScreenerResponse(
            results=candidates,
            rejected_tickers=rejected_tickers,
            warnings=warnings,
        )

    @staticmethod
    def _number(
        value: object,
    ) -> float | None:
        try:
            if value is None:
                return None

            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _matches(
        result: ScreenerResult,
        request: ScreenerRequest,
    ) -> bool:
        if (
            request.minimum_price is not None
            and result.current_price
            < request.minimum_price
        ):
            return False

        if (
            request.maximum_price is not None
            and result.current_price
            > request.maximum_price
        ):
            return False

        if (
            request.minimum_daily_change
            is not None
            and result.daily_change_percent
            < request.minimum_daily_change
        ):
            return False

        if (
            request.minimum_market_cap
            is not None
            and (
                result.market_cap_millions
                is None
                or result.market_cap_millions
                < request.minimum_market_cap
            )
        ):
            return False

        if (
            request.maximum_pe is not None
            and (
                result.pe_ratio is None
                or result.pe_ratio
                > request.maximum_pe
            )
        ):
            return False

        if request.industry:
            industry = (
                result.industry or ""
            ).lower()

            if (
                request.industry.lower()
                not in industry
            ):
                return False

        return True


screener_service = ScreenerService()