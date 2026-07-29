from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class IPasswordVerifier(Protocol):
    def verify(self, plain_text: str, password_hash: str) -> bool: ...


class ITokenService(Protocol):
    def generate_opaque(self) -> str: ...
    def hash_opaque(self, token: str) -> str: ...
    def issue_access(self, user_id: UUID, session_id: UUID, now: datetime) -> tuple[str, int]: ...
    def decode_access(self, token: str, now: datetime) -> tuple[UUID, UUID]: ...


class IEmailSender(Protocol):
    async def send_email_verification(self, email: str, token: str) -> None: ...
    async def send_password_reset(self, email: str, token: str) -> None: ...


class RateLimitAction(StrEnum):
    VERIFY_EMAIL = "verify_email"
    RESEND_EMAIL_VERIFICATION = "resend_email_verification"
    FORGOT_PASSWORD = "forgot_password"
    RESET_PASSWORD = "reset_password"
    LOGIN = "login"
    REFRESH = "refresh"
    CHANGE_PASSWORD = "change_password"


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    limit: int
    window_seconds: int

    def __post_init__(self) -> None:
        if self.limit <= 0 or self.window_seconds <= 0:
            raise ValueError("Limite e intervalo do rate limiter devem ser maiores que zero.")


type RateLimitPolicies = Mapping[RateLimitAction, RateLimitPolicy]


class IRateLimiter(Protocol):
    async def ensure_allowed(self, action: RateLimitAction, key: str) -> None: ...
