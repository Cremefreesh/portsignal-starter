from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.clients.alpha_vantage_client import (
    AlphaVantageAPIError,
)
from app.schemas.analytics import (
    PortfolioAnalytics,
)
from app.services.portfolio_analytics_service import (
    portfolio_analytics_service,
)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get(
    "/portfolios/{portfolio_id}",
    response_model=PortfolioAnalytics,
)
async def get_portfolio_analytics(
    portfolio_id: str,
) -> PortfolioAnalytics:
    try:
        analytics = (
            await portfolio_analytics_service
            .analyse_portfolio(portfolio_id)
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except AlphaVantageAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    if analytics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return analytics