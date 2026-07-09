from app.core.config import Settings


def test_production_env_aliases_are_supported(monkeypatch) -> None:
    monkeypatch.setenv("BUILDIQ_ENV", "production")
    monkeypatch.setenv("BUILDIQ_SECRET_KEY", "production-secret")
    monkeypatch.setenv(
        "BUILDIQ_ALLOWED_ORIGINS",
        "https://buildiq.kalveri.com,https://admin.buildiq.kalveri.com",
    )

    settings = Settings(_env_file=None)

    assert settings.environment == "production"
    assert settings.jwt_secret_key == "production-secret"
    assert settings.cors_allowed_origins == [
        "https://buildiq.kalveri.com",
        "https://admin.buildiq.kalveri.com",
    ]


def test_legacy_cors_origin_env_name_accepts_json_list(monkeypatch) -> None:
    monkeypatch.setenv("BUILDIQ_CORS_ALLOWED_ORIGINS", '["https://buildiq.kalveri.com"]')

    settings = Settings(_env_file=None)

    assert settings.cors_allowed_origins == ["https://buildiq.kalveri.com"]
