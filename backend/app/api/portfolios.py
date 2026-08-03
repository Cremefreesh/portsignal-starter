from fastapi import APIRouter, HTTPException, Response, status

from app.repositories.portfolio_repository import portfolio_repository
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PositionCreate,
    PositionResponse,
    PositionUpdate,
)

router = APIRouter(
    prefix="/portfolios",
    tags=["portfolios"],
)


@router.get(
    "",
    response_model=list[PortfolioSummary],
)
def list_portfolios() -> list[PortfolioSummary]:
    return portfolio_repository.list_portfolios()


@router.post(
    "",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio(
    payload: PortfolioCreate,
) -> PortfolioResponse:
    return portfolio_repository.create_portfolio(payload)


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
def get_portfolio(
    portfolio_id: str,
) -> PortfolioResponse:
    portfolio = portfolio_repository.get_portfolio(portfolio_id)

    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return portfolio


@router.post(
    "/{portfolio_id}/positions",
    response_model=PositionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_position(
    portfolio_id: str,
    payload: PositionCreate,
) -> PositionResponse:
    try:
        position = portfolio_repository.add_position(
            portfolio_id,
            payload,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return position


@router.patch(
    "/{portfolio_id}/positions/{position_id}",
    response_model=PositionResponse,
)
def update_position(
    portfolio_id: str,
    position_id: str,
    payload: PositionUpdate,
) -> PositionResponse:
    position = portfolio_repository.update_position(
        portfolio_id,
        position_id,
        payload,
    )

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio or position not found",
        )

    return position


@router.delete(
    "/{portfolio_id}/positions/{position_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_position(
    portfolio_id: str,
    position_id: str,
) -> Response:
    deleted = portfolio_repository.delete_position(
        portfolio_id,
        position_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio or position not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_portfolio(
    portfolio_id: str,
) -> Response:
    deleted = portfolio_repository.delete_portfolio(portfolio_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)