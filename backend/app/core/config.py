from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PortSignal API"
    environment: str = "development"
    frontend_origin: str = "http://localhost:5173"

    supabase_url: str = ""
    supabase_service_role_key: str = ""

    alpha_vantage_api_key: str = ""
    finnhub_api_key: str = ""
    fred_api_key: str = ""

    risk_free_rate: float = 0.043
    market_risk_premium: float = 0.050

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
