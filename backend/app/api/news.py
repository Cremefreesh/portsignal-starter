from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from app.clients.finnhub_client import (
    FinnhubAPIError,
)
from app.schemas.news import PortfolioNewsFeed
from app.services.portfolio_news_service import (
    portfolio_news_service,
)

router = APIRouter(
    prefix="/news",
    tags=["news"],
)


@router.get(
    "/portfolios/{portfolio_id}",
    response_model=PortfolioNewsFeed,
)
async def get_portfolio_news(
    portfolio_id: str,
    days: int = Query(
        default=7,
        ge=1,
        le=30,
    ),
) -> PortfolioNewsFeed:
    try:
        feed = (
            await portfolio_news_service
            .get_portfolio_news(
                portfolio_id=portfolio_id,
                days=days,
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error
    except FinnhubAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    if feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return feed