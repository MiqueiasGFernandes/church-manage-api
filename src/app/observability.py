import json
import logging
import sys
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from typing import Final

LOGGER_NAME: Final = "church_manage"
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_STANDARD_LOG_RECORD_FIELDS: Final = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
)


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        request_id = _request_id.get()
        if request_id is not None:
            payload["request_id"] = request_id
        payload.update(
            (key, value)
            for key, value in record.__dict__.items()
            if key not in _STANDARD_LOG_RECORD_FIELDS and not key.startswith("_")
        )
        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(_parse_log_level(level))
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logger.handlers.clear()
    logger.addHandler(handler)
    logging.getLogger("uvicorn.access").disabled = True
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def bind_request_id(request_id: str) -> Token[str | None]:
    return _request_id.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id.reset(token)


def _parse_log_level(level: str) -> int:
    normalized = level.strip().upper()
    supported_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    parsed = supported_levels.get(normalized)
    if parsed is None:
        supported = "DEBUG, INFO, WARNING, ERROR, CRITICAL"
        raise ValueError(f"LOG_LEVEL inválido. Valores aceitos: {supported}.")
    return parsed
