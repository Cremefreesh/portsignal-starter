from datetime import datetime

from pydantic import BaseModel


class PortfolioNewsArticle(BaseModel):
    id: str
    headline: str
    summary: str
    source: str
    additional_sources: list[str]

    url: str
    image_url: str | None
    published_at: datetime

    affected_tickers: list[str]
    affected_portfolio_weight: float

    category: str
    importance: str
    relevance_score: float
    why_it_matters: str

    duplicate_count: int


class PortfolioNewsBrief(BaseModel):
    material_story_count: int
    affected_portfolio_weight: float
    summary: str


class PortfolioNewsFeed(BaseModel):
    portfolio_id: str
    portfolio_name: str
    generated_at: datetime

    brief: PortfolioNewsBrief
    articles: list[PortfolioNewsArticle]
    warnings: list[str]