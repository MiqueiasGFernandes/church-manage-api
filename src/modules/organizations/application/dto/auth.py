from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    user_id: UUID
    session_id: UUID


@dataclass(frozen=True, slots=True)
class ChurchAccess:
    church_id: UUID
    role: str
    permissions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CurrentUserOutput:
    user_id: UUID
    name: str
    email: str
    churches: tuple[ChurchAccess, ...]


@dataclass(frozen=True, slots=True)
class UserSessionOutput:
    session_id: UUID
    created_at: datetime
    expires_at: datetime
    current: bool
