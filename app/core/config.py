from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Email Verification API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    api_key: str = Field(default="", alias="API_KEY")
    rapidapi_proxy_secret: str = Field(default="", alias="RAPIDAPI_PROXY_SECRET")

    enable_smtp_check: bool = Field(default=False, alias="ENABLE_SMTP_CHECK")
    smtp_timeout_seconds: int = Field(default=10, alias="SMTP_TIMEOUT_SECONDS", ge=1, le=60)
    dns_timeout_seconds: int = Field(default=5, alias="DNS_TIMEOUT_SECONDS", ge=1, le=30)
    max_bulk_emails: int = Field(default=100, alias="MAX_BULK_EMAILS", ge=1, le=1000)
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS", ge=1, le=120)

    cors_allow_origins: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")
    cors_allow_methods: str = Field(default="*", alias="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="*", alias="CORS_ALLOW_HEADERS")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(sorted(allowed))}")
        return upper

    @staticmethod
    def _split_csv(value: str) -> List[str]:
        value = value.strip()
        if not value:
            return []
        if value == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def cors_origins(self) -> List[str]:
        return self._split_csv(self.cors_allow_origins)

    @property
    def cors_methods(self) -> List[str]:
        return self._split_csv(self.cors_allow_methods)

    @property
    def cors_headers(self) -> List[str]:
        return self._split_csv(self.cors_allow_headers)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
