from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.clients.finnhub_client import (
    FinnhubAPIError,
)
from app.schemas.screener import (
    ScreenerRequest,
    ScreenerResponse,
)
from app.services.screener_service import (
    screener_service,
)

router = APIRouter(
    prefix="/screener",
    tags=["screener"],
)


@router.post(
    "",
    response_model=ScreenerResponse,
)
async def run_screener(
    payload: ScreenerRequest,
) -> ScreenerResponse:
    try:
        return await screener_service.screen(
            payload
        )
    except FinnhubAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error