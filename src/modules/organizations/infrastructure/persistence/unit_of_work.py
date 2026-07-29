from __future__ import annotations

import logging
from types import TracebackType
from typing import Never

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from modules.organizations.application.errors.register_church import (
    ChurchDocumentAlreadyExistsError,
    ChurchSlugAlreadyExistsError,
    UserEmailAlreadyExistsError,
)
from modules.organizations.application.ports.registration_services import IUnitOfWork

logger = logging.getLogger(f"church_manage.{__name__}")


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._committed = False

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self._committed:
            await self._session.rollback()
        await self._session.close()

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            self._raise_registration_conflict(exc)
        self._committed = True

    async def rollback(self) -> None:
        await self._session.rollback()
        self._committed = False

    @staticmethod
    def _raise_registration_conflict(exc: IntegrityError) -> Never:
        database_error = str(exc.orig)
        if "uq_users_email" in database_error:
            SqlAlchemyUnitOfWork._log_conflict("user_email")
            raise UserEmailAlreadyExistsError(
                "Já existe uma conta cadastrada com este e-mail."
            ) from exc
        if "uq_churches_slug" in database_error:
            SqlAlchemyUnitOfWork._log_conflict("church_slug")
            raise ChurchSlugAlreadyExistsError(
                "O endereço público escolhido já está em uso."
            ) from exc
        if "uq_churches_document" in database_error:
            SqlAlchemyUnitOfWork._log_conflict("church_document")
            raise ChurchDocumentAlreadyExistsError(
                "Já existe uma igreja cadastrada com este CNPJ."
            ) from exc
        raise exc

    @staticmethod
    def _log_conflict(resource: str) -> None:
        logger.warning(
            "registration_persistence_conflict_detected",
            extra={
                "operation": "commit_registration",
                "conflicting_resource": resource,
                "action": "Return the conflict response and ask the client to use unique data.",
            },
        )
