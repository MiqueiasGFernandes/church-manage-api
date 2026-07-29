from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import TracebackType
from uuid import UUID, uuid4

from modules.organizations.application.repositories.auth_repository import (
    EmailVerificationRecord,
    PasswordResetRecord,
    SecurityAuditEvent,
    SessionRecord,
)
from modules.organizations.application.repositories.registration_repository import (
    IRegistrationRepository,
)
from modules.organizations.domain.model import (
    CNPJ,
    Church,
    ChurchMembership,
    ChurchSettings,
    ChurchSlug,
    Congregation,
    EmailAddress,
    User,
    UserId,
)


class InMemoryRegistrationRepository(IRegistrationRepository):
    """Development adapter; production persistence can replace this port unchanged."""

    def __init__(self) -> None:
        self.churches: list[Church] = []
        self.users: list[User] = []
        self.congregations: list[Congregation] = []
        self.memberships: list[ChurchMembership] = []
        self.settings: list[ChurchSettings] = []
        self.email_verifications: list[EmailVerificationRecord] = []
        self.sessions: list[SessionRecord] = []
        self.consumed_refresh_tokens: dict[str, UUID] = {}
        self.audit_events: list[SecurityAuditEvent] = []
        self.password_resets: list[PasswordResetRecord] = []

    async def user_exists_by_email(self, email: EmailAddress) -> bool:
        return any(user.email == email for user in self.users)

    async def church_exists_by_slug(self, slug: ChurchSlug) -> bool:
        return any(church.slug == slug for church in self.churches)

    async def church_exists_by_document(self, document: CNPJ) -> bool:
        return any(church.document == document for church in self.churches)

    async def add_church(self, church: Church) -> None:
        self.churches.append(church)

    async def add_user(self, user: User) -> None:
        self.users.append(user)

    async def add_congregation(self, congregation: Congregation) -> None:
        self.congregations.append(congregation)

    async def add_membership(self, membership: ChurchMembership) -> None:
        self.memberships.append(membership)

    async def add_settings(self, settings: ChurchSettings) -> None:
        self.settings.append(settings)

    async def find_user_by_email(self, email: EmailAddress) -> User | None:
        return next((user for user in self.users if user.email == email), None)

    async def find_user_by_id(self, user_id: UUID) -> User | None:
        return next((user for user in self.users if user.id.value == user_id), None)

    async def save_user(self, user: User) -> None:
        self.users = [user if item.id == user.id else item for item in self.users]

    async def memberships_for_user(self, user_id: UUID) -> tuple[ChurchMembership, ...]:
        return tuple(item for item in self.memberships if item.user_id == UserId(user_id))

    async def save_membership(self, membership: ChurchMembership) -> None:
        self.memberships = [
            membership if item.id == membership.id else item for item in self.memberships
        ]

    async def add_email_verification(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self.email_verifications.append(EmailVerificationRecord(user_id, token_hash, expires_at))

    async def find_email_verification(self, token_hash: str) -> EmailVerificationRecord | None:
        return next(
            (item for item in self.email_verifications if item.token_hash == token_hash), None
        )

    async def use_email_verification(self, token_hash: str, used_at: datetime) -> None:
        record = await self.find_email_verification(token_hash)
        assert record is not None
        record.used_at = used_at

    async def add_session(
        self,
        session_id: UUID,
        user_id: UUID,
        refresh_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> None:
        self.sessions.append(
            SessionRecord(session_id, user_id, refresh_hash, created_at, expires_at)
        )

    async def find_session_by_refresh(self, refresh_hash: str) -> SessionRecord | None:
        return next(
            (item for item in self.sessions if item.refresh_token_hash == refresh_hash), None
        )

    async def find_session_by_id(self, session_id: UUID) -> SessionRecord | None:
        return next((item for item in self.sessions if item.id == session_id), None)

    async def rotate_session(
        self, session_id: UUID, refresh_hash: str, expires_at: datetime
    ) -> None:
        record = await self.find_session_by_id(session_id)
        assert record is not None
        record.refresh_token_hash, record.expires_at = refresh_hash, expires_at

    async def revoke_session(self, session_id: UUID, revoked_at: datetime) -> None:
        record = await self.find_session_by_id(session_id)
        assert record is not None
        record.revoked_at = revoked_at

    async def add_consumed_refresh_token(
        self, session_id: UUID, token_hash: str, consumed_at: datetime
    ) -> None:
        del consumed_at
        self.consumed_refresh_tokens[token_hash] = session_id

    async def find_session_id_by_consumed_refresh(self, token_hash: str) -> UUID | None:
        return self.consumed_refresh_tokens.get(token_hash)

    async def add_audit_event(self, event: SecurityAuditEvent) -> None:
        self.audit_events.append(event)

    async def sessions_for_user(self, user_id: UUID) -> tuple[SessionRecord, ...]:
        return tuple(item for item in self.sessions if item.user_id == user_id)

    async def invalidate_email_verifications(self, user_id: UUID, invalidated_at: datetime) -> None:
        for record in self.email_verifications:
            if record.user_id == user_id and record.used_at is None:
                record.used_at = invalidated_at

    async def add_password_reset(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self.password_resets.append(PasswordResetRecord(user_id, token_hash, expires_at))

    async def invalidate_password_resets(self, user_id: UUID, invalidated_at: datetime) -> None:
        for record in self.password_resets:
            if record.user_id == user_id and record.used_at is None:
                record.used_at = invalidated_at

    async def find_password_reset(self, token_hash: str) -> PasswordResetRecord | None:
        return next((item for item in self.password_resets if item.token_hash == token_hash), None)

    async def use_password_reset(self, token_hash: str, used_at: datetime) -> None:
        record = await self.find_password_reset(token_hash)
        assert record is not None
        record.used_at = used_at


class InMemoryUnitOfWork:
    def __init__(self, repository: InMemoryRegistrationRepository) -> None:
        self._repository = repository
        self._snapshot: InMemoryRegistrationRepository | None = None
        self.committed = False

    async def __aenter__(self) -> InMemoryUnitOfWork:
        self._snapshot = deepcopy(self._repository)
        self.committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            assert self._snapshot is not None
            self._repository.__dict__.update(deepcopy(self._snapshot.__dict__))

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        if self._snapshot is not None:
            self._repository.__dict__.update(deepcopy(self._snapshot.__dict__))
        self.committed = False


class Argon2Hasher:
    def __init__(self) -> None:
        from argon2 import PasswordHasher as Argon2PasswordHasher

        self._hasher = Argon2PasswordHasher()

    def hash(self, plain_text: str) -> str:
        return self._hasher.hash(plain_text)

    def verify(self, plain_text: str, password_hash: str) -> bool:
        from argon2.exceptions import VerificationError

        try:
            return bool(self._hasher.verify(password_hash, plain_text))
        except VerificationError:
            return False


class UuidGenerator:
    def generate(self) -> UUID:
        return uuid4()


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
