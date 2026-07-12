import pytest

from app.core.config import Settings


def test_production_env_aliases_are_supported(monkeypatch) -> None:
    monkeypatch.setenv("BUILDIQ_ENV", "production")
    monkeypatch.setenv("BUILDIQ_SECRET_KEY", "production-secret-value-with-at-least-32-chars")
    monkeypatch.setenv(
        "BUILDIQ_ALLOWED_ORIGINS",
        "https://app.example.invalid,https://admin.example.invalid",
    )

    settings = Settings(_env_file=None)

    assert settings.environment == "production"
    assert settings.jwt_secret_key == "production-secret-value-with-at-least-32-chars"
    assert settings.cors_allowed_origins == [
        "https://app.example.invalid",
        "https://admin.example.invalid",
    ]


def test_production_rejects_unsafe_defaults(monkeypatch) -> None:
    monkeypatch.setenv("BUILDIQ_ENV", "production")
    monkeypatch.setenv("BUILDIQ_SECRET_KEY", "short")
    monkeypatch.setenv("BUILDIQ_DEBUG", "true")
    monkeypatch.setenv("BUILDIQ_ALLOWED_ORIGINS", "http://localhost:5173,*")
    monkeypatch.setenv("BUILDIQ_STORAGE_PATH", "storage")
    monkeypatch.setenv("BUILDIQ_DATABASE_URL", "sqlite:///./buildiq.db")

    with pytest.raises(ValueError, match="Invalid production configuration"):
        Settings(_env_file=None)


def test_legacy_cors_origin_env_name_accepts_json_list(monkeypatch) -> None:
    monkeypatch.setenv("BUILDIQ_CORS_ALLOWED_ORIGINS", '["https://app.example.invalid"]')

    settings = Settings(_env_file=None)

    assert settings.cors_allowed_origins == ["https://app.example.invalid"]
