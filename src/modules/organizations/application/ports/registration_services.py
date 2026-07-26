from __future__ import annotations

from datetime import datetime
from types import TracebackType
from typing import Protocol
from uuid import UUID

from modules.organizations.domain.model import ChurchRegistered


class UnitOfWork(Protocol):
    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, plain_text: str) -> str: ...


class IdGenerator(Protocol):
    def generate(self) -> UUID: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class EventPublisher(Protocol):
    async def publish(self, event: ChurchRegistered) -> None: ...
