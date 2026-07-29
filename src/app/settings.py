import base64
import binascii
import re
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlsplit


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


@dataclass(frozen=True, slots=True)
class CorsSettings:
    allowed_origins: tuple[str, ...]
    allowed_methods: tuple[str, ...]
    allowed_headers: tuple[str, ...]
    allow_credentials: bool

    @classmethod
    def from_strings(
        cls, origins: str, methods: str, headers: str, allow_credentials: bool
    ) -> "CorsSettings":
        settings = cls(
            allowed_origins=_split_csv(origins, "CORS_ALLOWED_ORIGINS"),
            allowed_methods=tuple(
                method.upper() for method in _split_csv(methods, "CORS_ALLOWED_METHODS")
            ),
            allowed_headers=_split_csv(headers, "CORS_ALLOWED_HEADERS"),
            allow_credentials=allow_credentials,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        for origin in self.allowed_origins:
            if origin == "*":
                continue
            parsed = urlsplit(origin)
            canonical = f"{parsed.scheme}://{parsed.netloc}"
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or origin != canonical:
                raise ValueError(
                    "CORS_ALLOWED_ORIGINS deve conter apenas origens HTTP(S) sem caminho."
                )
        if "*" in self.allowed_origins and self.allow_credentials:
            raise ValueError(
                "CORS_ALLOWED_ORIGINS não pode usar wildcard com credenciais habilitadas."
            )


@dataclass(frozen=True, slots=True)
class ProductionSecuritySettings:
    persistence_backend: str
    database_url: str
    auth_token_secret: str | None
    auth_cookie_secure: bool
    email_backend: str
    smtp_host: str
    smtp_sender: str
    smtp_use_tls: bool
    public_app_url: str
    cors_allowed_origins: tuple[str, ...]
    cors_allow_credentials: bool

    def validate(self) -> None:
        if self.persistence_backend != "postgresql":
            raise ValueError("PERSISTENCE_BACKEND deve ser postgresql em produção.")
        if not self.database_url.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL deve usar o formato postgresql+asyncpg:// em produção.")
        self._validate_token_secret()
        if not self.auth_cookie_secure:
            raise ValueError("AUTH_COOKIE_SECURE deve ser true em produção.")
        if self.email_backend != "smtp":
            raise ValueError("EMAIL_BACKEND deve ser smtp em produção.")
        if not self.smtp_host.strip():
            raise ValueError("SMTP_HOST é obrigatório em produção.")
        if not self.smtp_sender.strip():
            raise ValueError("SMTP_SENDER é obrigatório em produção.")
        if not self.smtp_use_tls:
            raise ValueError("SMTP_USE_TLS deve ser true em produção.")
        public_url = urlsplit(self.public_app_url)
        if public_url.scheme != "https" or not public_url.netloc:
            raise ValueError("PUBLIC_APP_URL deve ser uma URL HTTPS válida em produção.")
        public_origin = f"{public_url.scheme}://{public_url.netloc}"
        if not self.cors_allow_credentials:
            raise ValueError("CORS_ALLOW_CREDENTIALS deve ser true em produção.")
        if public_origin not in self.cors_allowed_origins or any(
            not origin.startswith("https://") for origin in self.cors_allowed_origins
        ):
            raise ValueError(
                "CORS_ALLOWED_ORIGINS deve incluir a origem HTTPS de PUBLIC_APP_URL em produção."
            )

    def _validate_token_secret(self) -> None:
        secret = self.auth_token_secret
        if secret is None or not re.fullmatch(r"[A-Za-z0-9_-]{43,}", secret):
            raise ValueError(
                "AUTH_TOKEN_SECRET deve ser Base64 URL-safe e representar ao menos 32 bytes."
            )
        try:
            decoded = base64.urlsafe_b64decode(secret + "=" * (-len(secret) % 4))
        except (binascii.Error, ValueError) as exc:
            raise ValueError("AUTH_TOKEN_SECRET possui formato Base64 URL-safe inválido.") from exc
        if len(decoded) < 32 or len(set(secret)) < 16:
            raise ValueError("AUTH_TOKEN_SECRET não possui entropia suficiente para produção.")


def parse_environment(value: str) -> AppEnvironment:
    try:
        return AppEnvironment(value.strip().lower())
    except ValueError as exc:
        supported = ", ".join(item.value for item in AppEnvironment)
        raise ValueError(f"APP_ENV inválido. Valores aceitos: {supported}.") from exc


def parse_boolean(value: str, variable_name: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"{variable_name} deve ser true ou false.")
    return normalized == "true"


def _split_csv(value: str, variable_name: str) -> tuple[str, ...]:
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    if not items:
        raise ValueError(f"{variable_name} deve possuir ao menos um valor.")
    return items
