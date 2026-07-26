from __future__ import annotations

from datetime import datetime
from types import TracebackType
from typing import Protocol
from uuid import UUID

from modules.organizations.domain.model import ChurchRegistered


class IUnitOfWork(Protocol):
    async def __aenter__(self) -> IUnitOfWork: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class IPasswordHasher(Protocol):
    def hash(self, plain_text: str) -> str: ...


class IIdGenerator(Protocol):
    def generate(self) -> UUID: ...


class IClock(Protocol):
    def now(self) -> datetime: ...


class IEventPublisher(Protocol):
    async def publish(self, event: ChurchRegistered) -> None: ...
