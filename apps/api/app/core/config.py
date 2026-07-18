from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CONTROL_PLANE_",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "ClearGlass Artemis Commerce Control Plane"
    environment: str = "development"
    database_url: str = "sqlite+pysqlite:///./control-plane.db"
    api_key: str = Field(default="development-only-change-me-32-characters")
    allowed_origins: list[str] = []
    high_risk_price_delta_percent: int = Field(default=20, ge=1, le=100)
    high_risk_inventory_delta: int = Field(default=100, ge=1)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("CONTROL_PLANE_API_KEY must contain at least 32 characters")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
