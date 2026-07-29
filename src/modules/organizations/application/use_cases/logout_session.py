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
from modules.organizations.domain.use_cases.logout_session import ILogoutSession


class LogoutSession(ILogoutSession):
    def __init__(
        self, repository: IAuthRepository, unit_of_work: IUnitOfWork, clock: IClock
    ) -> None:
        self._repository, self._unit_of_work, self._clock = repository, unit_of_work, clock

    async def execute(self, actor: AuthenticatedUser) -> None:
        async with self._unit_of_work:
            await self._repository.revoke_session(actor.session_id, self._clock.now())
            await self._repository.add_audit_event(
                SecurityAuditEvent(
                    "SESSION_REVOKED",
                    self._clock.now(),
                    actor_user_id=actor.user_id,
                    session_id=actor.session_id,
                )
            )
            await self._unit_of_work.commit()
