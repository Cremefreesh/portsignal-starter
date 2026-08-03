from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from app.clients.finnhub_client import (
    FinnhubAPIError,
)
from app.schemas.market_data import (
    PortfolioValuation,
    StockQuote,
    SymbolSearchResult,
)
from app.services.market_data_service import (
    market_data_service,
)
from app.services.portfolio_valuation_service import (
    portfolio_valuation_service,
)

router = APIRouter(
    prefix="/market-data",
    tags=["market data"],
)


@router.get(
    "/search",
    response_model=list[SymbolSearchResult],
)
async def search_symbols(
    query: str = Query(
        min_length=1,
        max_length=100,
    ),
) -> list[SymbolSearchResult]:
    try:
        return await market_data_service.search_symbols(
            query
        )
    except FinnhubAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error


@router.get(
    "/quote/{symbol}",
    response_model=StockQuote,
)
async def get_quote(
    symbol: str,
) -> StockQuote:
    try:
        return await market_data_service.get_quote(
            symbol
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except FinnhubAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error


@router.get(
    "/portfolios/{portfolio_id}/valuation",
    response_model=PortfolioValuation,
)
async def get_portfolio_valuation(
    portfolio_id: str,
) -> PortfolioValuation:
    try:
        valuation = (
            await portfolio_valuation_service
            .value_portfolio(portfolio_id)
        )
    except FinnhubAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    if valuation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return valuation