import asyncio
import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from app.clients.finnhub_client import FinnhubClient
from app.repositories.portfolio_repository import (
    portfolio_repository,
)
from app.schemas.news import (
    PortfolioNewsArticle,
    PortfolioNewsBrief,
    PortfolioNewsFeed,
)
from app.services.portfolio_valuation_service import (
    portfolio_valuation_service,
)


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "earnings": (
        "earnings",
        "revenue",
        "profit",
        "quarter",
        "guidance",
        "results",
        "eps",
    ),
    "merger_acquisition": (
        "acquisition",
        "acquire",
        "merger",
        "takeover",
        "buyout",
    ),
    "regulation": (
        "regulation",
        "regulator",
        "antitrust",
        "investigation",
        "government",
        "ban",
        "tariff",
        "sanction",
    ),
    "analyst_rating": (
        "upgrade",
        "downgrade",
        "price target",
        "analyst",
        "rating",
    ),
    "product": (
        "launch",
        "announces",
        "product",
        "platform",
        "chip",
        "device",
        "service",
    ),
    "leadership": (
        "ceo",
        "cfo",
        "chairman",
        "executive",
        "resigns",
        "appointed",
    ),
    "litigation": (
        "lawsuit",
        "court",
        "legal",
        "settlement",
        "sued",
    ),
    "dividend": (
        "dividend",
        "distribution",
        "shareholder payout",
    ),
}


