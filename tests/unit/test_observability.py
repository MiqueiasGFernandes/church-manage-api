import json
import logging

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.observability import (
    JsonLogFormatter,
    bind_request_id,
    configure_logging,
    get_logger,
    reset_request_id,
)


class RecordCollector(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_json_formatter_includes_structured_context_and_action() -> None:
    record = logging.LogRecord(
        name="church_manage.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="operation_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "request-123"
    record.operation = "test_operation"
    record.action = "No action required."

    payload = json.loads(JsonLogFormatter().format(record))

    assert payload["message"] == "operation_completed"
    assert payload["request_id"] == "request-123"
    assert payload["operation"] == "test_operation"
    assert payload["action"] == "No action required."
    assert payload["timestamp"].endswith("+00:00")


def test_logging_configuration_rejects_an_unknown_level() -> None:
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        configure_logging("verbose")


def test_logging_configuration_disables_redundant_uvicorn_access_log() -> None:
    configure_logging("INFO")

    assert logging.getLogger("uvicorn.access").disabled is True


def test_request_id_is_inherited_by_internal_logs() -> None:
    logger = get_logger("internal-test")
    collector = RecordCollector()
    logger.addHandler(collector)
    token = bind_request_id("request-internal-123")
    try:
        logger.info(
            "internal_operation_completed",
            extra={"operation": "internal_test", "action": "No action required."},
        )
        serialized_record = JsonLogFormatter().format(collector.records[0])
    finally:
        reset_request_id(token)
        logger.removeHandler(collector)

    assert '"request_id": "request-internal-123"' in serialized_record


def test_request_logging_is_correlated_actionable_and_not_redundant() -> None:
    application = create_app()
    logger = get_logger("app.main")
    collector = RecordCollector()
    logger.addHandler(collector)
    try:
        with TestClient(application) as client:
            response = client.get("/openapi.json", headers={"X-Request-ID": "request-123"})
    finally:
        logger.removeHandler(collector)

    request_records = [
        record for record in collector.records if record.getMessage() == "http_request_completed"
    ]
    assert len(request_records) == 1
    serialized_record = JsonLogFormatter().format(request_records[0])
    assert '"request_id": "request-123"' in serialized_record
    assert '"operation": "http_request"' in serialized_record
    assert '"action": "No action required."' in serialized_record
    assert response.headers["X-Request-ID"] == "request-123"


def test_health_check_does_not_generate_request_log() -> None:
    application = create_app()
    logger = get_logger("app.main")
    collector = RecordCollector()
    logger.addHandler(collector)
    try:
        with TestClient(application) as client:
            response = client.get("/health")
    finally:
        logger.removeHandler(collector)

    assert response.status_code == 204
    assert not any(record.getMessage() == "http_request_completed" for record in collector.records)


def test_handled_error_is_logged_once_with_stable_error_code() -> None:
    application = create_app()
    logger = get_logger("app.main")
    collector = RecordCollector()
    logger.addHandler(collector)
    try:
        with TestClient(application) as client:
            response = client.get("/api/v1/auth/me")
    finally:
        logger.removeHandler(collector)

    request_records = [
        record for record in collector.records if record.getMessage() == "http_request_completed"
    ]
    assert response.status_code == 401
    assert len(request_records) == 1
    serialized_record = JsonLogFormatter().format(request_records[0])
    assert '"error_code": "AUTH_ACCESS_TOKEN_INVALID"' in serialized_record
    assert "Token de acesso ausente" not in serialized_record
