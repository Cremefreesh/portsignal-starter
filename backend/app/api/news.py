from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/portfolio/{portfolio_id}")
def get_portfolio_news(portfolio_id: str) -> list[dict]:
    return [
        {
            "id": "demo-news-1",
            "headline": "Example portfolio-relevant market story",
            "summary": "This placeholder demonstrates the response shape.",
            "source": "Demo Source",
            "published_at": datetime.now(timezone.utc),
            "affected_tickers": ["NVDA", "MSFT"],
            "affected_portfolio_weight": 0.44,
            "sentiment": "neutral",
            "importance": "high",
            "relevance_score": 0.91,
            "why_it_matters": "The affected holdings represent 44% of this portfolio.",
        }
    ]