class PortfolioNewsService:
    MINIMUM_RELEVANCE_SCORE = 0.35

    def __init__(self) -> None:
        self.client = FinnhubClient()

    @staticmethod
    def normalise_headline(headline: str) -> str:
        cleaned = re.sub(
            r"[^a-z0-9\s]",
            " ",
            headline.lower(),
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        noise_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "of",
            "to",
            "for",
            "in",
            "on",
            "with",
        }

        return " ".join(
            word
            for word in cleaned.split()
            if word not in noise_words
        )

    @staticmethod
    def headlines_are_similar(
        first: str,
        second: str,
    ) -> bool:
        if not first or not second:
            return False

        similarity = SequenceMatcher(
            None,
            first,
            second,
        ).ratio()

        first_words = set(first.split())
        second_words = set(second.split())

        intersection = first_words & second_words
        union = first_words | second_words

        word_overlap = (
            len(intersection) / len(union)
            if union
            else 0
        )

        return (
            similarity >= 0.78
            or word_overlap >= 0.65
        )

    @staticmethod
    def classify_article(
        headline: str,
        summary: str,
    ) -> str:
        text = f"{headline} {summary}".lower()

        category_scores: dict[str, int] = {}

        for category, keywords in (
            CATEGORY_KEYWORDS.items()
        ):
            category_scores[category] = sum(
                1
                for keyword in keywords
                if keyword in text
            )

        best_category = max(
            category_scores,
            key=category_scores.get,
        )

        if category_scores[best_category] == 0:
            return "general"

        return best_category

    @staticmethod
    def calculate_evidence_score(
        ticker: str,
        headline: str,
        summary: str,
        related: str,
    ) -> float:
        ticker_lower = ticker.lower()
        headline_lower = headline.lower()
        summary_lower = summary.lower()
        related_symbols = {
            item.strip().upper()
            for item in related.split(",")
            if item.strip()
        }

        score = 0.0

        if ticker.upper() in related_symbols:
            score += 0.30

        if ticker_lower in headline_lower:
            score += 0.35

        if ticker_lower in summary_lower:
            score += 0.15

        if headline.strip():
            score += 0.10

        if summary.strip():
            score += 0.10

        return min(score, 1.0)

    async def get_portfolio_news(
        self,
        portfolio_id: str,
        days: int = 7,
        important_only: bool = True,
        category: str | None = None,
    ) -> PortfolioNewsFeed | None:
        portfolio = (
            portfolio_repository.get_portfolio(
                portfolio_id
            )
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

        candidate_articles: list[dict] = []

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
                headline = str(
                    raw_article.get(
                        "headline",
                        "",
                    )
                ).strip()

                if not headline:
                    continue

                summary = str(
                    raw_article.get(
                        "summary",
                        "",
                    )
                ).strip()

                related = str(
                    raw_article.get(
                        "related",
                        "",
                    )
                )

                evidence_score = (
                    self.calculate_evidence_score(
                        ticker=symbol,
                        headline=headline,
                        summary=summary,
                        related=related,
                    )
                )

                if evidence_score < 0.30:
                    continue

                published_timestamp = int(
                    raw_article.get(
                        "datetime",
                        0,
                    )
                    or 0
                )

                if published_timestamp <= 0:
                    continue

                published_at = (
                    datetime.fromtimestamp(
                        published_timestamp,
                        tz=timezone.utc,
                    )
                )

                candidate_articles.append(
                    {
                        "raw": raw_article,
                        "headline": headline,
                        "normalised_headline": (
                            self.normalise_headline(
                                headline
                            )
                        ),
                        "summary": summary,
                        "published_at": published_at,
                        "tickers": {symbol},
                        "evidence_scores": {
                            symbol: evidence_score
                        },
                        "sources": {
                            str(
                                raw_article.get(
                                    "source",
                                    "Unknown source",
                                )
                            )
                        },
                    }
                )

        grouped_articles: list[dict] = []

        for candidate in sorted(
            candidate_articles,
            key=lambda article: article[
                "published_at"
            ],
            reverse=True,
        ):
            duplicate_group = next(
                (
                    grouped
                    for grouped in grouped_articles
                    if self.headlines_are_similar(
                        candidate[
                            "normalised_headline"
                        ],
                        grouped[
                            "normalised_headline"
                        ],
                    )
                ),
                None,
            )

            if duplicate_group is None:
                grouped_articles.append(
                    {
                        **candidate,
                        "duplicate_count": 1,
                    }
                )
                continue

            duplicate_group["tickers"].update(
                candidate["tickers"]
            )

            duplicate_group[
                "evidence_scores"
            ].update(
                candidate["evidence_scores"]
            )

            duplicate_group["sources"].update(
                candidate["sources"]
            )

            duplicate_group[
                "duplicate_count"
            ] += 1

            if (
                candidate["published_at"]
                > duplicate_group["published_at"]
            ):
                duplicate_group.update(
                    {
                        "raw": candidate["raw"],
                        "headline": candidate[
                            "headline"
                        ],
                        "summary": candidate[
                            "summary"
                        ],
                        "published_at": candidate[
                            "published_at"
                        ],
                    }
                )

        articles: list[
            PortfolioNewsArticle
        ] = []

        for grouped in grouped_articles:
            affected_tickers = sorted(
                grouped["tickers"]
            )

            affected_weight = sum(
                weights.get(ticker, 0)
                for ticker in affected_tickers
            )

            average_evidence = sum(
                grouped[
                    "evidence_scores"
                ].values()
            ) / len(
                grouped["evidence_scores"]
            )

            age_hours = max(
                0,
                (
                    now
                    - grouped["published_at"]
                ).total_seconds()
                / 3600,
            )

            freshness_score = max(
                0.05,
                1
                - age_hours
                / max(days * 24, 1),
            )

            duplicate_bonus = min(
                0.10,
                0.025
                * (
                    grouped[
                        "duplicate_count"
                    ]
                    - 1
                ),
            )

            multi_holding_bonus = min(
                0.10,
                0.05
                * max(
                    0,
                    len(affected_tickers)
                    - 1,
                ),
            )

            relevance_score = min(
                1.0,
                average_evidence * 0.45
                + affected_weight * 0.30
                + freshness_score * 0.15
                + duplicate_bonus
                + multi_holding_bonus,
            )

            if (
                relevance_score
                < self.MINIMUM_RELEVANCE_SCORE
            ):
                continue

            article_category = (
                self.classify_article(
                    grouped["headline"],
                    grouped["summary"],
                )
            )

            if (
                category
                and category != "all"
                and article_category
                != category
            ):
                continue

            if (
                affected_weight >= 0.25
                or relevance_score >= 0.72
            ):
                importance = "high"
            elif (
                affected_weight >= 0.10
                or relevance_score >= 0.50
            ):
                importance = "medium"
            else:
                importance = "low"

            if (
                important_only
                and importance == "low"
            ):
                continue

            sources = sorted(
                grouped["sources"]
            )

            main_source = (
                sources[0]
                if sources
                else "Unknown source"
            )

            ticker_text = ", ".join(
                affected_tickers
            )

            article_id = str(
                grouped["raw"].get("id")
                or grouped["raw"].get("url")
                or grouped["headline"]
            )

            articles.append(
                PortfolioNewsArticle(
                    id=article_id,
                    headline=grouped["headline"],
                    summary=grouped["summary"],
                    source=main_source,
                    additional_sources=[
                        source
                        for source in sources
                        if source != main_source
                    ],
                    url=str(
                        grouped["raw"].get(
                            "url",
                            "",
                        )
                    ),
                    image_url=(
                        str(
                            grouped["raw"][
                                "image"
                            ]
                        )
                        if grouped["raw"].get(
                            "image"
                        )
                        else None
                    ),
                    published_at=grouped[
                        "published_at"
                    ],
                    affected_tickers=(
                        affected_tickers
                    ),
                    affected_portfolio_weight=round(
                        affected_weight,
                        6,
                    ),
                    category=article_category,
                    importance=importance,
                    relevance_score=round(
                        relevance_score,
                        6,
                    ),
                    why_it_matters=(
                        f"This story relates to "
                        f"{ticker_text}, representing "
                        f"{affected_weight * 100:.1f}% "
                        f"of this portfolio."
                    ),
                    duplicate_count=grouped[
                        "duplicate_count"
                    ],
                )
            )

        articles.sort(
            key=lambda article: (
                article.relevance_score,
                article.published_at,
            ),
            reverse=True,
        )

        articles = articles[:20]

        material_articles = [
            article
            for article in articles
            if article.importance
            in {"high", "medium"}
        ]

        materially_affected_tickers = {
            ticker
            for article in material_articles
            for ticker in article.affected_tickers
        }

        material_weight = sum(
            weights.get(ticker, 0)
            for ticker
            in materially_affected_tickers
        )

        brief_summary = (
            f"{len(material_articles)} material "
            f"{'story' if len(material_articles) == 1 else 'stories'} "
            f"affect approximately "
            f"{material_weight * 100:.1f}% "
            f"of this portfolio."
        )

        return PortfolioNewsFeed(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            generated_at=now,
            brief=PortfolioNewsBrief(
                material_story_count=len(
                    material_articles
                ),
                affected_portfolio_weight=round(
                    material_weight,
                    6,
                ),
                summary=brief_summary,
            ),
            articles=articles,
            warnings=warnings,
        )


portfolio_news_service = PortfolioNewsService()