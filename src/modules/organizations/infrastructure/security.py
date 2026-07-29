import base64
import hashlib
import hmac
import json
import secrets
import smtplib
from asyncio import to_thread
from datetime import datetime, timedelta
from email.message import EmailMessage
from uuid import UUID, uuid4

from modules.organizations.application.errors.auth import RateLimitExceededError
from modules.organizations.application.ports.registration_services import IClock


class HmacTokenService:
    def __init__(self, secret: str, access_token_minutes: int = 15) -> None:
        if len(secret) < 32:
            raise ValueError("AUTH_TOKEN_SECRET deve possuir pelo menos 32 caracteres.")
        self._secret = secret.encode()
        self._access_token_minutes = access_token_minutes

    def generate_opaque(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_opaque(self, token: str) -> str:
        return hmac.new(self._secret, token.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def _encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    @staticmethod
    def _decode(data: str) -> bytes:
        return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))

    def issue_access(self, user_id: UUID, session_id: UUID, now: datetime) -> tuple[str, int]:
        expires_in = self._access_token_minutes * 60
        header = self._encode(b'{"alg":"HS256","typ":"JWT"}')
        payload = self._encode(
            json.dumps(
                {
                    "sub": str(user_id),
                    "sid": str(session_id),
                    "iat": int(now.timestamp()),
                    "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
                    "jti": str(uuid4()),
                    "iss": "church-manage",
                    "aud": "church-manage-api",
                },
                separators=(",", ":"),
            ).encode()
        )
        signature = self._encode(
            hmac.new(self._secret, f"{header}.{payload}".encode(), hashlib.sha256).digest()
        )
        return f"{header}.{payload}.{signature}", expires_in

    def decode_access(self, token: str, now: datetime) -> tuple[UUID, UUID]:
        try:
            header, payload, signature = token.split(".")
            if header != self._encode(b'{"alg":"HS256","typ":"JWT"}'):
                raise ValueError("invalid header")
            expected = self._encode(
                hmac.new(self._secret, f"{header}.{payload}".encode(), hashlib.sha256).digest()
            )
            if not hmac.compare_digest(signature, expected):
                raise ValueError("invalid signature")
            claims = json.loads(self._decode(payload))
            if (
                claims["iss"] != "church-manage"
                or claims["aud"] != "church-manage-api"
                or int(claims["exp"]) <= int(now.timestamp())
            ):
                raise ValueError("invalid claims")
            return UUID(claims["sub"]), UUID(claims["sid"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid access token") from exc


class InMemoryEmailSender:
    def __init__(self) -> None:
        self.verifications: list[tuple[str, str]] = []
        self.password_resets: list[tuple[str, str]] = []

    async def send_email_verification(self, email: str, token: str) -> None:
        self.verifications.append((email, token))

    async def send_password_reset(self, email: str, token: str) -> None:
        self.password_resets.append((email, token))


class FixedWindowRateLimiter:
    def __init__(self, clock: IClock) -> None:
        self._clock = clock
        self._attempts: dict[str, list[datetime]] = {}

    async def ensure_allowed(self, key: str, limit: int, window_seconds: int) -> None:
        cutoff = self._clock.now() - timedelta(seconds=window_seconds)
        attempts = [instant for instant in self._attempts.get(key, []) if instant > cutoff]
        if len(attempts) >= limit:
            raise RateLimitExceededError(
                "Limite de tentativas excedido. Tente novamente mais tarde."
            )
        attempts.append(self._clock.now())
        self._attempts[key] = attempts


class SmtpEmailSender:
    def __init__(
        self,
        host: str,
        port: int,
        sender: str,
        public_url: str,
        username: str = "",
        password: str = "",
        use_tls: bool = True,
    ) -> None:
        if not host or not sender or not public_url:
            raise ValueError("SMTP_HOST, SMTP_SENDER e PUBLIC_APP_URL são obrigatórios.")
        self._host, self._port, self._sender = host, port, sender
        self._public_url, self._username, self._password = (
            public_url.rstrip("/"),
            username,
            password,
        )
        self._use_tls = use_tls

    async def send_email_verification(self, email: str, token: str) -> None:
        message = EmailMessage()
        message["Subject"] = "Confirme seu e-mail"
        message["From"], message["To"] = self._sender, email
        message.set_content(
            f"Confirme seu e-mail acessando: {self._public_url}/verify-email?token={token}"
        )
        await to_thread(self._send, message)

    async def send_password_reset(self, email: str, token: str) -> None:
        message = EmailMessage()
        message["Subject"] = "Redefina sua senha"
        message["From"], message["To"] = self._sender, email
        message.set_content(
            f"Redefina sua senha acessando: {self._public_url}/reset-password?token={token}"
        )
        await to_thread(self._send, message)

    def _send(self, message: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=10) as client:
            if self._use_tls:
                client.starttls()
            if self._username:
                client.login(self._username, self._password)
            client.send_message(message)
