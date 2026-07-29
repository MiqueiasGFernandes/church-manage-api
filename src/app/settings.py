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
