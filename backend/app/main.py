from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.news import router as news_router
from app.api.portfolios import router as portfolios_router
from app.core.config import get_settings
from app.api.market_data import (
    router as market_data_router,
)
from app.api.analytics import (
    router as analytics_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Portfolio intelligence and personalised financial news.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolios_router, prefix="/api")
app.include_router(news_router, prefix="/api")
app.include_router(market_data_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
