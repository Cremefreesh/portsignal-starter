from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.clients.finnhub_client import (
    FinnhubAPIError,
)
from app.schemas.watchlist import (
    WatchlistItemCreate,
    WatchlistResponse,
)
from app.services.watchlist_service import (
    watchlist_service,
)

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
)


@router.get(
    "",
    response_model=WatchlistResponse,
)
async def get_watchlist() -> WatchlistResponse:
    return await watchlist_service.get_watchlist()


@router.post(
    "/items",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_watchlist_item(
    payload: WatchlistItemCreate,
) -> WatchlistResponse:
    try:
        return await watchlist_service.add_ticker(
            payload.ticker
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


@router.delete(
    "/items/{item_id}",
    response_model=WatchlistResponse,
)
async def remove_watchlist_item(
    item_id: str,
) -> WatchlistResponse:
    try:
        return await watchlist_service.remove_item(
            item_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error