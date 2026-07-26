from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import TracebackType
from uuid import UUID, uuid4

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
)


class InMemoryRegistrationRepository(IRegistrationRepository):
    """Development adapter; production persistence can replace this port unchanged."""

    def __init__(self) -> None:
        self.churches: list[Church] = []
        self.users: list[User] = []
        self.congregations: list[Congregation] = []
        self.memberships: list[ChurchMembership] = []
        self.settings: list[ChurchSettings] = []

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


class UuidGenerator:
    def generate(self) -> UUID:
        return uuid4()


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
