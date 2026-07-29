from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_reports_application_is_running() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 204
    assert response.content == b""
