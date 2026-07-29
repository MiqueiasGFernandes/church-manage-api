from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from modules.organizations.domain.model import ChurchMembership, EmailAddress, User


@dataclass(slots=True)
class EmailVerificationRecord:
    user_id: UUID
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None


@dataclass(slots=True)
class SessionRecord:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class SecurityAuditEvent:
    event_type: str
    occurred_at: datetime
    actor_user_id: UUID | None = None
    target_user_id: UUID | None = None
    church_id: UUID | None = None
    session_id: UUID | None = None


@dataclass(slots=True)
class PasswordResetRecord:
    user_id: UUID
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None


class IAuthRepository(Protocol):
    async def find_user_by_email(self, email: EmailAddress) -> User | None: ...
    async def find_user_by_id(self, user_id: UUID) -> User | None: ...
    async def save_user(self, user: User) -> None: ...
    async def memberships_for_user(self, user_id: UUID) -> tuple[ChurchMembership, ...]: ...
    async def save_membership(self, membership: ChurchMembership) -> None: ...
    async def add_email_verification(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None: ...
    async def find_email_verification(self, token_hash: str) -> EmailVerificationRecord | None: ...
    async def use_email_verification(self, token_hash: str, used_at: datetime) -> None: ...
    async def add_session(
        self,
        session_id: UUID,
        user_id: UUID,
        refresh_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> None: ...
    async def find_session_by_refresh(self, refresh_hash: str) -> SessionRecord | None: ...
    async def find_session_by_id(self, session_id: UUID) -> SessionRecord | None: ...
    async def rotate_session(
        self, session_id: UUID, refresh_hash: str, expires_at: datetime
    ) -> None: ...
    async def revoke_session(self, session_id: UUID, revoked_at: datetime) -> None: ...
    async def add_consumed_refresh_token(
        self, session_id: UUID, token_hash: str, consumed_at: datetime
    ) -> None: ...
    async def find_session_id_by_consumed_refresh(self, token_hash: str) -> UUID | None: ...
    async def add_audit_event(self, event: SecurityAuditEvent) -> None: ...
    async def sessions_for_user(self, user_id: UUID) -> tuple[SessionRecord, ...]: ...
    async def invalidate_email_verifications(
        self, user_id: UUID, invalidated_at: datetime
    ) -> None: ...
    async def add_password_reset(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None: ...
    async def find_password_reset(self, token_hash: str) -> PasswordResetRecord | None: ...
    async def use_password_reset(self, token_hash: str, used_at: datetime) -> None: ...
