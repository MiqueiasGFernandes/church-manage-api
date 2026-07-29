from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
    SecurityAuditEvent,
)
from modules.organizations.domain.use_cases.logout_all_sessions import ILogoutAllSessions


class LogoutAllSessions(ILogoutAllSessions):
    def __init__(
        self, repository: IAuthRepository, unit_of_work: IUnitOfWork, clock: IClock
    ) -> None:
        self._repository, self._unit_of_work, self._clock = repository, unit_of_work, clock

    async def execute(self, actor: AuthenticatedUser) -> None:
        now = self._clock.now()
        async with self._unit_of_work:
            for session in await self._repository.sessions_for_user(actor.user_id):
                if session.revoked_at is None:
                    await self._repository.revoke_session(session.id, now)
            await self._repository.add_audit_event(
                SecurityAuditEvent("ALL_SESSIONS_REVOKED", now, actor_user_id=actor.user_id)
            )
            await self._unit_of_work.commit()
