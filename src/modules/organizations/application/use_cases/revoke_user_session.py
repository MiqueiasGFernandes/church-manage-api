from uuid import UUID

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)
from modules.organizations.application.errors.auth import (
    SessionNotFoundError,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
    SecurityAuditEvent,
)
from modules.organizations.domain.use_cases.revoke_user_session import IRevokeUserSession


class RevokeUserSession(IRevokeUserSession):
    def __init__(
        self, repository: IAuthRepository, unit_of_work: IUnitOfWork, clock: IClock
    ) -> None:
        self._repository, self._unit_of_work, self._clock = repository, unit_of_work, clock

    async def execute(self, actor: AuthenticatedUser, session_id: UUID) -> None:
        now = self._clock.now()
        missing = False
        async with self._unit_of_work:
            owned = next(
                (
                    item
                    for item in await self._repository.sessions_for_user(actor.user_id)
                    if item.id == session_id
                ),
                None,
            )
            if owned is None:
                missing = True
            else:
                if owned.revoked_at is None:
                    await self._repository.revoke_session(session_id, now)
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "SESSION_REVOKED", now, actor_user_id=actor.user_id, session_id=session_id
                    )
                )
                await self._unit_of_work.commit()
        if missing:
            raise SessionNotFoundError("Sessão não encontrada.")
