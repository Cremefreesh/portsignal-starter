import asyncio
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.clients.finnhub_client import (
    FinnhubClient,
)
from app.repositories.portfolio_repository import (
    portfolio_repository,
)
from app.schemas.news import (
    PortfolioNewsArticle,
    PortfolioNewsFeed,
)
from app.services.portfolio_valuation_service import (
    portfolio_valuation_service,
)


class PortfolioNewsService:
    def __init__(self) -> None:
        self.client = FinnhubClient()

    async def get_portfolio_news(
        self,
        portfolio_id: str,
        days: int = 7,
    ) -> PortfolioNewsFeed | None:
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

        if valuation.total_market_value <= 0:
            raise ValueError(
                "Portfolio market value must be positive"
            )

        weights = {
            position.ticker: (
                position.market_value
                / valuation.total_market_value
            )
            for position in valuation.positions
        }

        now = datetime.now(timezone.utc)
        from_date = (
            now - timedelta(days=days)
        ).date().isoformat()
        to_date = now.date().isoformat()

        symbols = list(weights.keys())

        news_results = await asyncio.gather(
            *[
                self.client.get_company_news(
                    symbol=symbol,
                    from_date=from_date,
                    to_date=to_date,
                )
                for symbol in symbols
            ],
            return_exceptions=True,
        )

        article_map: dict[str, dict] = {}

        for symbol, result in zip(
            symbols,
            news_results,
        ):
            if isinstance(result, Exception):
                warnings.append(
                    f"News unavailable for "
                    f"{symbol}: {result}"
                )
                continue

            for raw_article in result:
                article_id = str(
                    raw_article.get("id")
                    or raw_article.get("url")
                    or raw_article.get("headline")
                )

                if not article_id:
                    continue

                article = article_map.setdefault(
                    article_id,
                    {
                        "raw": raw_article,
                        "tickers": set(),
                    },
                )

                article["tickers"].add(symbol)

                related_text = str(
                    raw_article.get("related", "")
                )

                for possible_symbol in symbols:
                    if possible_symbol in related_text:
                        article["tickers"].add(
                            possible_symbol
                        )

        articles: list[
            PortfolioNewsArticle
        ] = []

        for article_id, article_data in (
            article_map.items()
        ):
            raw = article_data["raw"]

            affected_tickers = sorted(
                article_data["tickers"]
            )

            affected_weight = sum(
                weights.get(ticker, 0)
                for ticker in affected_tickers
            )

            published_timestamp = int(
                raw.get("datetime", 0) or 0
            )

            if published_timestamp <= 0:
                continue

            age_hours = max(
                0,
                (
                    now
                    - datetime.fromtimestamp(
                        published_timestamp,
                        tz=timezone.utc,
                    )
                ).total_seconds()
                / 3600,
            )

            freshness_score = max(
                0.1,
                1 - age_hours / (days * 24),
            )

            multi_holding_bonus = min(
                0.15,
                0.05
                * max(
                    0,
                    len(affected_tickers) - 1,
                ),
            )

            relevance_score = min(
                1.0,
                affected_weight
                * 0.75
                + freshness_score
                * 0.25
                + multi_holding_bonus,
            )

            if (
                affected_weight >= 0.25
                or relevance_score >= 0.75
            ):
                importance = "high"
            elif (
                affected_weight >= 0.10
                or relevance_score >= 0.45
            ):
                importance = "medium"
            else:
                importance = "low"

            ticker_text = ", ".join(
                affected_tickers
            )

            why_it_matters = (
                f"This story relates to "
                f"{ticker_text}, representing "
                f"{affected_weight * 100:.1f}% "
                f"of this portfolio."
            )

            articles.append(
                PortfolioNewsArticle(
                    id=article_id,
                    headline=str(
                        raw.get(
                            "headline",
                            "Untitled story",
                        )
                    ),
                    summary=str(
                        raw.get("summary", "")
                    ),
                    source=str(
                        raw.get(
                            "source",
                            "Unknown source",
                        )
                    ),
                    url=str(
                        raw.get("url", "")
                    ),
                    image_url=(
                        str(raw["image"])
                        if raw.get("image")
                        else None
                    ),
                    published_at=(
                        datetime.fromtimestamp(
                            published_timestamp,
                            tz=timezone.utc,
                        )
                    ),
                    affected_tickers=(
                        affected_tickers
                    ),
                    affected_portfolio_weight=round(
                        affected_weight,
                        6,
                    ),
                    importance=importance,
                    relevance_score=round(
                        relevance_score,
                        6,
                    ),
                    why_it_matters=(
                        why_it_matters
                    ),
                )
            )

        articles.sort(
            key=lambda article: (
                article.relevance_score,
                article.published_at,
            ),
            reverse=True,
        )

        return PortfolioNewsFeed(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            generated_at=now,
            articles=articles[:50],
            warnings=warnings,
        )


portfolio_news_service = PortfolioNewsService()