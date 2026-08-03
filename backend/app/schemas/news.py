from datetime import datetime

from pydantic import BaseModel


class PortfolioNewsArticle(BaseModel):
    id: str
    headline: str
    summary: str
    source: str
    url: str
    image_url: str | None
    published_at: datetime

    affected_tickers: list[str]
    affected_portfolio_weight: float

    importance: str
    relevance_score: float
    why_it_matters: str


class PortfolioNewsFeed(BaseModel):
    portfolio_id: str
    portfolio_name: str
    generated_at: datetime

    articles: list[PortfolioNewsArticle]
    warnings: list[str]