import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Union

from pydantic import AliasChoices, Field, field_validator, model_validator
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
            "https://app.example.invalid",
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

    @model_validator(mode="after")
    def validate_production_gate(self) -> "Settings":
        if self.environment.lower() != "production":
            return self

        errors: list[str] = []
        normalized_secret = self.jwt_secret_key.strip().lower()
        if (
            not self.jwt_secret_key
            or normalized_secret == "change-me-in-local-development-secret-key"
            or normalized_secret.startswith(("replace_with", "replace-with", "change-me"))
            or len(self.jwt_secret_key) < 32
        ):
            errors.append("BUILDIQ_SECRET_KEY must be a unique value of at least 32 characters")
        if self.debug:
            errors.append("BUILDIQ_DEBUG must be false in production")
        if not self.cors_allowed_origins:
            errors.append("BUILDIQ_ALLOWED_ORIGINS must contain at least one origin")
        for origin in self.cors_allowed_origins:
            normalized = origin.strip().lower()
            if normalized == "*":
                errors.append("wildcard CORS origins are not allowed in production")
            elif not normalized.startswith("https://"):
                errors.append(f"production CORS origin must use HTTPS: {origin}")
            elif any(
                marker in normalized
                for marker in ("localhost", "127.0.0.1", "0.0.0.0", "dev.", "development")
            ):
                errors.append(f"local/development CORS origin is not allowed in production: {origin}")
        storage = Path(self.storage_path)
        if not storage.is_absolute():
            errors.append("BUILDIQ_STORAGE_PATH must be absolute in production")
        if self.database_url.lower().startswith(("sqlite:", "sqlite+")):
            errors.append("SQLite databases are not allowed in production")
        if errors:
            raise ValueError("Invalid production configuration: " + "; ".join(errors))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
