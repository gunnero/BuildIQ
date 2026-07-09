from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

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
    environment: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://buildiq:buildiq@localhost:5432/buildiq"
    log_level: str = "INFO"
    jwt_secret_key: str = "change-me-in-local-development-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    storage_path: str = str(REPO_ROOT / "storage")
    cors_allowed_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://127.0.0.1:5175",
        "http://localhost:5175",
        "https://buildiq.razbudise.mk",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
