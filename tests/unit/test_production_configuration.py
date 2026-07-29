from collections.abc import Mapping

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def valid_production_environment() -> dict[str, str]:
    return {
        "APP_ENV": "production",
        "PERSISTENCE_BACKEND": "postgresql",
        "DATABASE_URL": "postgresql+asyncpg://church:secret@database/church",
        "AUTH_TOKEN_SECRET": "Q7vZ2mN8pL4xR9tY6wK3cF1hJ5sD0aB7uE2iG8oP4qM",
        "AUTH_COOKIE_SECURE": "true",
        "EMAIL_BACKEND": "smtp",
        "SMTP_HOST": "smtp.example.com",
        "SMTP_SENDER": "no-reply@example.com",
        "SMTP_USE_TLS": "true",
        "PUBLIC_APP_URL": "https://app.example.com",
        "CORS_ALLOWED_ORIGINS": "https://app.example.com",
        "CORS_ALLOW_CREDENTIALS": "true",
        "ALLOWED_HOSTS": "api.example.com",
    }


def configure_environment(monkeypatch: pytest.MonkeyPatch, values: Mapping[str, str]) -> None:
    for name, value in values.items():
        monkeypatch.setenv(name, value)


@pytest.mark.parametrize(
    ("variable", "insecure_value"),
    [
        ("PERSISTENCE_BACKEND", "memory"),
        ("DATABASE_URL", ""),
        ("DATABASE_URL", "sqlite+aiosqlite:///production.db"),
        ("AUTH_TOKEN_SECRET", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
        ("AUTH_COOKIE_SECURE", "false"),
        ("EMAIL_BACKEND", "memory"),
        ("SMTP_HOST", ""),
        ("SMTP_SENDER", ""),
        ("SMTP_USE_TLS", "false"),
        ("PUBLIC_APP_URL", "http://app.example.com"),
        ("CORS_ALLOWED_ORIGINS", "http://app.example.com"),
        ("CORS_ALLOW_CREDENTIALS", "false"),
        ("ALLOWED_HOSTS", "*"),
    ],
)
def test_rejects_insecure_production_configuration(
    monkeypatch: pytest.MonkeyPatch, variable: str, insecure_value: str
) -> None:
    environment = valid_production_environment()
    environment[variable] = insecure_value
    configure_environment(monkeypatch, environment)

    with pytest.raises(ValueError, match=variable):
        create_app()


def test_requires_explicit_stable_token_secret_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment = valid_production_environment()
    del environment["AUTH_TOKEN_SECRET"]
    monkeypatch.delenv("AUTH_TOKEN_SECRET", raising=False)
    configure_environment(monkeypatch, environment)

    with pytest.raises(ValueError, match="AUTH_TOKEN_SECRET"):
        create_app()


def test_accepts_secure_production_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_environment(monkeypatch, valid_production_environment())

    application = create_app()

    assert application.state.auth_cookie_secure is True
    assert application.docs_url is None
    assert application.redoc_url is None
    assert application.openapi_url is None

    with TestClient(application, base_url="https://api.example.com") as client:
        response = client.get("/health")

    assert response.headers["strict-transport-security"] == ("max-age=31536000; includeSubDomains")
