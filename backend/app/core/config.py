import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Union

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        env_prefix="BUILDIQ_",
        extra="ignore",
    )

    app_name: str = "BuildIQ Backend"
    service_name: str = "buildiq-backend"
    app_version: str = "0.1.0"
    environment: str = Field(
        default="local",
        validation_alias=AliasChoices("BUILDIQ_ENV", "BUILDIQ_ENVIRONMENT"),
    )
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://buildiq:buildiq@localhost:5432/buildiq"
    log_level: str = "INFO"
    jwt_secret_key: str = Field(
        default="change-me-in-local-development-secret-key",
        validation_alias=AliasChoices("BUILDIQ_SECRET_KEY", "BUILDIQ_JWT_SECRET_KEY"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    storage_path: str = str(REPO_ROOT / "storage")
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(
        default=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:5174",
            "http://localhost:5174",
            "http://127.0.0.1:5175",
            "http://localhost:5175",
            "https://buildiq.razbudise.mk",
        ],
        validation_alias=AliasChoices("BUILDIQ_ALLOWED_ORIGINS", "BUILDIQ_CORS_ALLOWED_ORIGINS"),
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value: Union[str, list[str]]) -> list[str]:
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value.startswith("["):
                parsed_value = json.loads(stripped_value)
                if isinstance(parsed_value, list):
                    return [str(origin).strip() for origin in parsed_value if str(origin).strip()]

            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
