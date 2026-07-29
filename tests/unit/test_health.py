import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_reports_application_is_running() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 204
    assert response.content == b""


def test_rejects_untrusted_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOWED_HOSTS", "api.example.com")

    with TestClient(create_app(), base_url="http://api.example.com") as client:
        response = client.get("/health", headers={"host": "evil.example.com"})

    assert response.status_code == 400
    assert response.headers["x-content-type-options"] == "nosniff"


def test_adds_security_headers_in_development() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-frame-options"] == "DENY"
    assert "strict-transport-security" not in response.headers
