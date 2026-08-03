from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PortSignal API"
    environment: str = "development"
    frontend_origin: str = "http://localhost:5173"

    supabase_url: str = "https://ttugyrxkormpmlyeojxe.supabase.co"
    supabase_service_role_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR0dWd5cnhrb3JtcG1seWVvanhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTc3NzYwNCwiZXhwIjoyMTAxMzUzNjA0fQ.IcL9bXr0emTuOzUbnLSOKpaVviRX4nRyu9Pn_pxEVlc"
    dev_user_id: str = "49402a7a-97b6-4008-9935-71b8b73c5f26"

    alpha_vantage_api_key: str = ""
    finnhub_api_key: str = ""
    fred_api_key: str = ""

    risk_free_rate: float = 0.043
    market_risk_premium: float = 0.05

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()